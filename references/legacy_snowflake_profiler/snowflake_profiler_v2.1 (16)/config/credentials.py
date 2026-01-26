# Databricks notebook source
# Run this in a Databricks notebook cell to create the required secrets using the Databricks CLI.
# Replace <workspace-url> with your Databricks workspace URL.

# 1. Create the secret scope
# Run in terminal or %sh cell:
# databricks secrets create-scope --scope snowflake-profiler

# 2. Add secrets to the scope
# Run in terminal or %sh cell:
# databricks secrets put-secret --scope snowflake-profiler --key url --string-value "<YOUR_SNOWFLAKE_URL>"
# databricks secrets put-secret --scope snowflake-profiler --key username --string-value "<YOUR_USERNAME>"
# databricks secrets put-secret --scope snowflake-profiler --key password --string-value "<YOUR_PASSWORD>"

# COMMAND ----------

# MAGIC %sh
# MAGIC databricks secrets create-scope --scope snowflake-profiler

# COMMAND ----------

# MAGIC %sh
# MAGIC databricks secrets put-secret --scope snowflake-profiler --key url --string-value "<YOUR_SNOWFLAKE_URL>"
# MAGIC databricks secrets put-secret --scope snowflake-profiler --key username --string-value "<YOUR_USERNAME>"
# MAGIC databricks secrets put-secret --scope snowflake-profiler --key password --string-value "<YOUR_PASSWORD>"

# COMMAND ----------

"""
Enter credentials here
credentials : {"sfURL"       : "<YOUR_SNOWFLAKE_URL>",
               "sfUser"      : "<YOUR_USERNAME>",
               "sfPassword"  : "<YOUR_PASSWORD>",
               "sfDatabase"  : "<YOUR_DATABASE>",
               "sfSchema"    : "<YOUR_SCHEMA>",
               "sfWarehouse" : "<YOUR_WAREHOUSE>"}
"""

# snowflake connection information
#  include the 'https://' as in "sfUrl": "https://snowflake_username.snowflakecomputing.com"
creds = [
    {
        "sfURL": "https://your-account.snowflakecomputing.com",
        "sfUser": "YOUR_USERNAME",
        "sfPassword": "YOUR_PASSWORD_OR_TOKEN",
        "sfDatabase": "SNOWFLAKE",
        "sfSchema": "ACCOUNT_USAGE",
        "sfWarehouse": "YOUR_WAREHOUSE",
        "sfRole": "ACCOUNTADMIN",
    }
]

# COMMAND ----------


"""
Setup logging and initial parameters
"""

import os
import logging

# storage location for delta files
storage = "/Volumes/snowflake_profiler/default/storage_spot"

# create storage if it doesn't exist
try:
    dbutils.fs.mkdirs(storage)
except Exception as err:
    print(f"Failed to make directory, err: {err}")

# set the logging level
logging.getLogger().setLevel(logging.INFO)
# logging.getLogger().setLevel(logging.WARN)
# logging.getLogger().setLevel(logging.DEBUG)