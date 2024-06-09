import logging
import requests
from airflow.decorators import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from pendulum import datetime, duration

logger = logging.getLogger(__name__)


@task
def create_bucket(s3_bucket: str, region: str) -> str:
    """
    Creates an S3 bucket if it does not already exist.

    :param s3_bucket: The name of the S3 bucket to be created.
    :param region: The AWS region in which the S3 bucket should be created.
    :return: The name of the S3 bucket.
    """
    s3_hook = S3Hook()
    logger.info(f"Checking if S3 bucket {s3_bucket} exists...")
    if not s3_hook.check_for_bucket(bucket_name=s3_bucket):
        logger.info(f"S3 bucket {s3_bucket} does not exist. Creating...")
        s3_hook.create_bucket(bucket_name=s3_bucket, region_name=region)
        logger.info(f"Created S3 bucket {s3_bucket} in region {region}.")
    else:
        logger.info(f"S3 bucket {s3_bucket} already exists.")
    return s3_bucket


@task
def download_to_s3(url: str, s3_bucket: str) -> str:
    """
    Downloads a file from the specified URL and uploads it to an S3 bucket.

    :param url: The URL of the file to be downloaded.
    :param s3_bucket: S3 bucket where the file will be uploaded.
    :return: The S3 URI of the uploaded file.
    """
    s3_hook = S3Hook()
    filename = url.split("/")[-1]
    s3_key = f"extract/{filename}"
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        response.raw.decode_content = True
        s3_hook.load_file_obj(file_obj=response.raw, key=s3_key, bucket_name=s3_bucket, replace=True)
    s3_uri = f"s3://{s3_bucket}/{s3_key}"
    logger.info(f"File saved at: {s3_uri}")
    return s3_uri


@dag(
    dag_id="example_dag",
    start_date=datetime(2024, 6, 9),
    doc_md="""
        Example DAG 

        A very simple pipeline used to extract a CSV file (Rotten Tomato ratings of movies with Robert De Niro) from 
        a public server and save it on an S3 bucket.

        Data source: [here](https://people.sc.fsu.edu/~jburkardt/data/data.html)
    """,
    schedule=None,
    params={
        "url": "https://people.sc.fsu.edu/~jburkardt/data/csv/deniro.csv",
        "s3_bucket": "test-bucket",
        "region": "eu-central-1",
    },
    default_args={
        "retries": 3,
        "retry_delay": duration(minutes=5),
    }
)
def example_dag():
    s3_bucket = create_bucket(s3_bucket="{{ params.s3_bucket }}", region="{{ params.region }}")
    csv_s3a_uri = download_to_s3(url="{{ params.url }}", s3_bucket="{{ params.s3_bucket }}")
    s3_bucket >> csv_s3a_uri


example_dag()
