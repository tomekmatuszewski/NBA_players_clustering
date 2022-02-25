import logging
import os
import sys
from pyspark.sql import SparkSession
from web_scraper_extract_salaries import get_schema, scrap_urls_and_flags, main_crawler
from spark_transform import create_table_schema, create_dataframe, transform_df_salaries
import asyncio
import pathlib
from concurrent.futures import ThreadPoolExecutor

BASEDIR = pathlib.Path(__name__).resolve().parent.parent

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# env variables
URL = os.getenv("SALARIES_DATA_URL")
postgres_db_user = os.getenv('POSTGRES_DB_USER')
postgres_db_password = os.getenv('POSTGRES_DB_PASSWORD')

postgres_db = sys.argv[1]
path_to_jar = sys.argv[2]

# local
# path_to_jar = BASEDIR / "jars/postgresql-42.3.2.jar"

spark = SparkSession.builder \
    .config("spark.jars", path_to_jar) \
    .config("spark.driver.extraClassPath", path_to_jar) \
    .config("spark.executor.extraClassPath", path_to_jar) \
    .config("spark.repl.local.jars", path_to_jar) \
    .getOrCreate()


def load_to_postgres(url_table: tuple, data: list) -> None:
    schema = create_table_schema(get_schema(url_table[0]))
    df = create_dataframe(data, schema, spark, url_table[1])
    df = transform_df_salaries(df)
    if not df.rdd.isEmpty():
        df.write.format("jdbc"). \
            option("url", postgres_db). \
            option("driver", "org.postgresql.Driver"). \
            option("dbtable", f"public.players_salaries"). \
            option("user", postgres_db_user). \
            option("password", postgres_db_password). \
            mode("append"). \
            save()


urls_flags = scrap_urls_and_flags(URL)
data = asyncio.run(main_crawler(urls_flags))

# for url_table, data in zip(urls_flags, data):
#     load_to_postgres(url_table, data)

with ThreadPoolExecutor() as executor:
    executor.map(load_to_postgres, urls_flags, data)
