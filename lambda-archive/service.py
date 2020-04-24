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

    # Download Config File
    s3.Bucket(bucket).download_file('config/config.ini', '/tmp/config.ini')
    print('Config File Downloaded')

    # Initialize Config Parser
    config = ConfigParser()
    config.read('/tmp/config.ini')
    print('Config File Parsed')

    for obj in s3.Bucket(bucket).objects.filter(Prefix=config.get('aws', 'stage2')):
        tmp_file = obj.key
        print (tmp_file)
        if tmp_file.endswith('.json'):
            copy_source = {
                    'Bucket': bucket,
                    'Key': tmp_file
                            }
            s3.meta.client.copy(copy_source, bucket, 'archive/' + tmp_file)
            s3.Object(bucket, tmp_file).delete()
        
        
    
    return {
        'statusCode': 200,
        'body': json.dumps('Process Complete')
    }
