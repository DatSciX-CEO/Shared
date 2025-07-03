/*
====================================================================================================
    Data Discovery Script for DuckDB (Final, High-Compatibility Version)
====================================================================================================
    Description: This script uses a regex pattern designed for maximum compatibility with SQL
                 clients by avoiding special characters that can be misinterpreted as parameter
                 markers (like '?' and ':').

    Author:      Gemini
    Date:        July 03, 2025

    Instructions:
    1.  This is a direct query. Copy and paste it into your DuckDB client.
    2.  Replace 'your_table' and 'your_column_name' with your actual table and column names.
    3.  Execute the query to find potential credential data.
====================================================================================================
*/

SELECT
    your_column_name AS MatchedText
FROM
    your_table
WHERE
    regexp_matches(
        your_column_name,
        -- This regex avoids '?' and ':' characters for maximum client compatibility.
        '(?i)((\\b(pw|password|username|log\\s*in|log\\s*on)\\b\\W*).*(^|\\s)\\S{1,15}($|\\s)|(^|\\s)\\S{1,15}($|\\s).*(\\b(pw|password|username|log\\s*in|log\\s*on)\\b\\W*))'
    )
    
