# Databricks notebook source
# MAGIC %run ../config/mappers/tables_to_ingest

# COMMAND ----------


"""
Snowflake Profiler Class
"""

from typing import Dict, Callable, Tuple
from delta import DeltaTable
from pyspark.sql import DataFrame
from pyspark.sql.functions import lit, col, to_timestamp, max, lower, current_timestamp
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging


class SnowflakeProfiler:
    """
    This is a class that loads data from Snowflake into
    the accounts usage
    """

    __slots__ = ("_storage", "_credentials", "_log", "_overwrite")

    def __init__(self, storage: str, overwrite: bool = False) -> None:
        """
        Initialize the class

        Params :
        storage : Cloud storage (ADLS, S3, GCS) for storing
        credentials : {"sfURL"       : "<account_identifier>.snowflakecomputing.com",
                       "sfUser"      : "<user_name>",
                       "sfPassword"  : "<password>",
                       "sfDatabase"  : "<database>",
                       "sfSchema"    : "<schema>",
                       "sfWarehouse" : "<warehouse>"}
        overwrite : Boolean to determine whether or not to all profiler runs
        """

        self._storage: str = storage
        self._credentials: Dict[str, Dict[str, str]] = dict()
        self._log: str = "profiler_log"
        self._overwrite: bool = overwrite

    def __validate_credentials(self, creds: Dict[str, str]) -> bool:
        """
        Validate if credentials are valid
        """
        try:
            (
                spark.read.format("snowflake")
                .options(**creds)
                .option("query", "SELECT 1")
                .load()
                .collect()
            )
            logging.info(f"{str(datetime.now())[:-3]} : Connected to snowflake")
        except Exception as err:
            raise ValueError(
                f"Failed to connect to snowflake with {creds}, error : {err}"
            )
    
    def credit_rate(self, creds: Dict[str, str]) -> float:
        """
        Get the Snowflake compute unit credit rate
        """
        
        # query to generate the adjusted rate
        _query = """
                 SELECT (SUM(USAGE_IN_CURRENCY) / SUM(USAGE)) AS ADJUSTED_RATE
                 FROM SNOWFLAKE.ORGANIZATION_USAGE.USAGE_IN_CURRENCY_DAILY
                 WHERE USAGE_DATE >= DATEADD('DAY', -90, CURRENT_TIMESTAMP)
                   AND lower(USAGE_TYPE) = 'compute'
        
        """
        
        try:
            logging.debug(f"{str(datetime.now())[:-3]} : Getting snowflake credit rate using {_query}")
            
            _res = (
                spark.read.format("snowflake")
                .options(**creds)
                .option("query", _query)
                .load()
                .collect()
            )
            logging.info(f"{str(datetime.now())[:-3]} : Got snowflake credit rate for last 90 days")
            
            return float(_res[0][0])
          
        except Exception as err:
            raise ValueError(
                f"Failed to get snowflake credit rate, error : {err}"
            )
        

    def __create_profiler_log(self) -> bool:
        """
        Create the profiler log if it isn't available
        """

        try:
            # check if we want to remove previous loads
            if self._overwrite == True:
                logging.warning(
                    f"{str(datetime.now())[:-3]} : Overwrite mode engaged, removing profiler logs and data"
                )
                dbutils.fs.rm(self._storage, True)
                dbutils.fs.mkdirs(self._storage)
                logging.info(
                    f"{str(datetime.now())[:-3]} : Removed files in {self._storage}"
                )

            _query = f"CREATE TABLE IF NOT EXISTS delta.`{self._storage}/{self._log}` (account_url string, ingested_time timestamp, table string) USING DELTA"

            logging.debug(
                f"{str(datetime.now())[:-3]} : Creating profiler table with {_query} at {self._storage}/{self._log}"
            )
            # create the profiler table
            spark.sql(_query)

            logging.info(
                f"{str(datetime.now())[:-3]} : Loaded profiler log at {self._storage}/{self._log}"
            )

        except Exception as err:
            raise ValueError(f"Failed to create profiler log, err : {err}")

    def __read_snowflake_factory(
        self, creds: Dict[str, str]
    ) -> Callable[[str], Tuple[str, str, str]]:
        """
        Return a function that will take a table name
        and ingest to delta
        """

        def _fun(table: str) -> Callable[[str], Tuple[str, str, str]]:
            """
            Function to ingest a table from Snowflake
            """
            try:
                # check if are in overwrite mode or doing incremental loads
                if self._overwrite == False and (
                    "history" in table.lower()
                    or table.lower() in incremental_columns.keys()
                ):
                    # get incremental column, default to "END_TIME"
                    _incremental_column = (
                        incremental_columns.get(table.lower())
                        or "END_TIME"
                    )
                    logging.debug(
                        f"{str(datetime.now())[:-3]} : Using incremental load for {table} with key : {_incremental_column}"
                    )
                    try:
                        _previous_ingested_time = str(
                            spark.read.format("delta")
                            .load(f"{self._storage}/{table}")
                            .where(col("account_url") == creds["sfURL"])
                            .select(max(col(_incremental_column)))
                            .collect()[0][0]
                        )
                        # there are cases where we get back none
                        if _previous_ingested_time == "None":
                            raise ValueError(
                                f"Couldn't find the ingested time for {table}"
                            )
                        logging.info(
                            f"{str(datetime.now())[:-3]} : Starting incremental load for {table} from {_previous_ingested_time}"
                        )
                        # query for incremental loads
                        _query = f"SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.{table} WHERE {_incremental_column} > '{_previous_ingested_time}'"
                    except Exception as err:
                        logging.warning(
                            f"{str(datetime.now())[:-3]} : Couldn't find ingestion time for {table} with incremental column {_incremental_column}. Will ingest full load"
                        )
                        # query for new load
                        _query = f"SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.{table}"
                else:
                    logging.info(
                        f"{str(datetime.now())[:-3]} : Starting full load for {table}"
                    )
                    # query for new load
                    _query = f"SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.{table}"
                    
                # FIXME : Currently check if using the data_sharing_usage schema
                if table.lower() == "listing_consumption_daily":
                  _query = _query.replace("ACCOUNT_USAGE", "DATA_SHARING_USAGE")
                
                logging.debug(
                    f"{str(datetime.now())[:-3]} : Ingesting {table} using {_query}"
                )
                # ingest table into delta
                (
                    spark.read.format("snowflake")
                    .options(**creds)
                    .option("query", _query)
                    .load()
                    .withColumn("account_url", lit(creds["sfURL"]))
                    .withColumn("ingested_time", current_timestamp())
                    .write.format("delta")
                    .option("mergeSchema", True)
                    .option("overwriteSchema", True)
                    .partitionBy("account_url")
                    .mode("append")
                    .save(f"{self._storage}/{table}")
                )
                # log that data was ingested
                _ingestion_time = str(datetime.now())[:-3]
                logging.info(f"{_ingestion_time} : Ingested {table}")
                # return the table and ingestion time
                return (creds["sfURL"], _ingestion_time, table)
            except Exception as err:
                raise ValueError(f"Failed to ingest {table}, error : {err}")

        # return the function
        return _fun

    def register(self) -> bool:
        """
        Register delta tables to views
        """

        # loop for all tables
        for _table in tables_to_ingest + ["profiler_log"]:
            try:

                # load data into a dataframe
                _df = spark.read.format("delta").load(f"{self._storage}/{_table}")

                # register table as a view
                _view_name = f"snowflake_profiler_{_table}"
                _df.createOrReplaceTempView(_view_name)

                logging.info(f"{str(datetime.now())[:-3]} : Registered {_view_name}")
                logging.debug(
                    f"{str(datetime.now())[:-3]} : Registered {_view_name} from delta table located at {self._storage}/{_table}"
                )
            except Exception as err:
                raise ValueError(
                    f"{datetime.now()} : Failed to register {_table}, err : {err}"
                )

    def ingest(self, creds: Dict[str, str]) -> bool:
        """
        Read data from Snowflake
        """

        # validate that the credentials are valid
        self.__validate_credentials(creds)

        # create the profiler log if it's not created
        self.__create_profiler_log()

        # get the function to read from snowflake
        _fun = self.__read_snowflake_factory(creds)

        # boolean to store result progress
        _results = []

        # ingest tables from snowflake in parallel
        with ThreadPoolExecutor(
            max_workers=len(tables_to_ingest)
        ) as _executor:
            # get results from the table ingestion
            for _result in _executor.map(_fun, tables_to_ingest):
                _results.append(_result)

        # update profiler log
        try:
            # write to profiler log
            (
                spark.createDataFrame(
                    data=_results, schema=["account_url", "ingested_time", "table"]
                )
                .withColumn("ingested_time", to_timestamp(col("ingested_time")))
                .write.format("delta")
                .mode("append")
                .save(f"{self._storage}/{self._log}")
            )

            # log the write
            logging.info(
                f"{datetime.now()} : Logged to profiler log at {self._storage}/{self._log}"
            )

        except Exception as err:
            raise ValueError(f"Failed to update profiler log, error : {err}")

        return True