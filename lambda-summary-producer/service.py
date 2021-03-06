# -*- coding: utf-8 -*-

import json
import os
import time
from configparser import ConfigParser

import boto3
import requests
import sentry_sdk
from sentry_sdk import capture_message, capture_exception


def handler(event, context):
    # TODO implement

    bucket = os.environ['ip_bucket']
    s3 = boto3.resource('s3')
    client = boto3.client('lambda')

    # Download Config File
    s3.Bucket(bucket).download_file('config/config.ini', '/tmp/config.ini')
    print('Config File Downloaded')

    # Initialize Config Parser
    config = ConfigParser()
    config.read('/tmp/config.ini')
    print('Config File Parsed')

    # Initiate Sentry SDK
    sentry_sdk.init(config.get('sentry', 'init_params'))
    webhook_url = config.get('slack', 'webhook_url')

    i = 0

    for obj in s3.Bucket(bucket).objects.filter(Prefix=config.get('aws', 'stage2')):
        tmp_file = obj.key
        
        if tmp_file.endswith('.json'):
            i = i + 1
            msg = {"tmp_file": tmp_file}

            

            try:
                invoke_response = client.invoke(FunctionName="SummaryConsumer",
                                                InvocationType='Event',
                                                Payload=json.dumps(msg))
                print(invoke_response)


                invoke_response2 = client.invoke(FunctionName="SummaryConsumer-2",
                                                 InvocationType='Event',
                                                 Payload=json.dumps(msg))
                print(invoke_response2)


            except Exception as e:
                capture_exception(e)
                capture_message('Could not Invoke Lambda for URL - ' + u)

            print('File Sent to Consumer Lambda for Analysis')

    message = '*Summary Producer* | ' + str(i*2) + ' Lambda Summarization Consumer(s) Invoked'

    slack_data = {
        "attachments": [
            {
                "text": message,
                "color": "#36a64f",
                "footer": "Summary Producer"
            }
        ]
    }

    requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Pushed all Files')
    }
