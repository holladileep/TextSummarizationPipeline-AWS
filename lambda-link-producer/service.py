import json
import os
import random
import string
from configparser import ConfigParser
import boto3
import pandas as pd
import sentry_sdk
from sentry_sdk import capture_message, capture_exception
import string 
import random

def handler(event, context):
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

    try:
        # Download CSV with list of Valid URLs
        s3.Bucket(bucket).download_file(config.get('aws', 'link_op') + 'valid_url.csv', '/tmp/valid_url.csv')


    except Exception as e:
        capture_exception(e)
        capture_message('Input File not Found on S3')

        return {
            'statusCode': 400,
            'body': json.dumps('Input file not Found on S3')
        }
    df2 = pd.read_csv('/tmp/valid_url.csv')

    for index, row in df2.iterrows():
        u = row['url'].strip()
        file_id = ''.join(random.choice(string.ascii_lowercase) for i in range(8))

        msg = {"url": u, "file_id": file_id}

        try:
            invoke_response = client.invoke(FunctionName="LinkConsumerScrape",
                                            InvocationType='Event',
                                            Payload=json.dumps(msg))
            print(invoke_response)

        except Exception as e:
            capture_exception(e)
            capture_message('Could not Invoke Lambda for URL - ' + u)

        print('Link Sent to Scrape Lambda' + u)

    return {
        'statusCode': 200,
        'body': json.dumps('Process Done!')
    }
