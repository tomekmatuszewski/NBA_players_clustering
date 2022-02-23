import logging
import os
import sys
from pyspark.sql import SparkSession
from pathlib import Path
from web_scraper_extract_injuries import get_schema, scrap_urls_and_flags, main_crawler
from spark_transform import create_table_schema, create_dataframe, filter_injuries_df
import asyncio

BASEDIR = Path(__file__).resolve().parent.parent

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# env variables
STATS_DATA_URL = os.getenv("STATS_DATA_URL")
URL_STATS_PATTERN_SEASON = os.getenv("URL_STATS_PATTERN_SEASON")
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

sc = spark.sparkContext


def load_to_postgres(url_table: tuple, data: list) -> None:
    schema = create_table_schema(get_schema(url_table[0]))
    df = create_dataframe(data, schema, spark, url_table[1])
    df = filter_injuries_df(df)
    df.write.format("jdbc"). \
        option("url", postgres_db). \
        option("driver", "org.postgresql.Driver"). \
        option("dbtable", f"public.players_injuries"). \
        option("user", postgres_db_user). \
        option("password", postgres_db_password). \
        mode("append"). \
        save()


urls_flags = scrap_urls_and_flags(os.getenv('INJURIES_DATA_URL'))
data = asyncio.run(main_crawler(urls_flags))
zipped_data = list(zip(urls_flags, data))

for url_table, data in zipped_data:
    load_to_postgres(url_table, data)
