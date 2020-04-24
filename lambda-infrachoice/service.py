import json
import os
from configparser import ConfigParser

import boto3
import pandas as pd
import requests
import sentry_sdk
from sentry_sdk import capture_message


def handler(event, context):
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

    # Download CSV with list of Valid URLs
    s3.Bucket(bucket).download_file(config.get('aws', 'link_op') + 'valid_url.csv', '/tmp/valid_url.csv')
    s3.Bucket(bucket).download_file(config.get('aws', 'link_op') + 'invalid_url.csv', '/tmp/invalid_url.csv')
    df2 = pd.read_csv('/tmp/valid_url.csv')
    df3 = pd.read_csv('/tmp/invalid_url.csv')

    count_row = df2.shape[0]
    count_invalid = df3.shape[0]

    message = '*InfraChoice* | ' + str(count_row) + ' Valid URL(s) Found ; ' + str(
        count_invalid) + ' URL(s) may have been moved or are using AdBlock'

    slack_data = {
        "attachments": [
            {
                "text": message,
                "color": "#ffe019",
                "footer": "InfraChoice"
            }
        ]
    }

    requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )

    if (count_row == 0):
        capture_message('Lambda Process to be Followed ; Less than 60 links to Scrape')
        return {
            'statusCode': 400,
            'body': json.dumps('No Valid Links')
        }

    elif (count_row == 1):
        capture_message('Lambda Process to be Followed ; One link to Scrape')
        return {
            'statusCode': 150,
            'body': json.dumps('One Link - Invoking Normal flow')
        }

    elif (count_row <= 100):
        capture_message('100 Links')
        return {
            'statusCode': 200,
            'body': json.dumps('Lambda Process to be Followed ; Less than 100 links to Scrape')
        }
    else:
        capture_message('Batch Process to be Followed ; Less than 60 links to Scrape')
        return {
            'statusCode': 300,
            'body': json.dumps('More than 100 Links - Invoking Batch Process')
        }
