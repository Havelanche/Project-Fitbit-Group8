import traceback
from csv_data_wrangling import load_and_preview_data, clean_and_transform_data, summarize_data
from visualization import (
    plot_distance_distribution, plot_weekend_vs_weekday, plot_workout, plot_LRM, calories_burned_per_day,
    plot_activity_by_time_blocks, plot_statistical_summary,
    plot_grouped_data, calories_vs_heart_rate
)
from analysis import (
    activity_vs_sleep_insights, aggregate_data, check_activity_days, classify_user, distance_days_correlation, fill_missing_values, linear_regression, analyze_sleep_vs_activity, analyze_sleep_vs_sedentary,
    calculate_time_block_averages, get_activity_by_time_blocks, get_heart_rate_and_intensity,
    merge_and_group_data, statistical_summary, unique_users_totaldistance, get_unique_users
)
from database import SQL_acquisition, connect_db, verify_total_steps, compute_sleep_duration

DATA_FILE =  "dailyactivity.csv"
DB_NAME = "fitbit_database.db"

def proccess_data():
    
    try:
        # # Load and clean data
        original_data = load_and_preview_data(DATA_FILE) 
        cleaned_data = clean_and_transform_data(original_data)
        # summarize_data(cleaned_data)

        # follow-up parameter insert for function update
        unique_users = get_unique_users(cleaned_data)
        unique_user_distance = unique_users_totaldistance(cleaned_data)
        
        # Visualization
        plot_distance_distribution(unique_user_distance)
        plot_workout(cleaned_data)
        
        # Creative Analysis
        user_activity_days, top_5_users = check_activity_days(cleaned_data)
        merge_df_distance_days = distance_days_correlation(unique_user_distance, user_activity_days)


        # Linear regression model
        model = linear_regression(cleaned_data)
        print(model.summary())

        # Calories burned per day (example user)
        user_id_test = cleaned_data['Id'].iloc[0]  
        calories_burned_per_day(cleaned_data, user_id=user_id_test, start_date="2016-03-01", end_date="2016-03-30")

        # Regression plot for a user
        plot_LRM(cleaned_data, user_id=user_id_test)

        # Classify users based on activity
        user_classes = classify_user(cleaned_data)
        print(user_classes)
        return cleaned_data
        
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc() 
    
 
def analyzing_dataframe(connection, cleaned_data):
    try:
         # verify_total_steps(cleaned_data, connection)
        # df_sleep_duration = compute_sleep_duration(connection)
        # print(df_sleep_duration)

        # analyze_sleep_vs_activity(connection)
        # analyze_sleep_vs_sedentary(connection)

        # hourly_steps, hourly_calories, minute_sleep = get_activity_by_time_blocks(connection)
        # avg_steps, avg_calories, avg_sleep, labels = calculate_time_block_averages(hourly_steps, hourly_calories, minute_sleep)
        # plot_activity_by_time_blocks(avg_steps, avg_calories, avg_sleep, labels)

        # get_heart_rate_and_intensity(connection, user_id='1503960366')
        # discover_weather_impact(connection, CHICAGO_WEATHER)
        # discover_weather_impact(connection, CHICAGO_WEATHER) it is twice
        # tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
        # tables = pd.read_sql_query(tables_query, connection)
        # print("Tables in the database:")
        # print(tables)
        
        # minute_sleep_preview = pd.read_sql_query("PRAGMA table_info(minute_sleep);", connection)
        # print("Columns in minute_sleep table:")
        # print(minute_sleep_preview)
        
        # minute_sleep_data = pd.read_sql_query("SELECT * FROM minute_sleep LIMIT 10;", connection)
        # print("\nSample data from minute_sleep:")
        # print(minute_sleep_data)
        
        # weight_log_preview = pd.read_sql_query("PRAGMA table_info(weight_log);", connection)
        # print("Columns in weight_log table:")
        # print(weight_log_preview)

        # # Preview the first 10 rows of weight_log
        # weight_log_data = pd.read_sql_query("SELECT * FROM weight_log LIMIT 10;", connection)
        # print("\nSample data from weight_log:")
        # print(weight_log_data)
        
            # 2. Aggregate data
        print("Merging and analyzing data...")
        merged_df, user_summaries = merge_and_analyze_data(connection)
        
        print("Aggregating data...")
        df_aggregated = aggregate_data(merged_df)

        # 3. Activity vs Sleep insights (Weekends vs Weekdays)
        print("Analyzing activity vs sleep...")
        weekend_data = activity_vs_sleep_insights(df_aggregated)

        # 4. Weight log analysis
        print("Analyzing weight log...")
        weight_data = analyze_weight_log(connection)

        # 5. Visualizations
        print("Generating visualizations...")
        plot_grouped_data(df_aggregated)
        plot_statistical_summary(user_summaries)
        plot_weekend_vs_weekday(weekend_data)
        df, model = analyze_calories_vs_heart_rate(connection)
        plot_calories_vs_heart_rate(df)

        connection.close()
    except Exception as e:
        print(f"An error occurred while analyzing the dataframe: {e}")
        traceback.print_exc()  
        connection.close()
           
def main():
    try:
        cleaned_data = proccess_data()
        connection = connect_db(DB_NAME)
        if connection: 
            analyzing_dataframe(connection, cleaned_data)
            connection.close()  # Close the database connection after analyzing.
    except Exception as e:
        print(f"An error occurred in the main: {e}")
        traceback.print_exc()
        connection.close()  # Close the database connection if an error occurs at any point.
        
if __name__ == '__main__':
    main()
