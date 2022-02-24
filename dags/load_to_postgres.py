import os

from airflow.utils.dates import days_ago
from airflow.models import DAG
from airflow.operators.dummy import DummyOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

spark_master = os.getenv("SPARK_MASTER")  # spark_master=spark://spark:7077"
postgres_db = os.getenv("POSTGRES_DB")  # postgres_db = "jdbc:postgresql://postgres:5432/nba"
path_to_jar = os.getenv("POSTGRES_JAR")  # path_to_jar = "/opt/bitnami/spark/jars/postgresql-42.3.2.jar"

application_path_stats = '/opt/bitnami/spark/app/load_stats_tables.py'
application_path_injuries = '/opt/bitnami/spark/app/load_injuries_table.py'
application_path_salaries = '/opt/bitnami/spark/app/load_salaries_table.py'

args = {
    'owner': 'admin',
    'start_date': days_ago(1)
}

dag = DAG('spark_load_to_postgres', schedule_interval=None, default_args=args, catchup=False)


with dag:

    job1 = DummyOperator(
        task_id="start"
    )

    job2 = SparkSubmitOperator(
        task_id="spark_job_stats",
        application=application_path_stats,
        name="load_stats_tables",
        conn_id="spark_default",
        verbose=True,
        conf={"spark.master": spark_master},
        application_args=[postgres_db, path_to_jar],
        driver_class_path=path_to_jar
    )

    job3 = SparkSubmitOperator(
        task_id="spark_job_injuries",
        application=application_path_injuries,
        name="load_injuries_table",
        conn_id="spark_default",
        verbose=True,
        conf={"spark.master": spark_master},
        application_args=[postgres_db, path_to_jar],
        driver_class_path=path_to_jar
    )

    job4 = SparkSubmitOperator(
        task_id="spark_job_salaries",
        application=application_path_salaries,
        name="load_salaries_table",
        conn_id="spark_default",
        verbose=True,
        conf={"spark.master": spark_master},
        application_args=[postgres_db, path_to_jar],
        driver_class_path=path_to_jar
    )

    job1 >> [job2, job3, job4]
