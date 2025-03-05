import numpy as np
import traceback
from database import SQL_acquisition
from visualization import plot_sleep_vs_activity, plot_sleep_vs_sedentary, plot_residuals,plot_heart_rate_and_intensity_by_id, plot_activity_by_time_blocks
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from scipy.stats import shapiro
import pandas as pd

def get_unique_users(df):
    unique_users = df.groupby('Id')['TotalDistance'].sum().reset_index()
    print(f"\nTotal number of unique users in dataset: {unique_users.shape[0]}")
    return unique_users

def unique_users_totaldistance(df):
    unique_users_total_distance = df.groupby('Id')['TotalDistance'].sum().reset_index()

    unique_users_total_distance.insert(0, 'Index', range(1, len(unique_users_total_distance) + 1))
    unique_users_total_distance.columns = ['User Index', 'User ID', 'Total Distance']

    print("\nTotal distance of each unique user:")
    print(unique_users_total_distance)
    return unique_users_total_distance

def classify_user(df):
    user_counts = df.groupby('Id').size()
    categories = pd.cut(user_counts, bins=[0, 10, 15, float('inf')], labels=['Light', 'Moderate', 'Heavy'])
    return pd.DataFrame({'Class': categories})

def linear_regression(df):
    df['Id'] = df['Id'].astype(str)
    model = smf.ols('Calories ~ TotalSteps + C(Id)', data=df).fit()
    return model

def check_activity_days(df):
    # Group the data by user ID and count unique dates for each user
    user_activity_days = df.groupby('Id')['ActivityDate'].nunique().reset_index()
    user_activity_days.insert(0, 'Index', range(1, len(user_activity_days) + 1))
    user_activity_days.columns = ['User Index', 'User ID', 'Activity Days']

    # Sort users by activity days for better visualization
    user_activity_days = user_activity_days.sort_values(by='Activity Days', ascending=False)

    plt.figure(figsize=(12, 6))
    
    # Create a bar plot with colors mapped to activity days
    bars = plt.bar(user_activity_days['User Index'], user_activity_days['Activity Days'], color='skyblue', edgecolor='black')

    # Apply a colormap effect based on activity days
    cmap = cm.get_cmap("YlOrRd")  
    max_days = max(user_activity_days['Activity Days'])
    for bar, days in zip(bars, user_activity_days['Activity Days']):
        bar.set_facecolor(cmap(days / max_days))  # Normalize activity days for colormap

    plt.xlabel('Users (Sorted by Activity Days)')
    plt.ylabel('Number of Activity Days')
    plt.title('Number of Activity Days per User')
    plt.xticks(ticks=user_activity_days['User Index'], labels=user_activity_days['User ID'], rotation=90)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.show()

    # Get the top 5 users with the most activity days
    top_5_users = user_activity_days.sort_values(by='Activity Days', ascending=False).head(5)
    print(f"\nTop 5 users with the most activity days:\n{top_5_users}")

    return user_activity_days, top_5_users

def distance_days_correlation(unique_user_distance, user_activity_days):
    merged_df = pd.merge(unique_user_distance, user_activity_days, on='User ID')

    # Get the top 5 users with the most activity days
    top_5_users = merged_df.sort_values(by='Activity Days', ascending=False).head(5)

    # Calculate Pearson correlation between Total Distance and Activity Days
    correlation = merged_df["Total Distance"].corr(merged_df["Activity Days"])
    print(f"\nPearson correlation between Total Distance and Activity Days: {correlation}")

    # Scatter plot to visualize the relationship
    plt.figure(figsize=(12, 6))
    # Plot all points (users) first
    scatter = plt.scatter(merged_df['Activity Days'], merged_df['Total Distance'], 
                          c=merged_df['Total Distance'], cmap='YlOrRd', edgecolor='black', label='Other Users')
    
    # Highlight the top 5 users with larger and different color points
    plt.scatter(top_5_users['Activity Days'], top_5_users['Total Distance'], 
                color='green', s=100, edgecolor='black', label='Top 5 Users')  # Larger red points

    plt.colorbar(scatter, label='Total Distance')  # Add color bar to indicate distance
    plt.xlabel('Activity Days')
    plt.ylabel('Total Distance')
    plt.title('Scatter Plot of Total Distance vs. Activity Days')
    plt.legend()  # Add a legend to differentiate points
    plt.grid(True)
    plt.show()  

    return merged_df

def analyze_sleep_vs_activity(connection):
    query_sleep = """
        SELECT Id, date AS ActivityDate, SUM(value) AS SleepDuration
        FROM minute_sleep
        WHERE value > 0
        GROUP BY Id, ActivityDate
    """
    df_sleep = pd.read_sql_query(query_sleep, connection)
    df_sleep["SleepDuration"] = df_sleep["SleepDuration"] / 60

    query_activity = """
        SELECT Id, ActivityDate, 
               (VeryActiveMinutes + FairlyActiveMinutes + LightlyActiveMinutes) AS TotalActiveMinutes
        FROM daily_activity
    """
    df_activity = pd.read_sql_query(query_activity, connection)

    # Prepare and merge data
    df_sleep["Id"] = df_sleep["Id"].astype(str)
    df_activity["Id"] = df_activity["Id"].astype(str)
    df_sleep["ActivityDate"] = pd.to_datetime(df_sleep["ActivityDate"]).dt.date.astype(str)
    df_activity["ActivityDate"] = pd.to_datetime(df_activity["ActivityDate"]).dt.date.astype(str)
    df_merged = df_activity.merge(df_sleep, on=["Id", "ActivityDate"], how="inner")

    if df_merged.empty:
        print("No data available after merging activity and sleep data.")
        return None

    model = smf.ols("SleepDuration ~ TotalActiveMinutes", data=df_merged).fit()
    print(model.summary())
    plot_sleep_vs_activity(df_merged)
    return df_merged, model

# TASK 4: SLEEP VS. SEDENTARY MINUTES
def analyze_sleep_vs_sedentary(connection):
    try:
        query_sleep = """
            SELECT Id, date AS ActivityDate, SUM(value) AS SleepDuration
            FROM minute_sleep
            WHERE value > 0
            GROUP BY Id, ActivityDate
        """
        df_sleep = pd.read_sql_query(query_sleep, connection)
        df_sleep["SleepDuration"] = df_sleep["SleepDuration"] / 60

        query_sedentary = """
            SELECT Id, ActivityDate, SedentaryMinutes
            FROM daily_activity
        """
        df_sedentary = pd.read_sql_query(query_sedentary, connection)
        df_sleep["Id"] = df_sleep["Id"].astype(str)
        df_sedentary["Id"] = df_sedentary["Id"].astype(str)
        df_sleep["ActivityDate"] = pd.to_datetime(df_sleep["ActivityDate"]).dt.date.astype(str)
        df_sedentary["ActivityDate"] = pd.to_datetime(df_sedentary["ActivityDate"]).dt.date.astype(str)
        df_merged = df_sedentary.merge(df_sleep, on=["Id", "ActivityDate"], how="inner")

        if df_merged.empty:
            print("Error: Merged dataframe is empty. Check date formats.")
            return None

        model = smf.ols("SleepDuration ~ SedentaryMinutes", data=df_merged).fit()
        print(model.summary())
        plot_sleep_vs_sedentary(df_merged)
        plot_residuals(model)

        # Shapiro-Wilk test for normality
        residuals = model.resid
        sample = residuals.sample(min(5000, len(residuals)), random_state=42)
        shapiro_test_stat, shapiro_p_value = shapiro(sample)
        print(f"\nShapiro-Wilk Test for Normality: Test Statistic = {shapiro_test_stat:.4f}, p-value = {shapiro_p_value:.6f}")

        if shapiro_p_value < 0.05:
            print("Residuals are NOT normally distributed. Consider transformations.")
        else:
            print("Residuals appear normally distributed.")

        return df_merged, model
    except Exception as e:
        print(f" An error occurred: {e}")
        return None

def calculate_time_block_averages(hourly_steps_df, hourly_calories_df, minute_sleep_df):
    time_blocks = [(0, 4), (4, 8), (8, 12), (12, 16), (16, 20), (20, 24)]

    def calculate_avg(df, column):
        return [df[(df['hour'] >= start) & (df['hour'] < end)][column].mean() for start, end in time_blocks]

    avg_steps = calculate_avg(hourly_steps_df, 'StepTotal')
    avg_calories = calculate_avg(hourly_calories_df, 'Calories')
    avg_sleep = [minute_sleep_df[(minute_sleep_df['hour'] >= start) & (minute_sleep_df['hour'] < end)]['value'].sum() / 60
                 for start, end in time_blocks]

    labels = [f"{start}-{end}" for start, end in time_blocks]
    return avg_steps, avg_calories, avg_sleep, labels

def get_activity_by_time_blocks(connection):
    hourly_steps_query = "SELECT * FROM hourly_steps;"
    hourly_calories_query = "SELECT * FROM hourly_calories;"
    minute_sleep_query = "SELECT * FROM minute_sleep;"

    hourly_steps_df = pd.read_sql(hourly_steps_query, connection)
    hourly_calories_df = pd.read_sql(hourly_calories_query, connection)
    minute_sleep_df = pd.read_sql(minute_sleep_query, connection)

    hourly_steps_df['ActivityHour'] = pd.to_datetime(hourly_steps_df['ActivityHour'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    hourly_calories_df['ActivityHour'] = pd.to_datetime(hourly_calories_df['ActivityHour'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    minute_sleep_df['date'] = pd.to_datetime(minute_sleep_df['date'], errors='coerce')
    
    hourly_steps_df['hour'] = hourly_steps_df['ActivityHour'].dt.hour
    hourly_calories_df['hour'] = hourly_calories_df['ActivityHour'].dt.hour
    minute_sleep_df['hour'] = minute_sleep_df['date'].dt.hour

    avg_steps, avg_calories, avg_sleep, labels = calculate_time_block_averages(
        hourly_steps_df, hourly_calories_df, minute_sleep_df
    )
    return hourly_steps_df, hourly_calories_df, minute_sleep_df

# TASK 6: HEART RATE & INTENSITY
def get_heart_rate_and_intensity(connection, user_id):
    heart_rate_query = f"SELECT * FROM heart_rate WHERE Id = {user_id};"
    hourly_intensity_query = f"SELECT * FROM hourly_intensity WHERE Id = {user_id};"

    heart_rate_df = pd.read_sql(heart_rate_query, connection)
    hourly_intensity_df = pd.read_sql(hourly_intensity_query, connection)

    heart_rate_df['Time'] = pd.to_datetime(heart_rate_df['Time'], errors='coerce')
    hourly_intensity_df['ActivityHour'] = pd.to_datetime(hourly_intensity_df['ActivityHour'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')

    plot_heart_rate_and_intensity_by_id(heart_rate_df, hourly_intensity_df, user_id)

def aggregate_data(df, raw_data=None, group_by='Id'):
    try:
        print("Running aggregate_data function")
        df['date'] = pd.to_datetime(df['ActivityDate'], errors='coerce')
        df['DayOfWeek'] = df['date'].dt.day_name()
        df['Hour'] = df['date'].dt.hour
        group_columns = [group_by, 'DayOfWeek', 'Hour']

        # Aggregation
        aggregated = df.groupby(group_columns).agg({
            'TotalSteps': ['mean', 'median', 'std'],
            'Calories': ['mean', 'median', 'std'],
            'SedentaryMinutes': ['mean', 'median', 'std'],
            'SleepMinutes': ['mean', 'median', 'std'],
            'WeightKg': ['mean', 'median', 'std'],
            'BMI': ['mean', 'median', 'std']
        }).reset_index()

        # Ensure multi-index columns are flattened
        aggregated.columns = ['_'.join(map(str, col)).strip('_') if isinstance(col, tuple) else col for col in aggregated.columns]

        # Create a mapping for old and new names
        col_mapping = {
            'TotalSteps_mean': 'TotalSteps',
            'Calories_mean': 'Calories',
            'SedentaryMinutes_mean': 'SedentaryMinutes',
            'SleepMinutes_mean': 'SleepMinutes',
            'WeightKg_mean': 'WeightKg',
            'BMI_mean': 'BMI'
        }

        # Add backward-compatible columns
        for new_col, old_col in col_mapping.items():
            if new_col in aggregated.columns:
                aggregated[old_col] = aggregated[new_col]
                #debug print
        # print("New column names after aggregation:", aggregated.columns.tolist())
        return aggregated

    except Exception as e:
        print(f"Error in aggregate_data: {e}")
        traceback.print_exc()
        return None


def merge_and_group_data(df):
    try:
        # Fetch data from tables
        daily_activity = pd.read_sql("SELECT Id, ActivityDate, TotalSteps, Calories, SedentaryMinutes FROM daily_activity", df)
        minute_sleep = pd.read_sql("SELECT Id, date AS ActivityDate, value AS SleepMinutes FROM minute_sleep", df)
        weight_log = pd.read_sql("SELECT Id, Date AS ActivityDate, WeightKg, BMI FROM weight_log", df)
        
        # Convert dates
        for data in [daily_activity, minute_sleep, weight_log]:
            data['ActivityDate'] = pd.to_datetime(data['ActivityDate'], format='%m/%d/%Y', errors='coerce')

        merged_df = daily_activity.merge(minute_sleep, on=['Id', 'ActivityDate'], how='left')
        merged_df = merged_df.merge(weight_log, on=['Id', 'ActivityDate'], how='left')

        return handle_missing_weight_data(merged_df)

    except Exception as e:
        print(f"Error in merge_and_group_data: {e}")
        traceback.print_exc()
        return None

def statistical_summary(df, group_by='Id'):
    try:
        summary = df.groupby(group_by).agg({
            'TotalSteps': ['mean', 'median', 'std'],
            'Calories': ['mean', 'median', 'std'],
            'SedentaryMinutes': ['mean', 'median', 'std'],
            'SleepMinutes': ['mean', 'median', 'std'],
            'WeightKg': ['mean', 'median', 'std'],
            'BMI': ['mean', 'median', 'std']
        }).reset_index()

        # Flatten multi-index columns
        summary.columns = ['_'.join(col).rstrip('_') if isinstance(col, tuple) else col for col in summary.columns]
        #debug print
        # print("Flattened column names for statistical summary:", summary.columns.tolist())
        return summary

    except Exception as e:
        print(f"Error in statistical_summary: {e}")
        traceback.print_exc()
        return None


def activity_vs_sleep_insights(df):
    try:
        df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], errors='coerce')
        df['DayOfWeek'] = df['ActivityDate'].dt.day_name()
        df['Weekend'] = df['DayOfWeek'].isin(['Saturday', 'Sunday'])

        weekend_comparison = df.groupby('Weekend').agg({
            'TotalSteps_mean': 'mean',
            'SleepMinutes_mean': 'mean',
            'Calories_mean': 'mean'
        }).reset_index()

        print("Weekend vs weekday activity and sleep:")
        print(weekend_comparison)

        return weekend_comparison
    except Exception as e:
        print(f"Error in activity_vs_sleep_insights: {e}")
        traceback.print_exc()
        return None

def handle_missing_weight_data(df):
    median_fill_cols = ['TotalSteps', 'Calories', 'SedentaryMinutes', 'SleepMinutes']
    for col in median_fill_cols:
        df[col] = df[col].fillna(df[col].median())
   
    def estimate_bmi(weight):
        if pd.isna(weight):
            return np.nan
        
        if weight < 50:
            return 20  # Typical for smaller individuals
        elif weight < 70:
            return 22  # Average range
        elif weight < 90:
            return 25  # Higher range
        elif weight < 110:
            return 28  # Overweight range
        else:
            return 30  # Obese range
    
    df['BMI'] = df['BMI'].fillna(df['WeightKg'].apply(estimate_bmi))
    df[['BMI', 'WeightKg']] = df[['BMI', 'WeightKg']].fillna(df[['BMI', 'WeightKg']].median())

    print("Missing weight data handled.")
    return df
    
def fill_missing_values(df):
    num_cols = ['TotalSteps', 'Calories', 'SedentaryMinutes', 'SleepMinutes', 'WeightKg', 'BMI']
    for col in num_cols:
        df[col] = df[col].fillna(df[col].median())  
    if 'ActivityDate' in df.columns:
        df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], errors='coerce')
        df = df.sort_values(by=['Id', 'ActivityDate'])
        df['ActivityDate'] = df['ActivityDate'].fillna(method='ffill')

    if 'DayOfWeek' in df.columns:
        df['DayOfWeek'] = df['DayOfWeek'].fillna('Unknown')

    print("Missing values filled.")
    print(df.isnull().sum())

    return df