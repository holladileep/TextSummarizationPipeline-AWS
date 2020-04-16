import urllib
import requests
import pandas as pd
import json
import boto3
from configparser import ConfigParser
import os


def handler(event, context):


    bucket = os.environ['ip_bucket']
    s3 = boto3.resource('s3')

    s3.Bucket(bucket).download_file('config/config.ini', '/tmp/config.ini')

    print ('File Downloaded')

    config = ConfigParser()
    config.read('/tmp/config.ini')
    print ('Done')

    input_dir = config.get('aws', 'input_dir')
    stage1 = config.get('aws', 'link_op')

    s3.Bucket(bucket).download_file(input_dir + 'demo.txt', '/tmp/demo.txt')


    valid_url = pd.DataFrame(columns=['url'])
    invalid_url = pd.DataFrame(columns=['url'])

    with open("/tmp/demo.txt", "r") as a_file:
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
                invalid_url = invalid_url.append({'url': u}, ignore_index=True)

    valid_url.to_csv(r'/tmp/valid_url.csv', index=None)
    invalid_url.to_csv(r'/tmp/invalid_url.csv', index=None)

    s3.Bucket(bucket).upload_file('/tmp/valid_url.csv', stage1 + 'valid_url.csv')
    s3.Bucket(bucket).upload_file('/tmp/invalid_url.csv', stage1 + 'invalid_url.csv')

    return {
        'statusCode': 200,
        'body': json.dumps('Process Done!')
    }
