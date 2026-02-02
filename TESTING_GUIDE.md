# Snowflake Lakebridge Integration Testing Guide

This document provides a comprehensive guide for testing the complete Snowflake profiler workflow with the Lakebridge framework.

## 🎯 Overview

The Snowflake profiler is **fully integrated** with the Lakebridge framework and follows the official documented workflow. You have two approaches:

1. **[Recommended] Official Lakebridge Workflow** - Complete integration with CLI commands
2. **Standalone Demo** - Independent script for testing/development

## ✅ Integration Test Results

All integration tests are passing:

- ✅ Profiler configuration files exist and are valid
- ✅ Snowflake is listed as a supported source system  
- ✅ Profiler framework imports and creation work correctly
- ✅ Demo and profiler use compatible DuckDB output formats
- ✅ Configuration workflow is properly implemented
- ✅ Dependencies are properly installed

## 🚀 Testing the Official Lakebridge Workflow

### Prerequisites

1. **Install dependencies**:
   ```bash
   pip install snowflake-connector-python snowflake-sqlalchemy
   ```

2. **Valid Databricks workspace access** (for dashboard creation)

3. **Snowflake account with ACCOUNT_USAGE access**

### Step 1: Configure Snowflake Connection

```bash
databricks labs lakebridge configure-database-profiler
```

This will:
- Prompt you to select "snowflake" as the source system
- Ask for Snowflake connection details:
  - Account URL (e.g., `mycompany.snowflakecomputing.com`)
  - Username 
  - Password/Token
  - Warehouse (default: `COMPUTE_WH`)
  - Database (default: `SNOWFLAKE`)
  - Schema (default: `ACCOUNT_USAGE`) 
  - Role (default: `ACCOUNTADMIN`)
- Save credentials securely for the profiler

### Step 2: Execute Profiler

```bash
databricks labs lakebridge execute-database-profiler --source-tech snowflake
```

This will:
- Connect to Snowflake using saved credentials
- Execute comprehensive assessment queries:
  - Account information
  - Database objects and metadata
  - Warehouse usage (90-day lookback)
  - Query history (90-day lookback)
  - Storage usage statistics
  - User activity logs
- Save results to a DuckDB database file
- Generate execution summary

### Step 3: Create Dashboard (Optional)

```bash
databricks labs lakebridge create-profiler-dashboard \
  --extract-file ./output/profiler_results.db \
  --source-tech snowflake \
  --uc-volume /Volumes/lakebridge_profiler/profiler_runs \
  --catalog-name lakebridge_profiler \
  --schema-name profiler_runs
```

This will:
- Upload the profiler extract file to Unity Catalog volume
- Create and execute a Databricks job to ingest the data
- Convert results to Delta tables
- Deploy a summary dashboard
- Return the dashboard URL

## 🧪 Alternative: Standalone Demo Testing

If you want to test without the full Lakebridge infrastructure:

```bash
python demo.py
```

This provides:
- Interactive credential configuration
- Connection testing
- Comprehensive ACCOUNT_USAGE queries
- DuckDB output compatible with profiler framework
- Fallback queries for limited permissions

## 📊 Expected Output

### Profiler Tables Created

The profiler extracts data into these tables:
- `account_info` - Basic account metadata
- `database_objects` - Schema, tables, views, functions
- `warehouse_usage` - Compute usage and costs
- `query_history` - Query execution metrics
- `storage_usage` - Storage consumption
- `user_activity` - Authentication and access logs

### Output Location

- **Development**: `./output/snowflake_assessment_YYYYMMDD_HHMMSS.db`
- **Lakebridge**: Configured output location (typically `/tmp/data/snowflake_assessment`)

### Dashboard Contents

The generated dashboard includes:
- Warehouse utilization trends
- Query performance metrics  
- User activity patterns
- Storage consumption analysis
- Cost optimization insights

## 🔧 Troubleshooting

### Common Issues

1. **"Configuration file not found"**
   - Run in development mode: Configuration files are in source tree
   - For installed mode: Ensure proper installation with `pip install -e .`

2. **"Invalid access token"** 
   - Configure Databricks CLI: `databricks configure`
   - Ensure valid workspace access

3. **Snowflake connection fails**
   - Verify account URL format
   - Check user permissions for ACCOUNT_USAGE schema
   - Ensure role has necessary privileges

4. **No data returned**
   - User may not have ACCOUNT_USAGE access
   - Try with ACCOUNTADMIN role
   - Check warehouse is running

### Required Permissions

For comprehensive assessment, the user needs:
- USAGE on SNOWFLAKE database
- USAGE on ACCOUNT_USAGE schema  
- SELECT on all ACCOUNT_USAGE views
- ACCOUNTADMIN role (recommended)

## 📋 Testing Checklist

- [ ] Dependencies installed (`snowflake-connector-python`, `snowflake-sqlalchemy`)
- [ ] Lakebridge installed in development mode (`pip install -e .`)
- [ ] Databricks CLI configured (for dashboard creation)
- [ ] Snowflake credentials with ACCOUNT_USAGE access
- [ ] Integration tests pass (`python test_snowflake_integration.py`)
- [ ] Configure profiler completes successfully
- [ ] Execute profiler completes with data
- [ ] Dashboard creation works (optional)

## 🎯 Next Steps

1. **Production Deployment**: Test with your actual Snowflake environment
2. **CI/CD Integration**: Add profiler execution to your automation pipeline  
3. **Scheduling**: Set up regular profiling runs to track changes
4. **Custom Queries**: Extend with environment-specific assessment queries
5. **Dashboard Customization**: Modify dashboard templates for your needs

## 📚 Related Documentation

- [Official Lakebridge Profiler Guide](https://databrickslabs.github.io/lakebridge/docs/assessment/profiler/)
- [Snowflake ACCOUNT_USAGE Documentation](https://docs.snowflake.com/en/sql-reference/account-usage.html)
- [Databricks Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)