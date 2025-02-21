import sqlite3 as sql
import pandas as pd

db_name="fitbit_database.db"

def connect_db(db_name): 
    return sql.connect(db_name)

def SQL_acquisition(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])
    return df
    
def verify_total_steps(df):
    df_database = SQL_acquisition(f"SELECT Id, sum(StepTotal) AS total_steps FROM hourly_steps GROUP BY Id")
    df_csv = df.groupby('Id')['TotalSteps'].sum().reset_index()

    identical = df_database['total_steps'].equals(df_csv['TotalSteps'])
    print("If the total steps in csv file is indentical as in database?:", identical)
    