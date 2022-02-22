import os

from airflow.utils.dates import days_ago
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

spark_master = os.getenv("SPARK_MASTER")  # spark_master=spark://spark:7077"
postgres_db = os.getenv("POSTGRES_DB")  # postgres_db = "jdbc:postgresql://postgres:5432/nba"
path_to_jar = os.getenv("POSTGRES_JAR")  # path_to_jar = "/opt/bitnami/spark/jars/postgresql-42.3.2.jar"
application_path = os.getenv("SPARK_APP_PATH")  # application_path = "/opt/bitnami/spark/app/load_stats_tables.py"

args = {
    'owner': 'admin',
    'start_date': days_ago(1)
}

dag = DAG('spark_load_to_postgres', schedule_interval=None, default_args=args, catchup=False)


def finish():
    print("Table load to Postgres DB")


with dag:
    job1 = SparkSubmitOperator(
        task_id="spark_job",
        application=application_path,
        name="load_stats_tables",
        conn_id="spark_default",
        verbose=True,
        conf={"spark.master": spark_master},
        application_args=[postgres_db, path_to_jar],
        driver_class_path=path_to_jar
    )

    job2 = PythonOperator(
        task_id='2',
        python_callable=finish,
        retries=3
    )

    job1 >> job2
