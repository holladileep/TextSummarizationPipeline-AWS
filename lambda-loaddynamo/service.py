from __future__ import print_function  # Python 2/3 compatibility

import decimal
import json
import os
from configparser import ConfigParser

import boto3
import requests
import sentry_sdk


def handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('articles')

    bucket = os.environ['ip_bucket']
    s3 = boto3.resource('s3')

    # Download Config File
    s3.Bucket(bucket).download_file('config/config.ini', '/tmp/config.ini')
    print('Config File Downloaded')

    # Initialize Config Parser
    config = ConfigParser()
    config.read('/tmp/config.ini')
    print('Config File Parsed')

    sentry_sdk.init(config.get('sentry', 'init_params'))
    webhook_url = config.get('slack', 'webhook_url')

    s3_files = []

    for obj in s3.Bucket(bucket).objects.filter(Prefix=config.get('aws', 'stage2')):
        tmp_file = obj.key
        if tmp_file.endswith('.json'):
            s3_files.append('/tmp/' + os.path.basename(tmp_file))
            s3.Bucket(bucket).download_file(tmp_file, '/tmp/' + os.path.basename(tmp_file))

    for file in s3_files:
        with open(file) as json_file:
            articles = json.load(json_file, parse_float=decimal.Decimal)
            for a in articles:
                url = a['url']
                if a['publish_date'] == "":
                    a['publish_date'] = 'True'
                publish_date = a['publish_date']
                authors = a['authors']
                if a['summary'] == "":
                    a['summary'] = 'N/A'
                summary = a['summary']
                if a['text'] == "":
                    a['text'] = 'N/A'
                text = a['text']

                print("Adding article:", url)
                text = text.strip('\n')
                text = text.strip('\t')
                

                table.update_item(
                    Key={
                        'url': url,
                    },
                    UpdateExpression="set article_text = :c",
                    ExpressionAttributeValues={
                        ':c': text
                    },
                )

    print('Articles loaded into DynamoDB successfully.')

    message = '*Load DynamoDB* | Article text loaded'
    slack_data = {
        "attachments": [
            {
                "text": message,
                "color": "#42f5b9",
                "footer": "Lambda - LoadDynamoDB"
            }
        ]
    }

    requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Load to DynamoCompleted')
    }
