# -*- coding: utf-8 -*-

import json
import os
from configparser import ConfigParser

import boto3
import requests
import sentry_sdk


def handler(event, context):
    # TODO implement

    bucket = os.environ['ip_bucket']
    s3 = boto3.resource('s3')

    # Download Config File
    s3.Bucket(bucket).download_file('config/config.ini', '/tmp/config.ini')
    print('Config File Downloaded')

    # Initialize Config Parser
    config = ConfigParser()
    config.read('/tmp/config.ini')
    print('Config File Parsed')

    # Initiate Sentry SDK
    sentry_sdk.init(config.get('sentry', 'init_params'))

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('summary')

    # Download JSON with scraped data
    tmp_file = event.get('tmp_file')
    s3.Bucket(bucket).download_file(tmp_file, '/tmp/temp.json')
    headers = {
        'Content-type': 'text/plain',
    }

    with open("/tmp/temp.json") as json_file:
        articles = json.load(json_file, parse_float=decimal.Decimal)

        for a in articles:
            if a['text'] != '':  # Check if 'text is not an empty string
                text = a['text']
            else:  # If 'text is empty, continue with next record
                continue

            url = a['url']

    text = text.strip('\n')
    text = text.strip('\t')
    text_enc = text.encode()

    response2 = requests.post(config.get('flask', 'app2'), headers=headers, data=text_enc)
    data2 = response2.json()

    # print (data)
    print(data2)

    table.update_item(
        Key={
            'url': url,
        },
        UpdateExpression="set summary_a = :t",
        ExpressionAttributeValues={

            ':t': data2['summary']

        },
    )

    print(url)
    # print (text.replace('\n', '').replace('\r', ''))
    return {
        'statusCode': 200,
        'body': json.dumps('Summary Complete with Bert')
    }
