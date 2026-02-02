#!/usr/bin/env python3
"""
Script to remove all sensitive credentials from git history.
This will rewrite all commits to replace sensitive data with placeholder values.
"""

import re
import sys

def clean_content(content):
    """Replace all sensitive information with placeholders"""
    
    # Replace the specific exposed credentials
    replacements = [
        # Snowflake URLs
        (r'https://IKSJSZD-ZAB08105\.snowflakecomputing\.com', '<YOUR_SNOWFLAKE_URL>'),
        # Username
        (r'JWNEIL', '<YOUR_USERNAME>'),
        # Password
        (r'Yankees!7', '<YOUR_PASSWORD>'),
        # Database
        (r'"SNOWFLAKE"', '"<YOUR_DATABASE>"'),
        # Schema (but be careful not to replace legitimate usage)
        (r'"ACCOUNT_USAGE"', '"<YOUR_SCHEMA>"'),
        # Warehouse
        (r'BANANAPUDDING', '<YOUR_WAREHOUSE>'),
    ]
    
    result = content
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    return result

if __name__ == "__main__":
    # Read from stdin
    content = sys.stdin.read()
    
    # Clean the content
    cleaned = clean_content(content)
    
    # Write to stdout
    sys.stdout.write(cleaned)