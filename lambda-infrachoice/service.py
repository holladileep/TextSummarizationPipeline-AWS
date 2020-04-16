import json
import os
from configparser import ConfigParser

import boto3
import pandas as pd
import sentry_sdk

sentry_sdk.init("https://848ed5b8adbd4155b9c2dab067f8727b@o377913.ingest.sentry.io/5200643")


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

    # Download CSV with list of Valid URLs
    s3.Bucket(bucket).download_file(config.get('aws', 'link_op') + 'valid_url.csv', '/tmp/valid_url.csv')
    df2 = pd.read_csv('/tmp/valid_url.csv')

    count_row = df2.shape[0]

    if (count_row <= 10):
        return {
            'statusCode': 200,
            'body': json.dumps('Less than 10 links to Scrape - Lambda to be Invoked')
        }
    else:
        return {
            'statusCode': 300,
            'body': json.dumps('More than 10 Links - Invoking Batch Process')
        }
