import os
from csv_data_wrangling import load_and_preview_data, clean_and_transform_data, summarize_data
from analysis import get_unique_users, unique_users_totaldistance, classify_user, linear_regression, check_activity_days, distance_days_correlation 
from database import connect_db, verify_total_steps
from visualization import plot_distance_distribution, plot_workout, plot_LRM, calories_burned_per_day
from creative_analysis import analyze_correlation
from lala_ex import print_random_message, dashboarding


FOLDER_DATA = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(FOLDER_DATA, "data", "daily_activity.csv")
DB_NAME = os.path.join(FOLDER_DATA, "data", "fitbit_database.db")

def main():
    print_random_message()

    # Load and clean data
    original_data = load_and_preview_data(DATA_FILE) 

    cleaned_data = clean_and_transform_data(original_data)  
    summarize_data(cleaned_data)  

    # Elementary data analysis
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
    verify_total_steps(cleaned_data, connection)
    connection.close()

    # Dashboarding
    dashboarding()
    

if __name__ == '__main__':
    main()
