import json
import os
from configparser import ConfigParser
from sentry_sdk import capture_message
import boto3
import pandas as pd
import sentry_sdk



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

    # Download CSV with list of Valid URLs
    s3.Bucket(bucket).download_file(config.get('aws', 'link_op') + 'valid_url.csv', '/tmp/valid_url.csv')
    df2 = pd.read_csv('/tmp/valid_url.csv')

    count_row = df2.shape[0]

    if (count_row <= 60):
        capture_message('Lambda Process to be Followed ; Less than 60 links to Scrape')
        return {
            'statusCode': 200,
            'body': json.dumps('Less than 60 links to Scrape - Lambda to be Invoked')
        }
    else:
        capture_message('Batch Process to be Followed ; Less than 60 links to Scrape')
        return {
            'statusCode': 300,
            'body': json.dumps('More than 10 Links - Invoking Batch Process')
        }
