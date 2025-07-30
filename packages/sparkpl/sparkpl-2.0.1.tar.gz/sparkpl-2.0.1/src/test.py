import polars as pl
from pyspark.sql import SparkSession
from sparkpl.converter import DataFrameConverter, spark_to_polars, polars_to_spark

# Initialize Spark
spark = SparkSession.builder.appName("MyApp").getOrCreate()

# Method 1: Convenience functions
spark_df = spark.createDataFrame([(1, "Alice"), (2, "Bob")], ["id", "name"])
polars_df = spark_to_polars(spark_df)
spark_df_back = polars_to_spark(polars_df)

# Method 2: Using converter class
converter = DataFrameConverter(spark)
polars_df = converter.spark_to_polars(spark_df)
print(type(polars_df))
spark_df = converter.polars_to_spark(polars_df, table_name="my_table")
print(type(spark_df))