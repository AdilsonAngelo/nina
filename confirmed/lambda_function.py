import boto3
import json
import yaml
import time
import re
import os
import csv

with open('config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)

QUERY = "SELECT * FROM covid_agg"

ATHENA = boto3.client('athena', aws_access_key_id=CONFIG['aws_access_key_id'],
                      aws_secret_access_key=CONFIG['aws_secret_access_key'])

S3RES = boto3.resource('s3', aws_access_key_id=CONFIG['aws_access_key_id'],
                       aws_secret_access_key=CONFIG['aws_secret_access_key'])


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def query_athena():
    bucket, key = CONFIG['confirmed']['bucket'], CONFIG['confirmed']['key']
    response = ATHENA.start_query_execution(
        QueryString='SELECT countryregion, confirmed FROM covid_agg',
        QueryExecutionContext={
            'Database': CONFIG['database'],
        },
        ResultConfiguration={
            'OutputLocation': f's3://{bucket}/{key}'
        }
    )
    return response


def query_result():
    execution = query_athena()
    execution_id = execution['QueryExecutionId']
    state = 'RUNNING'

    while state == 'RUNNING' or state == 'QUEUED':
        response = ATHENA.get_query_execution(QueryExecutionId=execution_id)

        if 'QueryExecution' in response and \
                'Status' in response['QueryExecution'] and \
                'State' in response['QueryExecution']['Status']:
            state = response['QueryExecution']['Status']['State']
            print(state)
            if state == 'FAILED':
                raise RuntimeError('Athena query FAILED!')
            elif state == 'SUCCEEDED':
                print(response)
                s3_path = response['QueryExecution']['ResultConfiguration']['OutputLocation']
                return s3_path
        time.sleep(1)

    return False


def digest_query(query_file):
    path = re.sub('s3://', '', query_file).split('/')
    bucket = path[0]
    key = '/'.join(path[1:])

    local_csv = '/tmp/data.csv'
    obj = S3RES.Object(bucket, key)
    obj.download_file(local_csv)

    _fields = CONFIG['schema']
    with open(local_csv, 'r') as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        res = list(reader)

    os.unlink(local_csv)
    return res


def lambda_handler(event, context):

    operations = {
        'GET',
        'POST'
    }

    operation = event['httpMethod']

    if operation in operations:
        query_file = query_result()
        if not query_file:
            respond(ValueError(f'Unsupported method "{operation}"'))

        response = digest_query(query_file)
        return respond(None, response)
    else:
        return respond(ValueError(f'Unsupported method "{operation}"'))
