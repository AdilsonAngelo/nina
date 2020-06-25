import time
import yaml
import boto3

with open('config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)

QUERY = """
CREATE TABLE covid_agg AS 
    (SELECT countryregion,
         SUM(confirmed) AS confirmed,
         SUM(recovered) AS recovered,
         SUM(deaths) AS deaths
    FROM COVID
    GROUP BY  countryregion
    ORDER BY  confirmed DESC)
"""

ATHENA = boto3.client('athena', aws_access_key_id=CONFIG['aws_access_key_id'],
                      aws_secret_access_key=CONFIG['aws_secret_access_key'])


def lambda_handler(event, context):

    bucket, key = CONFIG['s3agg']['bucket'], CONFIG['s3agg']['key']

    ATHENA.start_query_execution(
        QueryString='DROP TABLE IF EXISTS `covid_agg`;',
        QueryExecutionContext={
            'Database': CONFIG['database'],
        },
        ResultConfiguration={
            'OutputLocation': f's3://{bucket}/{key}'
        }
    )

    time.sleep(3)

    ATHENA.start_query_execution(
        QueryString=QUERY,
        QueryExecutionContext={
            'Database': CONFIG['database'],
        },
        ResultConfiguration={
            'OutputLocation': f's3://{bucket}/{key}'
        }
    )

    print('Done!!')
