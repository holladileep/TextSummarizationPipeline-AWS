import urllib
import requests
import pandas as pd
import json
import boto3
from configparser import ConfigParser
import os
from sentry_sdk import capture_message
import sentry_sdk


def handler(event, context):


    bucket = os.environ['ip_bucket']
    s3 = boto3.resource('s3')

    s3.Bucket(bucket).download_file('config/config.ini', '/tmp/config.ini')

    config = ConfigParser()
    config.read('/tmp/config.ini')
    print ('Done')

    input_dir = config.get('aws', 'input_dir')
    stage1 = config.get('aws', 'link_op')

    sentry_sdk.init(config.get('sentry', 'init_params'))

    s3_files = []

    for obj in s3.Bucket(bucket).objects.filter(Prefix=input_dir):
        tmp_file = obj.key
        if tmp_file.endswith('.txt'):
            s3_files.append('tmp/' + os.path.basename(tmp_file))
            s3.Bucket(bucket).download_file(tmp_file, 'tmp/' + os.path.basename(tmp_file))

    print(s3_files)

    valid_url = pd.DataFrame(columns=['url'])
    invalid_url = pd.DataFrame(columns=['url'])

    for file in s3_files:

        with open(file, "r") as a_file:
            for line in a_file:
                u = line.strip()
                try:
                    request = requests.get(u, timeout=6)
                except:
                    print('Invalid URL: ' + u)
                    invalid_url = invalid_url.append({'url': u}, ignore_index=True)
                    continue

                if request.status_code == 200:
                    print('Valid Url: ' + u)
                    valid_url = valid_url.append({'url': u}, ignore_index=True)
                else:
                    print('Invalid URL: ' + u)
                    capture_message('Invalid URL: ' + u)
                    invalid_url = invalid_url.append({'url': u}, ignore_index=True)

    s3.Bucket(bucket).upload_file('/tmp/valid_url.csv', stage1 + 'valid_url.csv')
    s3.Bucket(bucket).upload_file('/tmp/invalid_url.csv', stage1 + 'invalid_url.csv')

    return {
        'statusCode': 200,
        'body': json.dumps('Process Done!')
    }
