-- Warehouse Usage and Performance Analysis
-- Extract warehouse utilization metrics and performance data

SELECT 
    WAREHOUSE_NAME,
    WAREHOUSE_SIZE,
    START_TIME,
    END_TIME,
    CREDITS_USED,
    CREDITS_USED_COMPUTE,
    CREDITS_USED_CLOUD_SERVICES,
    DATE(START_TIME) as USAGE_DATE,
    HOUR(START_TIME) as USAGE_HOUR,
    EXTRACT(dayofweek FROM START_TIME) as DAY_OF_WEEK,
    CURRENT_TIMESTAMP() as EXTRACT_TIMESTAMP
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD('day', -{lookback_days}, CURRENT_TIMESTAMP())
    AND CREDITS_USED > 0
ORDER BY START_TIME DESC;

-- Note: {lookback_days} will be replaced with the configured lookback period