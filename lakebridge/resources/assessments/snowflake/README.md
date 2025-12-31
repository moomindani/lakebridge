# Enhanced Snowflake Assessment Module

This module provides comprehensive profiling and analysis capabilities for Snowflake data warehouses, migrated from the legacy PySpark-based profiler to a local CLI tool with enhanced user experience and testing capabilities.

## 🚀 Enhanced Features (NEW)

- **Interactive Launcher**: Easy-to-use menu system for all assessment capabilities
- **Enhanced UX Script**: Guided workflow with improved user experience and colored output
- **Standalone Demo**: Run assessments without full lakebridge setup
- **Comprehensive Testing**: Complete test suite for validation and troubleshooting
- **Better Error Handling**: Enhanced connection testing and validation
- **Multiple Execution Modes**: Choose between demo, full assessment, or guided workflow

## 🎯 Core Assessment Features

- **Account Usage Extraction**: Basic account metadata (databases, tables, views, functions, procedures, etc.)
- **Warehouse Analysis**: Warehouse usage patterns, load history, and performance metrics  
- **Query Analysis**: Query history, access patterns, login history, and query acceleration metrics
- **Cost Analysis**: Metering history, storage usage, data transfer costs, and credit rate calculation

## Architecture

The migration follows these key principles:

- **No PySpark**: All Spark/RDD logic converted to standard Python and SQL
- **Local Execution**: Runs on user's machine using `snowflake-connector-python`
- **DuckDB Storage**: Results stored in local `profiler_extract.db` file
- **Token Authentication**: Supports Snowflake JWT tokens and passwords

## Files Structure

```
snowflake/
├── __init__.py                     # Module initialization
├── pipeline_config.yml             # Pipeline configuration
├── account_usage_extract.py        # Basic account metadata extraction
├── warehouse_analysis.py           # Warehouse usage analysis
├── query_analysis.py              # Query performance analysis  
├── cost_analysis.py               # Cost and usage analysis
└── extracts/                      # SQL query files
    ├── databases.sql
    ├── tables.sql
    ├── views.sql
    ├── warehouse_metering_history.sql
    ├── query_history.sql
    └── access_history.sql
```

## Usage

### 🆕 Enhanced Usage (Recommended)

#### Interactive Launcher
```bash
# Start the interactive menu
python launcher.py

# Available options:
# 1. Quick Demo - No setup required
# 2. Full Assessment - Complete lakebridge integration  
# 3. Configuration - Set up credentials
# 4. Test Suite - Validate installation
# 5. Analyze Results - Explore assessment data
```

#### Command Line Options
```bash
# Quick demo assessment (standalone)
python launcher.py --demo

# Full guided assessment
python launcher.py --full  

# Configuration setup only
python launcher.py --config

# Run comprehensive tests
python launcher.py --test
```

#### Enhanced UX Script
```bash
# Guided workflow with enhanced UX
python ux.py

# Demo mode with enhanced output
python ux.py --demo

# Quick assessment workflow
python ux.py --quick
```

### 🔧 Traditional Usage

1. **Configuration**: Use `ConfigureSnowflakeAssessment` to set up credentials with token-based authentication

2. **Execution**: The pipeline runs the following steps:
   - Account usage extraction (static metadata)
   - Warehouse analysis (performance metrics)
   - Query analysis (usage patterns)
   - Cost analysis (billing and storage)

3. **Output**: All results stored in DuckDB `profiler_extract.db` with table names prefixed `snowflake_`

## Migration Notes

This module preserves the business logic from the legacy `snowflake_profiler_v2.1` while converting:

- PySpark DataFrames → Pandas DataFrames + DuckDB
- Databricks storage → Local DuckDB file
- Cluster execution → Local client execution
- Legacy authentication → Token-based authentication

## Dependencies

- `snowflake-connector-python`
- `sqlalchemy-snowflake` 
- `pandas`
- `duckdb`
- `databricks-labs-blueprint`