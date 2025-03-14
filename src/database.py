import sqlite3 as sql
import pandas as pd
from analysis import SQL_acquisition, analyze_sleep_vs_activity, analyze_sleep_vs_sedentary, get_activity_by_time_blocks, calculate_time_block_averages, get_heart_rate_and_intensity, get_weather_and_daily_activity
from visualization import plot_sleep_vs_activity, plot_sleep_vs_sedentary, plot_activity_by_time_blocks, plot_heart_rate_and_intensity_by_id, plot_weather_and_daily_activity

def connect_db(db_name): 
    return sql.connect(db_name)
    
# lala's dashboard new helper funtion
def get_unique_user_ids(connection):
    query = "SELECT DISTINCT Id FROM daily_activity"
    cursor = connection.cursor()
    cursor.execute(query)
    return sorted([str(row[0]) for row in cursor.fetchall()])

def verify_total_steps(df, connection):
    df_database = SQL_acquisition(connection, f"SELECT Id, sum(StepTotal) AS total_steps FROM hourly_steps GROUP BY Id")
    df_csv = df.groupby('Id')['TotalSteps'].sum().reset_index()

    identical = df_database['total_steps'].equals(df_csv['TotalSteps'])
    print("If the total steps in csv file is indentical as in database?:", identical)
    

def compute_sleep_duration(connection):
    query = """
        SELECT Id, logId, COUNT(*) AS SleepDuration
        FROM minute_sleep
        GROUP BY Id, logId
        ORDER BY Id, logId
    """
    df_sleep = SQL_acquisition(connection, query)

    if df_sleep.empty:
        print("No sleep data found in database.")
        return pd.DataFrame()
    
    df_sleep["logId"] = df_sleep["logId"].astype(str)
    df_sleep["Id"] = df_sleep["Id"].astype(str)
    print("Computed Sleep Duration per User and Session:")

    return df_sleep


def sleep_vs_activity(connection):
    df_merged, model = analyze_sleep_vs_activity(connection)
    #print(model.summary())
    plot_sleep_vs_activity(df_merged)


def sleep_vs_sedentary(connection):
    df_merged, model = analyze_sleep_vs_sedentary(connection)
        # Display regression summary
    print(model.summary())
    plot_sleep_vs_sedentary(df_merged)
        

def activity_by_time_blocks_from_db(connection):
    hourly_steps_df, hourly_calories_df, minute_sleep_df = get_activity_by_time_blocks(connection)
    avg_steps, avg_calories, avg_sleep, labels = calculate_time_block_averages(hourly_steps_df, hourly_calories_df, minute_sleep_df)
    plot_activity_by_time_blocks(avg_steps, avg_calories, avg_sleep, labels)
    


def heart_rate_and_intensity_by_id(connection, user_id):
    heart_rate_df, hourly_intensity_df = get_heart_rate_and_intensity(connection, user_id)
    plot_heart_rate_and_intensity_by_id(heart_rate_df, hourly_intensity_df, user_id)
   

def discover_weather_impact(connection, CHICAGO_WEATHER):
    df_weather = pd.read_csv(CHICAGO_WEATHER)  
    df_final_activity, df_final_distance, df_final_steps = get_weather_and_daily_activity(connection, df_weather)
    plot_weather_and_daily_activity(df_final_activity, df_final_distance, df_final_steps)
