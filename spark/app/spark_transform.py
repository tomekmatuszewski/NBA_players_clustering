import os
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType
from pyspark.sql.functions import col, lit
from pyspark.sql import SparkSession, DataFrame
from dotenv import load_dotenv
from pathlib import Path
import logging

logging.basicConfig(
     filename='log_file_name.log',
     level=logging.INFO,
     format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
     datefmt='%H:%M:%S'
 )

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

STATS_DATA_URL = os.getenv("STATS_DATA_URL")
URL_STATS_PATTERN_SEASON = os.getenv("URL_STATS_PATTERN_SEASON")


def create_table_schema(column_names: list) -> StructType:
    schema = map(lambda x: StructField(x, StringType(), True), column_names)
    return StructType(list(schema))


def create_dataframe(data: list, schema: StructType, spark: SparkSession, season: str):
    df = spark.createDataFrame(data=data, schema=schema)
    df = df.withColumn('season', lit(season))
    return df


def get_converted_df(df: DataFrame) -> DataFrame:
    integer_fields = ["RK", "GP", "DD2", "TD3"]
    string_fields = ["Name", "POS", "season"]
    for column in df.columns:
        if column in integer_fields:
            df = df.withColumn(column, col(column).cast(IntegerType()))
        elif column in string_fields:
            continue
        else:
            df = df.withColumn(column, col(column).cast(FloatType()))
    return df


