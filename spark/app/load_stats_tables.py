import logging
import os
import sys
from pyspark.sql import SparkSession
from pathlib import Path
from web_scraper_extract_stats import get_stats_data, get_urls_and_table_names, get_schema_stats
from spark_transform import create_table_schema, create_dataframe, get_converted_stats_df

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

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


def load_to_postgres(url: str, table: str, service) -> None:
    column_names, data = get_schema_stats(url), get_stats_data(url, service)
    schema = create_table_schema(column_names)
    df = create_dataframe(data, schema, spark, table)
    df = get_converted_stats_df(df)
    df.write.format("jdbc"). \
        option("url", postgres_db). \
        option("driver", "org.postgresql.Driver"). \
        option("dbtable", f"public.players_stats"). \
        option("user", postgres_db_user). \
        option("password", postgres_db_password). \
        mode("append"). \
        save()


urls = get_urls_and_table_names(STATS_DATA_URL, URL_STATS_PATTERN_SEASON)

# install chrome driver used by selenium
service = Service(ChromeDriverManager().install())

for url, table in urls:
    load_to_postgres(url, table, service)
