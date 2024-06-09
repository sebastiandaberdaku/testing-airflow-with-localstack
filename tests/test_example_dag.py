from airflow.providers.amazon.aws.hooks.s3 import S3Hook

from dags.example_dag import example_dag

def test_example_dag():
    # Run example_dag
    example_dag().test()
    # Assert that the file was correctly saved on S3
    s3_hook = S3Hook()
    assert s3_hook.check_for_key("s3://test-bucket/extract/deniro.csv")
