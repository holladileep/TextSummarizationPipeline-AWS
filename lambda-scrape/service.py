import json
import pandas as pd
import sentry_sdk
from newspaper import Article
from sentry_sdk import capture_exception
import os
import boto3
from configparser import ConfigParser

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

    df = pd.DataFrame(columns=['url', 'publish_date', 'authors', 'summary', 'text'])

    # Download CSV with list of Valid URLs
    s3.Bucket(bucket).download_file(config.get('aws', 'link_op') + 'valid_url.csv', '/tmp/valid_url.csv')

    df2 = pd.read_csv('/tmp/valid_url.csv')

    for index, row in df2.iterrows():
        u = row['url'].strip()

        try:
            article = Article(u)
            article.download()
            article.parse()

            df = df.append({'url': article.url, 'publish_date': article.publish_date, 'authors': article.authors,
                            'summary': article.summary, 'text': article.text},
                           ignore_index=True)

        except Exception as e:
            capture_exception(e)
            # capture_message('Something went wrong')
            print('Could not Parse URL ' + u)

        print(df)

    # Convert to JSON
    df.to_json('/tmp/temp.json', orient='records', indent=1)

    print('File Generated')

    s3.Bucket(bucket).upload_file('/tmp/temp.json', config.get('aws', 'stage2') + 'temp.json')
    print('File Uploaded to Stage2')

    return {
        'statusCode': 200,
        'body': json.dumps('Scrape Done!')
    }
