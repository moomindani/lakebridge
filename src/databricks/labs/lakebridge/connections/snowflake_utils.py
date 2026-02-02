"""
Snowflake utility functions for account URL parsing and connection handling.
"""


def parse_snowflake_account(account_input: str) -> str:
    """
    Parse Snowflake account identifier from various input formats.
    
    Users typically copy one of these formats from Snowflake console:
    - IKSJSZD-ZAB08105.snowflakecomputing.com
    - https://IKSJSZD-ZAB08105.snowflakecomputing.com
    - IKSJSZD-ZAB08105 (just the identifier)
    
    Returns the clean account identifier needed for connections.
    
    Args:
        account_input: Raw account URL or identifier from user
        
    Returns:
        Clean account identifier (e.g., IKSJSZD-ZAB08105)
    """
    if not account_input:
        return ""
    
    # Remove https:// prefix if present
    account = account_input.replace("https://", "")
    
    # Remove .snowflakecomputing.com suffix if present  
    account = account.replace(".snowflakecomputing.com", "")
    
    # Remove any path components (everything after first /)
    if "/" in account:
        account = account.split("/")[0]
    
    # Remove trailing slashes
    account = account.rstrip("/")
    
    return account


def validate_snowflake_account(account_identifier: str) -> bool:
    """
    Basic validation of Snowflake account identifier format.
    
    Args:
        account_identifier: Clean account identifier
        
    Returns:
        True if format appears valid, False otherwise
    """
    if not account_identifier:
        return False
    
    # Snowflake account identifiers typically contain letters, numbers, and hyphens
    # They cannot be empty and should not contain spaces or special characters
    import re
    pattern = r'^[A-Za-z0-9\-_]+$'
    return bool(re.match(pattern, account_identifier))


def build_snowflake_url(account: str, user: str, password: str = None, 
                       warehouse: str = "COMPUTE_WH", database: str = "SNOWFLAKE",
                       schema: str = "ACCOUNT_USAGE", role: str = "ACCOUNTADMIN",
                       authenticator: str = "password") -> str:
    """
    Build SQLAlchemy connection URL for Snowflake.
    
    Args:
        account: Snowflake account identifier (parsed)
        user: Username
        password: Password/token (optional for external auth)
        warehouse: Warehouse name
        database: Database name  
        schema: Schema name
        role: Role name
        authenticator: Authentication method
        
    Returns:
        SQLAlchemy connection URL
    """
    # Clean the account identifier
    clean_account = parse_snowflake_account(account)
    
    if authenticator == "externalbrowser":
        # For external browser authentication, don't include password in URL
        url = (
            f"snowflake://{user}@{clean_account}/"
            f"{database}/{schema}?warehouse={warehouse}&role={role}&authenticator=externalbrowser"
        )
    else:
        # For password authentication
        if not password:
            raise ValueError("Password is required for password authentication")
        url = (
            f"snowflake://{user}:{password}@{clean_account}/"
            f"{database}/{schema}?warehouse={warehouse}&role={role}"
        )
    
    return url


# Example usage and test cases
if __name__ == "__main__":
    # Test cases for account parsing
    test_cases = [
        "IKSJSZD-ZAB08105.snowflakecomputing.com",
        "https://IKSJSZD-ZAB08105.snowflakecomputing.com",
        "https://IKSJSZD-ZAB08105.snowflakecomputing.com/",
        "IKSJSZD-ZAB08105",
        "mycompany.snowflakecomputing.com",
        "https://mycompany.snowflakecomputing.com/console/login",
    ]
    
    print("Testing Snowflake account parsing:")
    for test_input in test_cases:
        parsed = parse_snowflake_account(test_input)
        valid = validate_snowflake_account(parsed)
        print(f"  Input: {test_input}")
        print(f"  Parsed: {parsed}")
        print(f"  Valid: {valid}")
        print()