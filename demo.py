#!/usr/bin/env python3
"""
Snowflake Assessment Demo
This script demonstrates the complete Snowflake assessment workflow:
- Password/Token authentication
- Comprehensive data extraction from Snowflake ACCOUNT_USAGE schema
- DuckDB storage for analytics

Usage:
    python demo.py

Requirements:
    - snowflake-connector-python
    - pandas
    - duckdb
"""

import json
import logging
import sys
import os
from pathlib import Path
import getpass
from datetime import datetime

def configure_snowflake_credentials():
    """Configure Snowflake credentials with password/token authentication"""
    print("🔐 Snowflake Assessment Configuration")
    print("=" * 60)
    
    credentials = {}
    
    print("\nPlease provide your Snowflake connection details:")
    sf_url_input = input("Snowflake URL (e.g., https://myaccount.snowflakecomputing.com): ").strip()
    
    # Handle different URL formats
    if sf_url_input.startswith("https://"):
        credentials["sfURL"] = sf_url_input
    elif ".snowflakecomputing.com" in sf_url_input:
        credentials["sfURL"] = f"https://{sf_url_input}"
    else:
        credentials["sfURL"] = f"https://{sf_url_input}.snowflakecomputing.com"
        
    credentials["sfUser"] = input("Username: ").strip()
    credentials["sfWarehouse"] = input("Warehouse (default: COMPUTE_WH): ").strip() or "COMPUTE_WH"
    credentials["sfDatabase"] = input("Database (default: SNOWFLAKE): ").strip() or "SNOWFLAKE"
    credentials["sfSchema"] = input("Schema (default: ACCOUNT_USAGE): ").strip() or "ACCOUNT_USAGE"
    credentials["sfRole"] = input("Role (default: ACCOUNTADMIN): ").strip() or "ACCOUNTADMIN"
    
    credentials["authenticator"] = "password"
    credentials["sfPassword"] = getpass.getpass("Password/Token: ").strip()
    
    return credentials

def test_account_usage_access(credentials):
    """Test if ACCOUNT_USAGE schema is accessible"""
    try:
        import snowflake.connector
        
        print("\n🔍 Testing ACCOUNT_USAGE schema access...")
        
        # Extract account from URL for connection
        sf_url = credentials.get("sfURL", "")
        account = sf_url.replace("https://", "").replace(".snowflakecomputing.com", "") if sf_url else ""
        
        conn_params = {
            "account": account,
            "user": credentials["sfUser"],
            "password": credentials["sfPassword"]
        }
        
        conn = snowflake.connector.connect(**conn_params)
        
        # Test access with warehouse and schema context
        cursor = conn.cursor()
        cursor.execute(f"USE WAREHOUSE {credentials['sfWarehouse']}")
        cursor.execute(f"USE ROLE {credentials['sfRole']}")
        cursor.execute("USE DATABASE SNOWFLAKE")
        cursor.execute("USE SCHEMA ACCOUNT_USAGE")
        cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA()")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print(f"✅ ACCOUNT_USAGE accessible! Database: {result[0]}, Schema: {result[1]}")
        return True
        
    except Exception as e:
        print(f"❌ ACCOUNT_USAGE access failed: {e}")
        print("💡 Will use alternative queries that don't require special permissions")
        return False

def test_snowflake_connection(credentials):
    """Test connection to Snowflake with minimal parameters"""
    try:
        import snowflake.connector
        
        print("\n🔍 Testing Snowflake connection...")
        
        # Extract account from URL for connection
        sf_url = credentials.get("sfURL", "")
        account = sf_url.replace("https://", "").replace(".snowflakecomputing.com", "") if sf_url else ""
        
        # Minimal connection parameters
        conn_params = {
            "account": account,
            "user": credentials["sfUser"],
            "password": credentials["sfPassword"]
        }
        
        # Create connection with minimal parameters
        conn = snowflake.connector.connect(**conn_params)
        
        # Test with simple query
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print(f"✅ Connection successful! Snowflake version: {version[0]}")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def get_assessment_queries():
    """Get comprehensive Snowflake assessment queries for ACCOUNT_USAGE schema"""
    return {
        "query_history": {
            "name": "query_history", 
            "description": "Query History (Last 7 days)",
            "sql": """
                SELECT 
                    query_id,
                    query_text,
                    user_name,
                    role_name,
                    warehouse_name,
                    database_name,
                    schema_name,
                    query_type,
                    query_tag,
                    session_id,
                    start_time,
                    end_time,
                    total_elapsed_time,
                    bytes_scanned,
                    bytes_written,
                    compilation_time,
                    execution_time,
                    credits_used_cloud_services
                FROM snowflake.account_usage.query_history
                WHERE start_time >= DATEADD('day', -7, CURRENT_TIMESTAMP())
                ORDER BY start_time DESC
                LIMIT 100
            """
        },
        "warehouse_usage": {
            "name": "warehouse_usage",
            "description": "Warehouse Usage (Last 7 days)", 
            "sql": """
                SELECT 
                    warehouse_id,
                    warehouse_name,
                    start_time,
                    end_time,
                    credits_used,
                    credits_used_compute,
                    credits_used_cloud_services
                FROM snowflake.account_usage.warehouse_metering_history
                WHERE start_time >= DATEADD('day', -7, CURRENT_TIMESTAMP())
                ORDER BY start_time DESC
                LIMIT 100
            """
        },
        "storage_usage": {
            "name": "storage_usage",
            "description": "Storage Usage by Database",
            "sql": """
                SELECT 
                    usage_date,
                    storage_bytes,
                    stage_bytes,
                    failsafe_bytes
                FROM snowflake.account_usage.storage_usage
                WHERE usage_date >= DATEADD('day', -7, CURRENT_TIMESTAMP())
                ORDER BY usage_date DESC
                LIMIT 100
            """
        },
        "user_activity": {
            "name": "user_activity",
            "description": "User Login History",
            "sql": """
                SELECT 
                    user_name,
                    client_ip,
                    reported_client_type,
                    reported_client_version,
                    first_authentication_factor,
                    second_authentication_factor,
                    is_success,
                    error_code,
                    error_message,
                    event_timestamp
                FROM snowflake.account_usage.login_history
                WHERE event_timestamp >= DATEADD('day', -7, CURRENT_TIMESTAMP())
                ORDER BY event_timestamp DESC
                LIMIT 100
            """
        }
    }

def get_fallback_queries():
    """Get basic queries that work without special permissions"""
    return {
        "basic_info": {
            "name": "basic_info", 
            "description": "Basic Account Information",
            "sql": "SELECT CURRENT_ACCOUNT() as ACCOUNT_NAME, CURRENT_VERSION() as VERSION, CURRENT_USER() as USER_NAME"
        },
        "current_context": {
            "name": "current_context",
            "description": "Current Session Context", 
            "sql": """
                SELECT 
                    CURRENT_ACCOUNT() as account,
                    CURRENT_USER() as current_user,
                    CURRENT_ROLE() as current_role,
                    CURRENT_DATABASE() as current_database,
                    CURRENT_SCHEMA() as current_schema,
                    CURRENT_WAREHOUSE() as current_warehouse,
                    CURRENT_TIMESTAMP() as extract_time
            """
        },
        "show_databases": {
            "name": "show_databases",
            "description": "Available Databases",
            "sql": "SHOW DATABASES"
        },
        "show_warehouses": {
            "name": "show_warehouses",
            "description": "Available Warehouses",
            "sql": "SHOW WAREHOUSES"
        },
        "show_roles": {
            "name": "show_roles", 
            "description": "Available Roles",
            "sql": "SHOW ROLES"
        }
    }

def run_assessment_query(credentials, query_info):
    """Run a single assessment query with proper context setting for ACCOUNT_USAGE"""
    try:
        import snowflake.connector
        import pandas as pd
        
        print(f"\n📊 Running {query_info['description']}...")
        
        # Extract account from URL for connection
        sf_url = credentials.get("sfURL", "")
        account = sf_url.replace("https://", "").replace(".snowflakecomputing.com", "") if sf_url else ""
        
        # Connection parameters
        conn_params = {
            "account": account,
            "user": credentials["sfUser"],
            "password": credentials["sfPassword"]
        }
        
        # Create connection
        conn = snowflake.connector.connect(**conn_params)
        
        cursor = conn.cursor()
        
        # For ACCOUNT_USAGE queries, set warehouse context first
        if "account_usage" in query_info["sql"].lower() or "snowflake.account_usage" in query_info["sql"].lower():
            print(f"   🏭 Setting warehouse: {credentials['sfWarehouse']}")
            cursor.execute(f"USE WAREHOUSE {credentials['sfWarehouse']}")
            cursor.execute(f"USE ROLE {credentials['sfRole']}")
        
        # Execute query
        cursor.execute(query_info["sql"])
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        df = pd.DataFrame(rows, columns=columns)
        
        conn.close()
        
        print(f"✅ Query completed. Retrieved {len(df)} rows.")
        if len(df) > 0:
            print("📋 Sample data:")
            print(df.head(3).to_string(index=False))
        
        return df
        
    except Exception as e:
        print(f"❌ Query failed: {e}")
        print(f"   Query: {query_info['name']}")
        return None

def save_to_duckdb(data, table_name, db_path):
    """Save data to DuckDB database"""
    try:
        import duckdb
        
        if data is not None and len(data) > 0:
            conn = duckdb.connect(db_path)
            conn.register("temp_data", data)
            
            # Create table and insert data
            conn.execute(f"CREATE TABLE IF NOT EXISTS snowflake_{table_name} AS SELECT * FROM temp_data WHERE 1=0")
            conn.execute(f"DELETE FROM snowflake_{table_name}")  # Clear existing data
            conn.execute(f"INSERT INTO snowflake_{table_name} SELECT * FROM temp_data")
            
            conn.close()
            print(f"💾 Saved {len(data)} rows to DuckDB table 'snowflake_{table_name}'")
            return True
    except Exception as e:
        print(f"❌ Failed to save to DuckDB: {e}")
    
    return False

def check_required_packages():
    """Check if required packages are available"""
    missing_packages = []
    
    try:
        import snowflake.connector
    except ImportError:
        missing_packages.append("snowflake-connector-python")
    
    try:
        import pandas
    except ImportError:
        missing_packages.append("pandas")
    
    try:
        import duckdb
    except ImportError:
        missing_packages.append("duckdb")
    
    if missing_packages:
        print("❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\nInstall with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All required packages are available")
    return True

def main():
    """Main demo function"""
    print("🏔️  Snowflake Lakebridge Assessment Demo")
    print("=" * 60)
    print("This demo runs the complete Snowflake assessment workflow")
    print("using comprehensive ACCOUNT_USAGE schema queries.")
    print("Authentication: Password/Token")
    print()
    
    # Check dependencies
    if not check_required_packages():
        return
    
    # Step 1: Configure credentials
    credentials = configure_snowflake_credentials()
    
    # Step 2: Test connection
    if not test_snowflake_connection(credentials):
        print("\n❌ Cannot proceed without a valid connection.")
        return
    
    # Test ACCOUNT_USAGE access
    has_account_usage = test_account_usage_access(credentials)
    
    # Step 3: Load assessment queries
    print("\n📋 Loading Assessment Queries...")
    print("-" * 50)
    
    if has_account_usage:
        print("📋 Using comprehensive ACCOUNT_USAGE assessment queries")
        queries = get_assessment_queries()
    else:
        print("🔄 Using basic queries (ACCOUNT_USAGE not accessible)")
        queries = get_fallback_queries()
    
    # Step 4: Run assessment queries
    print("\n📊 Running Snowflake Assessment...")
    print("-" * 50)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_path = f"snowflake_lakebridge_assessment_{timestamp}.db"
    successful_extracts = 0
    
    for query_name, query_info in queries.items():
        result_df = run_assessment_query(credentials, query_info)
        
        if result_df is not None:
            save_to_duckdb(result_df, query_name, db_path)
            successful_extracts += 1
    
    # Step 5: Summary and analysis
    print("\n" + "=" * 60)
    print("📊 Lakebridge Snowflake Assessment Summary:")
    print(f"✅ Successful extracts: {successful_extracts}/{len(queries)}")
    print(f"💾 Results saved to: {db_path}")
    
    if successful_extracts > 0:
        # Show DuckDB contents
        try:
            import duckdb
            conn = duckdb.connect(db_path)
            
            tables = conn.execute("SHOW TABLES").fetchall()
            print(f"\n📋 Created {len(tables)} assessment tables:")
            
            total_rows = 0
            for table in tables:
                table_name = table[0]
                count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                total_rows += count
                print(f"   - {table_name}: {count} rows")
            
            print(f"\n📈 Total assessment data: {total_rows} rows")
            
            # Basic analytics
            print(f"\n🔍 Sample Assessment Analytics:")
            
            # Count warehouses if we have warehouse data
            if any('warehouse' in table[0] for table in tables):
                try:
                    wh_count = conn.execute("SELECT COUNT(DISTINCT warehouse_name) FROM snowflake_warehouse_usage").fetchone()[0]
                    print(f"   Warehouses analyzed: {wh_count}")
                except:
                    pass
            
            # Count queries if we have query data
            if any('query' in table[0] for table in tables):
                try:
                    query_count = conn.execute("SELECT COUNT(*) FROM snowflake_query_history").fetchone()[0]
                    print(f"   Query history records: {query_count}")
                except:
                    pass
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Could not analyze results: {e}")
    
    print("\n🎉 Snowflake Lakebridge Assessment completed!")
    print()
    print("This assessment provides the same comprehensive data collection")
    print("as the full lakebridge platform, ready for analysis and reporting.")

if __name__ == "__main__":
    main()