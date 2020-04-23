# -*- coding: utf8-*-
from __future__ import print_function  # Python 2/3 compatibility
import boto3
import json
import decimal
import os
from configparser import ConfigParser
import sentry_sdk


def handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('articles')

    bucket = os.environ['ip_bucket']
    s3 = boto3.resource('s3')

    comprehend = boto3.client(service_name='comprehend')

    # Download Config File
    s3.Bucket(bucket).download_file('config/config.ini', '/tmp/config.ini')
    print('Config File Downloaded')

    # Initialize Config Parser
    config = ConfigParser()
    config.read('/tmp/config.ini')
    print('Config File Parsed')

    # Download JSON with scraped data
    tmp_file = event.get('tmp_file')
    s3.Bucket(bucket).download_file(tmp_file, '/tmp/temp.json')

    with open("/tmp/temp.json") as json_file:
        articles = json.load(json_file, parse_float=decimal.Decimal)
        for a in articles:
            if a['text'] != '':  # Check if 'text is not an empty string
                text = a['text']
            else:  # If 'text is empty, continue with next record
                continue
            url = a['url']
            print('Calling DetectSentiment')

            print(text)

            # Calling AWS Comprehend API
            a = json.dumps(comprehend.detect_sentiment(Text=text[:4000], LanguageCode='en'), sort_keys=True, indent=4)
            json1_data = json.loads(a)

            print(json1_data)

            # Loading DynamoDB with the Sentiment and the corresponding Sentiment score
            if json1_data["Sentiment"] == 'POSITIVE':
                table.update_item(
                    Key={
                        'url': url,
                    },
                    UpdateExpression="set sentiment = :s, sentiment_score = :c",
                    ExpressionAttributeValues={
                        ':s': json1_data["Sentiment"],
                        ':c': decimal.Decimal(json1_data["SentimentScore"]["Positive"])

                    },
                )
            if json1_data["Sentiment"] == 'NEGATIVE':
                table.update_item(
                    Key={
                        'url': url,
                    },
                    UpdateExpression="set sentiment = :s, sentiment_score = :c",
                    ExpressionAttributeValues={
                        ':s': json1_data["Sentiment"],
                        ':c': decimal.Decimal(json1_data["SentimentScore"]["Negative"])
                    },
                )
            if json1_data["Sentiment"] == 'NEUTRAL':
                table.update_item(
                    Key={
                        'url': url,
                    },
                    UpdateExpression="set sentiment = :s, sentiment_score = :c",
                    ExpressionAttributeValues={
                        ':s': json1_data["Sentiment"],
                        ':c': decimal.Decimal(json1_data["SentimentScore"]["Neutral"])
                    },
                )
            if json1_data["Sentiment"] == 'MIXED':
                table.update_item(
                    Key={
                        'url': url,
                    },
                    UpdateExpression="set sentiment = :s, sentiment_score = :c",
                    ExpressionAttributeValues={
                        ':s': json1_data["Sentiment"],
                        ':c': decimal.Decimal(json1_data["SentimentScore"]["Mixed"])
                    },
                )

            print('End of DetectSentiment')

            print("Adding sentiment and sentiment scores:", url)
    return {
        'statusCode': 200,
        'body': json.dumps('Sentiment Analysis Complete')
    }