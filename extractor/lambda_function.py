import yaml
import os
import re
import csv
import boto3

with open('config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)

S3RES = boto3.resource('s3', aws_access_key_id=CONFIG['aws_access_key_id'],
                       aws_secret_access_key=CONFIG['aws_secret_access_key'])

LOCAL_CSV = f'/tmp/data.csv'


def clean_field(field):
    return ''.join([l for l in field if l.isalpha()]).lower()


def download_csv(bucket, key):
    obj = S3RES.Object(bucket, key)
    obj.download_file(LOCAL_CSV)


def transform_csv(csv_matrix, date):
    _fields = CONFIG['schema']

    csv_matrix[0] = [clean_field(l) for l in csv_matrix[0]]

    template = [(h in _fields) for h in csv_matrix[0]]

    new_csv = [list(filter(lambda x: x in _fields, csv_matrix[0])) + ['date']]

    for row in csv_matrix[1:]:
        new_row = list(
            map(
                lambda x: x[0],
                filter(
                    lambda x: x[1], zip(row, template)
                )
            )
        )
        new_csv.append(new_row + [date])

    return new_csv


def upload_csv(key):
    bucket = CONFIG['s3']['ingest']['bucket']
    key = CONFIG['s3']['ingest']['key'] + f'/{key}'

    obj = S3RES.Object(bucket, key)
    obj.upload_file(LOCAL_CSV)


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    rex_date = re.compile(
        r'.*(?P<data>(?P<ano>\d{4})_(?P<mes>\d{2})_(?P<dia>\d{2})).csv')

    m = rex_date.match(key)
    date = m['data'].replace('_', '-')

    download_csv(bucket, key)

    with open(LOCAL_CSV, 'r') as f:
        csv_matrix = csv.reader(f, delimiter=",")

    os.unlink(LOCAL_CSV)

    new_csv = transform_csv(csv_matrix, date)

    with open(LOCAL_CSV, "w", newline="\n") as f:
        writer = csv.writer(f)
        writer.writerows(a)

    filename = os.path.basename(key)
    upload_csv(filename)

    os.unlink(LOCAL_CSV)
