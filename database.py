import sqlite3 as sql
import pandas as pd

def connect_db(db_name): 
    return sql.connect(db_name)

def SQL_acquisition(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])
    return df
    
def verify_total_steps(df, connection):
    df_database = SQL_acquisition(connection, f"SELECT Id, sum(StepTotal) AS total_steps FROM hourly_steps GROUP BY Id")
    df_csv = df.groupby('Id')['TotalSteps'].sum().reset_index()

    identical = df_database['total_steps'].equals(df_csv['TotalSteps'])
    print("If the total steps in csv file is indentical as in database?:", identical) 

def safe_sql_query(connection, query, params=None):
    try:
        df = SQL_acquisition(connection, query)
        return df
    except Exception as e:
        print(f"An error occurred while executing the SQL query: {e}")
        return pd.DataFrame()
    
def compute_sleep_duration(connection):
    query = """
        SELECT Id, logId, COUNT(*) AS SleepDuration
        FROM minute_sleep
        GROUP BY Id, logId
        ORDER BY Id, logId
    """
    df_sleep = safe_sql_query(connection, query)

    if df_sleep.empty:
        print("No sleep data found in database.")
        return pd.DataFrame()
    
    df_sleep["logId"] = df_sleep["logId"].astype(str)
    df_sleep["Id"] = df_sleep["Id"].astype(str)
    print("Computed Sleep Duration per User and Session:")
    print(df_sleep.head(10))

    return df_sleep