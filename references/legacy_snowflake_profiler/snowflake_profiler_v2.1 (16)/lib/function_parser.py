# Databricks notebook source
"""
Get valid spark sql functions
"""

valid_sql = [a.function for a in spark.sql("SHOW FUNCTIONS").collect()]

# COMMAND ----------

# MAGIC %run ../config/mappers/snowflake_mapper

# COMMAND ----------

# MAGIC %run ../config/mappers/photon_mapper

# COMMAND ----------


"""
Filter out dataframe and get some complexity
"""

from pyspark.sql.functions import col, count, sum, when, size, split, lit, array_except, array, lower, expr, array_distinct, transform, array_intersect, lower, concat_ws, sha2
from pyspark.sql import DataFrame
from typing import List

def parse_queries_for_functions(df : DataFrame, 
                                udf_res : List[str], 
                                table_res : List[str]) -> DataFrame:
  # get all valid functions
  valid_functions = set(valid_sql).union(set(valid_photon)).union(set(snow_funs)).union(set(udf_res))

  _df = (df.groupBy(col("ACCOUNT_URL"), 
                    col("QUERY_TEXT"), 
                    col("CATEGORY"), 
                    col("WAREHOUSE_NAME"))
            .agg(count(col("QUERY_TEXT")).alias("RUN_COUNTS"),
                  sum(col("QUERY_TIME_SECONDS")).alias("QUERY_TIME_SECONDS"),
                  sum(col("TOTAL_CREDITS")).alias("TOTAL_CREDITS"))
            .withColumn("FUNCTIONS", transform(
                              expr("regexp_extract_all(QUERY_TEXT, r'\\b\\w+\\(\\w*\\,*\\s*\\w*\\)*', 0)"),
                            lambda x: lower(split(x, "\(")[0])
                            )
            )
            .withColumn("FUNCTIONS", array_intersect(col("FUNCTIONS"),
                                                      array([lit(a) for a in valid_functions])))
            .withColumn("UNSUPPORTED_FUNCTIONS", array_except(col("FUNCTIONS"),
                                                              array([lit(a) for a in valid_sql])))
            .withColumn("UNSUPPORTED_FUNCTIONS", array_except(col("UNSUPPORTED_FUNCTIONS"),
                                                              array([lit(a) for a in ["table", "from", "select", "with", "distinct", ",", "number", "is_incremental", "config", "source", "ref", "get_snowflake_warehouse"]])))
            .withColumn("PHOTON_FUNCTIONS", array_intersect(col("FUNCTIONS"),
                                                            array([lit(a) for a in valid_photon])))
            .drop("FUNCTIONS")
            .withColumn("FOUND_UDF", array_intersect(col("UNSUPPORTED_FUNCTIONS"),
                                                      array([lit(a) for a in udf_res])))
            .withColumn("TABLES", array_intersect(split(col("QUERY_TEXT"), " "),
                                                  array([lit(a) for a in table_res])))
            .withColumn("CTE_FLAG", lower(col("query_text")).contains("with"))
            .withColumn("WINDOW_FLAG", lower(col("query_text")).contains("over"))
            .withColumn("PIVOT_FLAG", lower(col("query_text")).contains("pivot"))
            .withColumn("AGGREGATION_FLAG", lower(col("query_text")).contains("group by"))
            .withColumn("CROSS_JOIN_FLAG", lower(col("query_text")).contains("cross join"))
            .withColumn("MIGRATION_COMPLEXITY", when(size(col("UNSUPPORTED_FUNCTIONS")) > 4, "complex")
                                                  .when(size(col("UNSUPPORTED_FUNCTIONS")) > 2, "medium")
                                                  .when(size(col("UNSUPPORTED_FUNCTIONS")) > 0, "simple")
                                                  .otherwise("native"))
            .withColumn("FINGERPRINT", sha2(concat_ws("|", col("UNSUPPORTED_FUNCTIONS"), col("PHOTON_FUNCTIONS"), col("FOUND_UDF"), col("TABLES"), col("CTE_FLAG"), col("WINDOW_FLAG"), col("PIVOT_FLAG"), col("AGGREGATION_FLAG"), col("CROSS_JOIN_FLAG"), col("MIGRATION_COMPLEXITY")), 256))
            .repartition(2000))

  return _df