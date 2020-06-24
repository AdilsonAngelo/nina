import yaml
import json
import os
import re

import requests
import boto3

with open('config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)

URL = 'https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports'
RAW_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}-{}-{}.csv'.format

REX_URLS = re.compile(
    r'href="(.*)?/(?P<mes>\d{2})-(?P<dia>\d{2})-(?P<ano>\d{4}).csv"')

S3RES = boto3.resource('s3', aws_access_key_id=CONFIG['aws_access_key_id'],
                       aws_secret_access_key=CONFIG['aws_secret_access_key'])


def get_urls():
    res = requests.get(URL)
    lines = res.text.split('\n')
    matches = filter(lambda x: bool(x), map(REX_URLS.search, lines))
    return list(map(lambda x: RAW_URL(x['mes'], x['dia'], x['ano']), matches))


def get_consumed_urls():
    s3obj = CONFIG['s3']['consumed']
    obj = S3RES.Object(s3obj['bucket'], s3obj['key'])
    local_file = '/tmp/consumed.json'
    with open(local_file, 'wb') as f:
        obj.download_fileobj(f)
    with open(local_file, 'r') as f:
        consumed = json.load(f)
    os.unlink(local_file)
    return consumed


def download_csvs(csvs):
    rex_data = re.compile(
        r'.*/(?P<mes>\d{2})-(?P<dia>\d{2})-(?P<ano>\d{4}).csv')
    bucket, path = CONFIG['s3']['csvs']['bucket'], CONFIG['s3']['csvs']['key']

    for url in csvs:
        res = requests.get(url)
        m = rex_data.search(url)

        filename = f'{m["ano"]}_{m["mes"]}_{m["dia"]}.csv'
        local_file = f'/tmp/{filename}'

        with open(local_file, 'wb') as f:
            f.write(res.content.decode("utf-8-sig").encode('utf-8'))

        obj = S3RES.Object(bucket, f'{path}/{filename}')
        obj.upload_file(local_file)
        os.unlink(local_file)


def update_consumed(new_list):
    s3obj = CONFIG['s3']['consumed']
    obj = S3RES.Object(s3obj['bucket'], s3obj['key'])
    local_file = '/tmp/consumed.json'

    with open(local_file, 'w') as f:
        json.dump(new_list, f)

    obj.upload_file(local_file)
    os.unlink(local_file)


def lambda_handler(event, context):
    urls = get_urls()
    consumed = get_consumed_urls()
    not_consumed = list(filter(lambda x: x not in consumed, urls))
    download_csvs(not_consumed)
    update_consumed(consumed + not_consumed)
    print('Novas urls consumidas:')
    print('\n'.join(not_consumed))


if __name__ == "__main__":
    lambda_handler(None, None)
