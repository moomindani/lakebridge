# Snowflake Assessment Demo

This demo demonstrates the complete Snowflake assessment workflow using the Lakebridge methodology, extracting comprehensive operational data from Snowflake's ACCOUNT_USAGE schema and storing it in DuckDB for analysis.

## Features

✅ **Password/Token Authentication**
- Simple, reliable username/password authentication
- Works with personal access tokens

✅ **Comprehensive Data Extraction**
- Query History (last 90 days)
- Warehouse Usage and Credits (90-day lookback)
- Storage Usage by Database (90-day history)
- User Login History (90-day activity)

✅ **DuckDB Integration**
- Automatic timestamped database creation
- Structured table schemas
- Ready for analytics and reporting

## Requirements

Install required packages:
```bash
pip install snowflake-connector-python pandas duckdb
```

## Usage

```bash
python demo.py
```

The demo will:
1. Prompt for Snowflake connection details
2. Test connection and ACCOUNT_USAGE access
3. Extract comprehensive assessment data
4. Save results to timestamped DuckDB file
5. Display summary analytics

## Output

Creates a DuckDB file named `snowflake_lakebridge_assessment_YYYYMMDD_HHMMSS.db` containing:

- `snowflake_query_history`: SQL queries with execution metrics
- `snowflake_warehouse_usage`: Credit consumption and usage patterns  
- `snowflake_storage_usage`: Storage consumption over time
- `snowflake_user_activity`: Login history and authentication events

## Fallback Mode

If ACCOUNT_USAGE access is not available, the demo automatically falls back to basic information queries that work with standard permissions:

- Basic account information
- Current session context  
- Available databases, warehouses, and roles

## Example Output

```
📊 Lakebridge Snowflake Assessment Summary:
✅ Successful extracts: 4/4
💾 Results saved to: snowflake_lakebridge_assessment_20251230_185404.db

📋 Created 4 assessment tables:
   - snowflake_query_history: 100 rows
   - snowflake_storage_usage: 7 rows
   - snowflake_user_activity: 72 rows
   - snowflake_warehouse_usage: 2 rows

📈 Total assessment data: 181 rows
```

This provides the same comprehensive data collection as the full Lakebridge platform, ready for analysis and reporting.