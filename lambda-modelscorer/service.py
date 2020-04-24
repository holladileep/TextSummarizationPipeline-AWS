import decimal
import json
import boto3
import pandas as pd
import rouge
from rouge import FilesRouge, Rouge


def handler(event, context):

    dynamodb = boto3.resource('dynamodb')
    table_scores = dynamodb.Table('scores')

    table_articles = dynamodb.Table('articles')
    response_summary = table_articles.scan()
    data_articles = response_summary['Items']
    df_articles = pd.DataFrame.from_dict(data_articles)
    #df_articles = df_articles[:3]

    table_summary = dynamodb.Table('summary')
    response_summary = table_summary.scan()
    data_summary = response_summary['Items']
    df_summary = pd.DataFrame.from_dict(data_summary)
    #df_summary = df_summary[:3]

    print(df_articles)
    print('-----------')
    print((df_summary))
    df = pd.merge(df_articles,df_summary,on='url')
    print('-----------')
    print(df)

    for index, row in df.iterrows():
        c1 = row['summary_a']
        c2 = row['summary_b']
        r = row['article_text']
        rouge = Rouge()
        a = rouge.get_scores(c1, r)
        score_a = a[0]['rouge-1']['f']
        print('score a')
        print(score_a)

        b = rouge.get_scores(c2, r)
        score_b = b[0]['rouge-1']['f']
        print('score b')
        print(score_b)

        if score_a > score_b :
            best = 'distilbert-base-uncased'
        else:
            best = 'bert-large-uncased'

        table_summary.update_item(
            Key={
                'url': row['url'],

            },
            UpdateExpression="set score_a = :p, score_b = :r, best_summarizer = :b",
            ExpressionAttributeValues={
                ':p': str(score_a),
                ':r': str(score_b),
                ':b': best

            },
        )


    return {
        'statusCode': 200,
        'body': json.dumps('Scores Calculated')
    }