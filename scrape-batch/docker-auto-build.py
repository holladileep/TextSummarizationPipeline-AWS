from newspaper import Article
import pandas as pd
from datetime import datetime
import boto3
import sentry_sdk
sentry_sdk.init("")
from sentry_sdk import capture_message, capture_exception
import random
import string
import json


s3 = boto3.resource('s3',
                    aws_access_key_id='',
                    aws_secret_access_key='')
bucket = ''
s3.Bucket(bucket).download_file('stage1/valid_url.csv', 'valid_url.csv')

df2 = pd.read_csv('valid_url.csv')

for index, row in df2.iterrows():
    df = pd.DataFrame(columns=['url', 'publish_date', 'authors', 'summary', 'text'])
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
        print ('Could not Parse URL ' + u)

    file_id = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    tmp_filename = file_id + 'temp.json'
    df.to_json(tmp_filename, orient='records')
    s3.Bucket(bucket).upload_file(tmp_filename, 'stage2/' + tmp_filename)
    print('File Uploaded')


