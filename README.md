# Testing Airflow DAGs with LocalStack

This project provides a simple example of how to test Apache Airflow DAGs locally with LocalStack. 

## Debug interactively with dag.test()
Airflow 2.5.0 introduced the `dag.test()` method which allows you to run all tasks in a DAG within a single serialized 
Python process without running the Airflow scheduler. The `dag.test()` method allows for faster iteration and use of IDE 
debugging tools when developing DAGs.

## Prerequisites
Ensure that your testing environment has:
* Airflow 2.5.0 or later. You can check your version by running `airflow version`.
* All providers' packages that your DAG uses.
* An initialized Airflow metadata database, if your DAG uses elements of the metadata database like XCom. The Airflow 
metadata database is created when Airflow is first run in an environment. You can check that it exists with `airflow db 
check` and initialize a new database with `airflow db migrate` (`airflow db init` in Airflow versions pre-2.7).
* Docker for running the LocalStack container (installation instructions available [here](https://www.docker.com/get-started/)).

## Installing required dependencies
The project dependencies are provided in the `requirements.txt` file. We recommend creating a dedicated Conda 
environment for managing the dependencies.

Setup and activate Conda environment and install the required dependencies with the following commands:
```shell
# 1. Choose the Python and Apache Airflow versions to use 
export PYTHON_VERSION="3.10"
export AIRFLOW_VERSION="2.9.1"
# 2. Create a new Conda environment named 'testing-airflow'
conda create --name testing-airflow python="${PYTHON_VERSION}" -y
# 3. Activate the newly created Conda environment
conda activate testing-airflow
# 4. Install Apache Airflow and the required dependencies
pip install apache-airflow=="${AIRFLOW_VERSION}" \
  --requirement requirements.txt \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
```

## Set up a Database Backend
Airflow requires a Database Backend to manage its metadata. In production environments, you should consider setting up a 
database backend to PostgreSQL, MySQL, or MSSQL. By default, Airflow uses SQLite, which is intended for development 
purposes only.

For our tests, we will use SQLite. To initialize the SQLite database, please execute the following commands:
```shell
# 1. Configure the location of the SQLite database
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="sqlite:////tmp/airflow.db"
# 2. Initialize the db
airflow db migrate
```
This will create the `airflow.db` file in your `/tmp` directory. 
If you have any issues in setting up the SQLite database, please refer to the [official Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/howto/set-up-database.html#setting-up-a-sqlite-database).

## Run tests
Start the tests with the following command:
```shell
pytest
```