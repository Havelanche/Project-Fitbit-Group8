import sqlite3

import pandas as pd
from csv_data_wrangling import load_and_preview_data, clean_and_transform_data, summarize_data
from database import SQL_acquisition

DATA_FILE =  'daily_activity_copy.csv'
DB_NAME = 'fitbit_database.db'

def inspect_database(db_name):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # List all tables
    print("\n Tables in the Database:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(f" - {table[0]}")

    # Preview first 5 rows of each table
    for table in tables:
        table_name = table[0]
        print(f"\n Preview of '{table_name}' (first 5 rows):")
        query = f"SELECT * FROM {table_name} LIMIT 5;"
        df = pd.read_sql_query(query, connection)
        print(df)

    connection.close()
    
connection = sqlite3.connect(DB_NAME)
    
print("\n Unique IDs in daily_activity:")
query = "SELECT DISTINCT Id FROM daily_activity"
daily_activity_ids = SQL_acquisition(connection, query)
print(daily_activity_ids)

print("\n Unique IDs in minute_sleep:")
query = "SELECT DISTINCT Id FROM minute_sleep"
minute_sleep_ids = SQL_acquisition(connection, query)
print(minute_sleep_ids)

print("\n Unique IDs in weight_log:")
query = "SELECT DISTINCT Id FROM weight_log"
weight_log_ids = SQL_acquisition(connection, query)
print(weight_log_ids)

# Check mismatches
daily_ids = set(daily_activity_ids['Id'])
sleep_ids = set(minute_sleep_ids['Id'])
weight_ids = set(weight_log_ids['Id'])

print("\n IDs present in daily_activity but not in minute_sleep:")
print(daily_ids - sleep_ids)

print("\n IDs present in daily_activity but not in weight_log:")
print(daily_ids - weight_ids)

def main():
    cleaned_data = load_and_preview_data(DATA_FILE)
    cleaned_data = clean_and_transform_data(cleaned_data)
    summarize_data(cleaned_data) 
    inspect_database(DB_NAME)
    
    

if __name__ == '__main__':
    main()
