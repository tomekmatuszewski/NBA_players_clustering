from airflow.utils.dates import days_ago
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow import settings
from airflow.models import Connection
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

args = {
    'owner': 'admin',
    'start_date': days_ago(1)
}

dag = DAG('deploy_connections',
          schedule_interval=None,
          default_args=args,
          template_searchpath='/opt/airflow/dags/sql',
          catchup=False)


def deploy_connections():
    conn_spark = Connection(
        conn_id='spark_default',
        conn_type='Spark',
        description='connection to spark container',
        host='spark://spark',
        port=7077,
        extra={"queue": "root.default"}
    )
    conn_postgres = Connection(
        conn_id='nba_postgres',
        schema='nba',
        conn_type='Postgres',
        description='connection to nba postgres db',
        host='postgres',
        port=5432,
        login='nba',
        password='nba'
    )
    session = settings.Session()
    session.add(conn_spark)
    session.add(conn_postgres)
    session.commit()


with dag:
    job1 = PythonOperator(
        task_id='connections',
        python_callable=deploy_connections,
        retries=3
    )

    # job2 = PostgresOperator(
    #     task_id='deploy_tables',
    #     postgres_conn_id='nba_postgres',
    #     sql='create_tables.sql',
    #     autocommit=True
    # )
