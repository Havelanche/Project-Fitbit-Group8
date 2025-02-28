import os
from csv_data_wrangling import load_and_preview_data, clean_and_transform_data, summarize_data
from visualization import plot_distance_distribution, plot_workout, plot_LRM, calories_burned_per_day
from analysis import classify_user, linear_regression
from data_processing import load_data, get_unique_users
from visualization import plot_distance_distribution, plot_workout, plot_LRM, calories_burned_per_day, plot_activity_by_time_blocks, plot_heart_rate_and_intensity_by_id
from analysis import classify_user, linear_regression, analyze_sleep_vs_activity, analyze_sleep_vs_sedentary, calculate_time_block_averages, get_activity_by_time_blocks, get_heart_rate_and_intensity
from database import connect_db, verify_total_steps, compute_sleep_duration

FOLDER_DATA = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(FOLDER_DATA, "data", "daily_activity.csv")
DB_NAME = os.path.join(FOLDER_DATA, "data", "fitbit_database.db")

def main():
    
    # Load and clean data
    original_data = load_and_preview_data(DATA_FILE) 

    cleaned_data = clean_and_transform_data(original_data)  
    summarize_data(cleaned_data) 

    # follow-up parameter insert for function update
    unique_users = get_unique_users(cleaned_data, 'TotalSteps')
    print(f"Number of unique users: {cleaned_data['Id'].nunique()} \n")

    # Visualization
    plot_distance_distribution(cleaned_data)
    plot_workout(cleaned_data)

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
        cleaned_data_sleep_duration = analyze_sleep_vs_activity(connection)
        analyze_sleep_vs_sedentary(connection)

        hourly_steps_cleaned_data, hourly_calories_cleaned_data, minute_sleep_cleaned_data = get_activity_by_time_blocks(connection)
        hourly_steps_cleaned_data['hour'] = hourly_steps_cleaned_data['ActivityHour'].dt.hour
        hourly_calories_cleaned_data['hour'] = hourly_calories_cleaned_data['ActivityHour'].dt.hour
        minute_sleep_cleaned_data['hour'] = minute_sleep_cleaned_data['date'].dt.hour

        avg_steps, avg_calories, avg_sleep, labels = calculate_time_block_averages(
            hourly_steps_cleaned_data, hourly_calories_cleaned_data, minute_sleep_cleaned_data
        )
        plot_activity_by_time_blocks(avg_steps, avg_calories, avg_sleep, labels)
        get_heart_rate_and_intensity(connection, user_id='1503960366')
        connection.close()

if __name__ == '__main__':
    main()
