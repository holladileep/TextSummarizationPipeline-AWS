import json
import os
import boto3
import sentry_sdk
from sentry_sdk import capture_message, capture_exception
from configparser import ConfigParser


def lambda_handler(event, context):
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

    for obj in s3.Bucket(bucket).objects.filter(Prefix=config.get('aws', 'stage2')):
        tmp_file = obj.key
        if tmp_file.endswith('.json'):
            msg = {"tmp_file": tmp_file}
            
            try:
                invoke_response = client.invoke(FunctionName="SentimentConsumer",
                                                InvocationType='Event',
                                                Payload=json.dumps(msg))
                print(invoke_response)

            except Exception as e:
                capture_exception(e)
                capture_message('Could not Invoke Lambda for URL - ' + u)

            print('File Sent to Consumer Lambda for Analysis')

    return {
        'statusCode': 200,
        'body': json.dumps('Pushed all Files')
    }
