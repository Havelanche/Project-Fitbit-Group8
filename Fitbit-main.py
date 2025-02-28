import os
import pandas as pd
from csv_data_wrangling import load_and_preview_data, clean_and_transform_data, summarize_data
from data_processing import get_unique_users
from visualization import (
    plot_distance_distribution, plot_workout, plot_LRM, calories_burned_per_day,
    plot_activity_by_time_blocks, plot_heart_rate_and_intensity_by_id, plot_statistical_summary,
    plot_grouped_data, calories_vs_heart_rate
)
from analysis import (
    classify_user, linear_regression, analyze_sleep_vs_activity, analyze_sleep_vs_sedentary,
    calculate_time_block_averages, get_activity_by_time_blocks, get_heart_rate_and_intensity,
    merge_and_group_data, statistical_summary
)
from database import connect_db, verify_total_steps, compute_sleep_duration

DATA_FILE =  'daily_activity.csv'
DB_NAME = 'fitbit_database.db'

def main():
    # print("Daily Activity Sample:")
    # print(hourly_steps_df.head())

    # print("Minute Sleep Sample:")
    # print(minute_sleep_df.head())

    # print("Weight Log Sample:")
    # print(weight_log_df.head())
    cleaned_data = load_and_preview_data(DATA_FILE)
    cleaned_data = clean_and_transform_data(cleaned_data)
    summarize_data(cleaned_data) 

    # # follow-up parameter insert for function update
    # unique_users = get_unique_users(cleaned_data, 'TotalSteps')
    # print(f"Number of unique users: {cleaned_data['Id'].nunique()} \n")

    # plot_distance_distribution(cleaned_data)
    # plot_workout(cleaned_data)

    # model = linear_regression(cleaned_data)
    # print(model.summary())

    # # Calories burned per day (example user)
    # user_id_test = cleaned_data['Id'].iloc[0]  
    # calories_burned_per_day(cleaned_data, user_id=user_id_test, start_date="2016-03-01", end_date="2016-03-30")

    # plot_LRM(cleaned_data, user_id=user_id_test)

    # user_classes = classify_user(cleaned_data)
    # print(user_classes)

    connection = connect_db(DB_NAME)
    
    # if connection:
    #     verify_total_steps(cleaned_data, connection)
    #     df_sleep_duration = compute_sleep_duration(connection)
    #     print(df_sleep_duration)

    #     analyze_sleep_vs_activity(connection)
    #     analyze_sleep_vs_sedentary(connection)

    #     hourly_steps, hourly_calories, minute_sleep = get_activity_by_time_blocks(connection)
    #     avg_steps, avg_calories, avg_sleep, labels = calculate_time_block_averages(hourly_steps, hourly_calories, minute_sleep)
    #     plot_activity_by_time_blocks(avg_steps, avg_calories, avg_sleep, labels)

    #     get_heart_rate_and_intensity(connection, user_id='1503960366')

    #     df_grouped = merge_and_group_data(connection)
    #     plot_grouped_data(df_grouped)

    #     # df_summary = statistical_summary(df_grouped)
    #     # plot_statistical_summary(df_summary)

    #     # calories_vs_heart_rate(connection)

    #     connection.close()

if __name__ == '__main__':
    main()
