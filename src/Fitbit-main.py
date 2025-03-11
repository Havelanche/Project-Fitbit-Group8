import os

import pandas as pd
from csv_data_wrangling import load_and_preview_data, clean_and_transform_data, summarize_data
from visualization import plot_distance_distribution, plot_grouped_data, plot_statistical_summary, plot_weekend_vs_weekday, plot_workout, plot_LRM, calories_burned_per_day, plot_activity_by_time_blocks
from analysis import activity_vs_sleep_insights, aggregate_data, analyze_weight_log, check_activity_days, classify_user, distance_days_correlation, linear_regression, get_unique_users, merge_and_analyze_data, unique_users_totaldistance, analyze_sleep_vs_activity, analyze_sleep_vs_sedentary, calculate_time_block_averages, get_activity_by_time_blocks, get_heart_rate_and_intensity
from database import connect_db, compute_sleep_duration, verify_total_steps, discover_weather_impact

FOLDER_DATA = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(FOLDER_DATA, "data", "daily_activity.csv")
DB_NAME = os.path.join(FOLDER_DATA, "data", "fitbit_database.db")
CHICAGO_WEATHER = os.path.join(FOLDER_DATA, "data", "Chicago_Weather.csv")
# CHICAGO_WEATHER = os.path.join(FOLDER_DATA, "data", "Chicago_Weather.csv")

def main():
    
    # Load and clean data
    original_data = load_and_preview_data(DATA_FILE) 
    cleaned_data = clean_and_transform_data(original_data)
    summarize_data(cleaned_data)

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

    # Database verification
    connection = connect_db(DB_NAME)
    
    if connection:

        verify_total_steps(cleaned_data, connection)
        df_sleep_duration = compute_sleep_duration(connection)
        print(df_sleep_duration)

        analyze_sleep_vs_activity(connection)
        analyze_sleep_vs_sedentary(connection)

        hourly_steps, hourly_calories, minute_sleep = get_activity_by_time_blocks(connection)
        avg_steps, avg_calories, avg_sleep, labels = calculate_time_block_averages(hourly_steps, hourly_calories, minute_sleep)
        plot_activity_by_time_blocks(avg_steps, avg_calories, avg_sleep, labels)

        get_heart_rate_and_intensity(connection, user_id='1503960366')
        discover_weather_impact(connection, CHICAGO_WEATHER)
        # discover_weather_impact(connection, CHICAGO_WEATHER) it is twice
        
            # 2. Aggregate data
        # print("Merging and analyzing data...")
        merged_df, user_summaries = merge_and_analyze_data(connection)
        
        # print("Aggregating data...")
        df_aggregated = aggregate_data(merged_df)

        # 3. Activity vs Sleep insights (Weekends vs Weekdays)
        # print("Analyzing activity vs sleep...")
        activity_vs_sleep_insights(df_aggregated)

        # 4. Weight log analysis
        print("Analyzing weight log...")
        analyze_weight_log(connection)

        # 5. Visualizations
        # print("Generating visualizations...")
        plot_grouped_data(df_aggregated)
        plot_statistical_summary(user_summaries)
        # print("weekend_vs_weekday...")
        plot_weekend_vs_weekday(df_aggregated)


        connection.close()

if __name__ == '__main__':
    main()
