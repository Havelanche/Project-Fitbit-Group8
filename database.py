import sqlite3 as sql
import pandas as pd

# db_name="fitbit_database.db"

def connect_db(db_name): 
    return sql.connect(db_name)

def SQL_acquisition(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])
    return df

def show_table_columns(connection, table_name):
    query = f"PRAGMA table_info({table_name})"
    df = SQL_acquisition(connection, query)
    print(f"Columns in {table_name}:", df['name'].tolist())
    
def show_all_tables(connection):
    try:
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        df = SQL_acquisition(connection, query)
        print("Tables in database:", df['name'].tolist())
    except Exception as e:
        print(f"Error fetching tables: {e}")

    
def verify_total_steps(df, connection):
    df_database = SQL_acquisition(connection, f"SELECT Id, sum(StepTotal) AS total_steps FROM hourly_steps GROUP BY Id")
    df_csv = df.groupby('Id')['TotalSteps'].sum().reset_index()

    identical = df_database['total_steps'].equals(df_csv['TotalSteps'])
    print("If the total steps in csv file is indentical as in database?:", identical)
    