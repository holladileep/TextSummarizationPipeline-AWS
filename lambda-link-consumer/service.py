import json
import pandas as pd
import sentry_sdk
from newspaper import Article
from sentry_sdk import capture_exception
import os
import boto3
from configparser import ConfigParser



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

    # Initiate Sentry SDK
    sentry_sdk.init(config.get('sentry', 'init_params'))

    df = pd.DataFrame(columns=['url', 'publish_date', 'authors', 'summary', 'text'])


    # Get the passed URL and FileID from ProducerLambda
    url = event.get('url')
    file_id = event.get('file_id')

    u = url.strip()

    try:
        article = Article(u)
        article.download()
        article.parse()

        df = df.append({'url': article.url, 'publish_date': article.publish_date, 'authors': article.authors,
                        'summary': article.summary, 'text': article.text},
                       ignore_index=True)

    except Exception as e:
        capture_exception(e)
        capture_message('Could not Parse URL ' + u)
        print('Could not Parse URL ' + u)

    print(df)

# Convert to JSON

    tmp_filename = str(file_id) + 'temp.json'
    df.to_json('/tmp/' + tmp_filename, orient='records', indent=1)

    print('File Generated')

    s3.Bucket(bucket).upload_file('/tmp/' + tmp_filename, config.get('aws', 'stage2') + tmp_filename)
    print('File Uploaded to Stage2')

    return {
        'statusCode': 200,
        'body': json.dumps('Scrape Done!')
    }
    