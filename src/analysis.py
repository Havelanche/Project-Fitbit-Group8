import traceback
import numpy as np
from visualization import plot_sleep_vs_activity, plot_sleep_vs_sedentary, plot_residuals
import statsmodels.formula.api as smf
from scipy.stats import shapiro
import seaborn as sns
import pandas as pd
import matplotlib.cm as cm
import matplotlib.pyplot as plt

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
    user_counts = df.groupby('Id')['VeryActiveMinutes'].mean()
    categories = pd.cut(user_counts, bins=[0, 10, 15, float('inf')], labels=['Light', 'Moderate', 'Heavy'])
    return pd.DataFrame({'Class': categories})

def linear_regression(df):
    df['Id'] = df['Id'].astype(str)
    model = smf.ols('Calories ~ TotalSteps + C(Id)', data=df).fit()
    return model

def check_activity_days(df):
    user_activity_days = df.groupby('Id')['ActivityDate'].nunique().reset_index()
    user_activity_days.insert(0, 'Index', range(1, len(user_activity_days) + 1))
    user_activity_days.columns = ['User Index', 'User ID', 'Activity Days']

    user_activity_days = user_activity_days.sort_values(by='Activity Days', ascending=False)

    plt.figure(figsize=(12, 6))
    
    bars = plt.bar(user_activity_days['User Index'], user_activity_days['Activity Days'], color='skyblue', edgecolor='black')

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

    top_5_users = user_activity_days.sort_values(by='Activity Days', ascending=False).head(5)
    print(f"\nTop 5 users with the most activity days:\n{top_5_users}")

    return user_activity_days, top_5_users

def distance_days_correlation(unique_user_distance, user_activity_days):
    merged_df = pd.merge(unique_user_distance, user_activity_days, on='User ID')

    top_5_users = merged_df.sort_values(by='Activity Days', ascending=False).head(5)

    correlation = merged_df["Total Distance"].corr(merged_df["Activity Days"])
    print(f"\nPearson correlation between Total Distance and Activity Days: {correlation}")

    plt.figure(figsize=(12, 6))
    scatter = plt.scatter(merged_df['Activity Days'], merged_df['Total Distance'], 
                          c=merged_df['Total Distance'], cmap='YlOrRd', edgecolor='black', label='Other Users')
    
    plt.scatter(top_5_users['Activity Days'], top_5_users['Total Distance'], 
                color='green', s=100, edgecolor='black', label='Top 5 Users')  

    plt.colorbar(scatter, label='Total Distance') 
    plt.xlabel('Activity Days')
    plt.ylabel('Total Distance')
    plt.title('Scatter Plot of Total Distance vs. Activity Days')
    plt.legend() 
    plt.grid(True)
    plt.show()  

    return merged_df

def SQL_acquisition(connection, query):
    try:
         with connection:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])
            return df
    except Exception as e:
        print(f"An error occurred while executing the SQL query: {e}")
        return pd.DataFrame()
    
def analyze_sleep_vs_activity(connection):
    try:
        query_sleep = """
            SELECT Id, 
                   COUNT(*) AS SleepDuration
            FROM minute_sleep
            WHERE value > 0
            GROUP BY Id
        """
        df_sleep = SQL_acquisition(connection, query_sleep)

        query_activity = """
            SELECT Id, 
                   COALESCE(VeryActiveMinutes, 0) + 
                   COALESCE(FairlyActiveMinutes, 0) + 
                   COALESCE(LightlyActiveMinutes, 0) AS TotalActiveMinutes
            FROM daily_activity
            GROUP BY Id

        """
        df_activity = SQL_acquisition(connection, query_activity)

        df_sleep["Id"] = df_sleep["Id"].astype(str)
        df_activity["Id"] = df_activity["Id"].astype(str)

        df_merged = df_activity.merge(df_sleep, on=["Id"], how="inner")

        if df_merged.empty:
            print("No data available after merging activity and sleep data.")
            return None
    
    except Exception as e:
        print(f"⚠️ An error occurred: {e}")
        return None

    model = smf.ols("SleepDuration ~ TotalActiveMinutes", data=df_merged).fit()
    print(model.summary())
    plot_sleep_vs_activity(df_merged)
    return df_merged, model

# TASK 4: SLEEP VS. SEDENTARY MINUTES
def analyze_sleep_vs_sedentary(connection):
    try:
        query_sleep = """
            SELECT Id, 
                   COUNT(*) AS SleepDuration
            FROM minute_sleep
            WHERE value > 0
            GROUP BY Id
        """
        df_sleep = SQL_acquisition(connection, query_sleep)

        query_sedentary = """
            SELECT Id, 
                   COALESCE(SedentaryMinutes, 0) AS SedentaryMinutes
            FROM daily_activity
            GROUP BY Id

        """
        df_sedentary = SQL_acquisition(connection, query_sedentary)

        df_sleep["Id"] = df_sleep["Id"].astype(str)
        df_sedentary["Id"] = df_sedentary["Id"].astype(str)

        df_merged = df_sedentary.merge(df_sleep, on=["Id"], how="inner")

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
        print(f"⚠️ An error occurred: {e}")
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

    hourly_steps_df = SQL_acquisition(connection, hourly_steps_query)
    hourly_calories_df = SQL_acquisition(connection, hourly_calories_query)
    minute_sleep_df = SQL_acquisition(connection, minute_sleep_query)

    hourly_steps_df['ActivityHour'] = pd.to_datetime(hourly_steps_df['ActivityHour'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    hourly_calories_df['ActivityHour'] = pd.to_datetime(hourly_calories_df['ActivityHour'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    minute_sleep_df['date'] = pd.to_datetime(minute_sleep_df['date'], errors='coerce')
    
    hourly_steps_df['hour'] = hourly_steps_df['ActivityHour'].dt.hour
    hourly_calories_df['hour'] = hourly_calories_df['ActivityHour'].dt.hour
    minute_sleep_df['hour'] = minute_sleep_df['date'].dt.hour

    return hourly_steps_df, hourly_calories_df, minute_sleep_df

# TASK 6: HEART RATE & INTENSITY
def get_heart_rate_and_intensity(connection, user_id):
    heart_rate_query = f"SELECT * FROM heart_rate WHERE Id = {user_id};"
    hourly_intensity_query = f"SELECT * FROM hourly_intensity WHERE Id = {user_id};"

    heart_rate_df = SQL_acquisition(connection, heart_rate_query)
    hourly_intensity_df = SQL_acquisition(connection, hourly_intensity_query)

    heart_rate_df['Time'] = pd.to_datetime(heart_rate_df['Time'])
    hourly_intensity_df['ActivityHour'] = pd.to_datetime(hourly_intensity_df['ActivityHour'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')

    return heart_rate_df, hourly_intensity_df

# TASK 7: Weather Impact
def get_weather_and_daily_activity(connection, df_weather):
    query_active = """
    SELECT ActivityDate, AVG(LightlyActiveMinutes) AS LightlyActive, 
    AVG(FairlyActiveMinutes) AS FairlyActive, 
    AVG(VeryActiveMinutes) AS VeryActive
    FROM daily_activity GROUP BY ActivityDate
    """
    query_distance = """
    SELECT ActivityDate, AVG(TotalDistance) AS TotalDistance FROM daily_activity GROUP BY ActivityDate
    """
    query_steps = """
    SELECT ActivityDate, AVG(TotalSteps) AS TotalSteps FROM daily_activity GROUP BY ActivityDate
    """
    df_activity = SQL_acquisition(connection, query_active)
    df_distance = SQL_acquisition(connection, query_distance)
    df_steps = SQL_acquisition(connection, query_steps)

    df_activity['ActivityDate'] = pd.to_datetime(df_activity['ActivityDate'])
    df_distance['ActivityDate'] = pd.to_datetime(df_distance['ActivityDate'])
    df_steps['ActivityDate'] = pd.to_datetime(df_steps['ActivityDate'])

    df_weather['datetime'] = pd.to_datetime(df_weather['datetime'])
    
    df_activity_merged = df_activity.merge(df_weather[['datetime', 'temp']], left_on='ActivityDate', right_on='datetime', how='inner')
    df_distance_merged = df_distance.merge(df_weather[['datetime', 'temp']], left_on='ActivityDate', right_on='datetime', how='inner')
    df_steps_merged = df_steps.merge(df_weather[['datetime', 'temp']], left_on='ActivityDate', right_on='datetime', how='inner')
    temp_bins = list(range(int(df_weather['temp'].min()), int(df_weather['temp'].max()) + 5, 5))
    temp_labels = [f"{t}-{t+5}" for t in temp_bins[:-1]]

    df_activity_merged['temp_bin'] = pd.cut(df_activity_merged['temp'], bins=temp_bins, labels=temp_labels)
    df_distance_merged['temp_bin'] = pd.cut(df_distance_merged['temp'], bins=temp_bins, labels=temp_labels)
    df_steps_merged['temp_bin'] = pd.cut(df_steps_merged['temp'], bins=temp_bins, labels=temp_labels)

    df_final_activity = df_activity_merged.groupby('temp_bin', observed=False)[['LightlyActive', 'FairlyActive', 'VeryActive']].mean().reset_index()
    df_final_distance = df_distance_merged.groupby('temp_bin', observed=False)[['TotalDistance']].mean().reset_index()
    df_final_steps = df_steps_merged.groupby('temp_bin', observed=False)[['TotalSteps']].mean().reset_index()

    return df_final_activity, df_final_distance, df_final_steps

#Task 8: aggregate data.
def aggregate_data(df, raw_data=None, group_by='Id'):
    try:
        print("Running aggregate_data function")

        # Convert to datetime and extract necessary columns
        df['date'] = pd.to_datetime(df['ActivityDate'], errors='coerce')
        df['DayOfWeek'] = df['date'].dt.day_name()
        df['Hour'] = df['date'].dt.hour

        # Define grouping columns
        group_columns = [group_by, 'DayOfWeek', 'Hour']

        # Aggregation on multiple columns with mean, median, and std
        aggregated = df.groupby(group_columns).agg({
            'TotalSteps': ['mean', 'median', 'std'],
            'Calories': ['mean', 'median', 'std'],
            'SedentaryMinutes': ['mean', 'median', 'std'],
            'SleepMinutes': ['mean', 'median', 'std'],
            'WeightKg': ['mean', 'median', 'std'],
            'BMI': ['mean', 'median', 'std']
        }).reset_index()

        # Flatten multi-index columns
        aggregated.columns = ['_'.join(map(str, col)).strip('_') if isinstance(col, tuple) else col for col in aggregated.columns]

        # Map old column names to new ones
        col_mapping = {
            'TotalSteps_mean': 'TotalSteps',
            'Calories_mean': 'Calories',
            'SedentaryMinutes_mean': 'SedentaryMinutes',
            'SleepMinutes_mean': 'SleepMinutes',
            'WeightKg_mean': 'WeightKg',
            'BMI_mean': 'BMI'
        }
        print("Columns after merge:", aggregated.columns)

        for new_col, old_col in col_mapping.items():
            if new_col in aggregated.columns:
                aggregated[old_col] = aggregated[new_col]

        return aggregated

    except Exception as e:
        print(f"Error in aggregate_data: {e}")
        traceback.print_exc()
        return None

# Task 9: Analyzing and merge data
def merge_and_analyze_data(connection):
    try:
        # Load all relevant tables
        daily_activity = SQL_acquisition(connection, 
            "SELECT Id, ActivityDate, TotalSteps, TotalDistance, Calories, "
            "SedentaryMinutes, VeryActiveMinutes, FairlyActiveMinutes, LightlyActiveMinutes "
            "FROM daily_activity")

        heart_rate = SQL_acquisition(connection, 
            "SELECT Id, Time AS ActivityDate, Value AS HeartRate FROM heart_rate")

        hourly_calories = SQL_acquisition(connection, 
            "SELECT Id, ActivityHour AS ActivityDate, Calories AS HourlyCalories FROM hourly_calories")

        hourly_intensity = SQL_acquisition(connection, 
            "SELECT Id, ActivityHour AS ActivityDate, TotalIntensity, AverageIntensity FROM hourly_intensity")

        hourly_steps = SQL_acquisition(connection, 
            "SELECT Id, ActivityHour AS ActivityDate, StepTotal FROM hourly_steps")

        minute_sleep = SQL_acquisition(connection, 
            "SELECT Id, date AS ActivityDate, value AS SleepMinutes FROM minute_sleep")

        weight_log = SQL_acquisition(connection, 
            "SELECT Id, Date AS ActivityDate, WeightKg, BMI FROM weight_log")

        daily_activity['ActivityDate'] = pd.to_datetime(daily_activity['ActivityDate'], format='%m/%d/%Y', errors='coerce')
        heart_rate['ActivityDate'] = pd.to_datetime(heart_rate['ActivityDate'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
        hourly_calories['ActivityDate'] = pd.to_datetime(hourly_calories['ActivityDate'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
        hourly_intensity['ActivityDate'] = pd.to_datetime(hourly_intensity['ActivityDate'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
        hourly_steps['ActivityDate'] = pd.to_datetime(hourly_steps['ActivityDate'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
        minute_sleep['ActivityDate'] = pd.to_datetime(minute_sleep['ActivityDate'].str.split().str[0], format='%m/%d/%Y', errors='coerce')
        weight_log['ActivityDate'] = pd.to_datetime(weight_log['ActivityDate'].str.split().str[0], format='%m/%d/%Y', errors='coerce')

        minute_sleep = minute_sleep.groupby(['Id', 'ActivityDate']).agg({'SleepMinutes': 'sum'}).reset_index()
        merged_df = daily_activity.copy()

        for df in [minute_sleep, weight_log, hourly_calories, hourly_intensity, hourly_steps, heart_rate]:
            merged_df = pd.merge(merged_df, df, on=['Id', 'ActivityDate'], how='left')
        
        merged_df['SleepMinutes'] = merged_df['SleepMinutes'].fillna(0)
        merged_df['WeightKg'] = merged_df['WeightKg'].fillna(merged_df['WeightKg'].median(skipna=True))
        merged_df['BMI'] = merged_df['BMI'].fillna(merged_df['BMI'].median(skipna=True))
        merged_df['HeartRate'] = merged_df['HeartRate'].fillna(merged_df['HeartRate'].median(skipna=True))
        merged_df['HourlyCalories'] = merged_df['HourlyCalories'].fillna(0)
        merged_df['TotalIntensity'] = merged_df['TotalIntensity'].fillna(0)
        merged_df['AverageIntensity'] = merged_df['AverageIntensity'].fillna(0)
        merged_df['StepTotal'] = merged_df['StepTotal'].fillna(0)

        numeric_cols = ['TotalSteps', 'Calories', 'SedentaryMinutes', 'VeryActiveMinutes', 
                        'FairlyActiveMinutes', 'LightlyActiveMinutes', 'SleepMinutes', 
                        'WeightKg', 'BMI', 'HeartRate', 'HourlyCalories', 
                        'TotalIntensity', 'AverageIntensity', 'StepTotal']

        merged_df[numeric_cols] = merged_df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        user_classifications = classify_user(merged_df)
        merged_df = merged_df.merge(user_classifications, left_on="Id", right_index=True, how="left")

        merged_df["Class"] = merged_df["Class"].fillna("Light")

        user_summaries = merged_df.groupby('Id').agg({
            'TotalSteps': 'mean',
            'Calories': 'mean',
            'SedentaryMinutes': 'mean',
            'VeryActiveMinutes': 'mean',
            'FairlyActiveMinutes': 'mean',
            'LightlyActiveMinutes': 'mean',
            'SleepMinutes': 'mean',
            'WeightKg': 'mean',
            'BMI': 'mean',
            'HeartRate': 'mean',
            'HourlyCalories': 'mean',
            'TotalIntensity': 'mean',
            'AverageIntensity': 'mean',
            'StepTotal': 'mean',
            'Class': 'first'
        }).reset_index()

        return merged_df, user_summaries

    except Exception as e:
        print(f"Error in merge_and_analyze_data: {e}")
        return None, None

#Task 10: weekdays
def activity_vs_sleep_insights(df):
    try:
        if 'DayOfWeek' not in df.columns:
            print("Error: 'DayOfWeek' column not found in merged data.")
            print("Available columns:", df.columns)
            return None

        df['Weekend'] = df['DayOfWeek'].isin(['Saturday', 'Sunday'])

        weekend_comparison = df.groupby('Weekend').agg({
            'TotalSteps': 'mean',
            'SleepMinutes': 'mean',
            'Calories': 'mean'
        }).reset_index()

        print("\nWeekend vs Weekday activity and sleep:")
        print(weekend_comparison)

        return weekend_comparison

    except Exception as e:
        print(f"Error in activity_vs_sleep_insights: {e}")
        traceback.print_exc()
        return None

# Task 11: weightlog
def analyze_weight_log(connection):
    """Analyze weight log table and handle missing values."""
    query = "SELECT * FROM weight_log"
    weight_df = SQL_acquisition(connection, query)

    for col in ['WeightKg', 'Fat', 'BMI']:
        weight_df[col] = weight_df.groupby('Id')[col].transform(lambda x: x.fillna(x.mean()))

    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Id', y='WeightKg', data=weight_df)
    plt.title('Weight Distribution by User')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    print("\nWeight Log Descriptive Statistics:")
    print(weight_df.groupby('Id')[['WeightKg', 'Fat', 'BMI']].describe())

    return weight_df

# lala's leaderboard dataframe funtion
def compute_leader_metrics(connection):
    daily_query = """
        SELECT 
            CAST(Id AS INTEGER) AS Id,
            SUM(TotalDistance) AS TotalDistance,
            SUM(TotalSteps) AS TotalSteps,
            SUM(VeryActiveMinutes) AS VeryActiveMinutes,
            SUM(Calories) AS TotalCalories
        FROM daily_activity
        GROUP BY Id
    """
    df_daily = SQL_acquisition(connection, daily_query)
    
    activity_query = """
        SELECT 
            CAST(Id AS INTEGER) AS Id,
            AVG(VeryActiveMinutes) AS AvgActiveMinutes,
            SUM(VeryActiveMinutes) AS TotalActiveMinutes,
            COUNT(ActivityDate) AS ActivityDays
        FROM daily_activity
        GROUP BY Id
    """
    df_activity = SQL_acquisition(connection, activity_query)
    
    hourly_query = """
        SELECT 
            CAST(Id AS INTEGER) AS Id,
            AVG(TotalIntensity) AS AverageIntensity
        FROM hourly_intensity
        GROUP BY Id
    """
    df_hourly = SQL_acquisition(connection, hourly_query)
    
    sleep_query = """
        SELECT 
            CAST(Id AS INTEGER) AS Id,
            COUNT(*) AS TotalRestfulSleep
        FROM minute_sleep
        WHERE value = 1
        GROUP BY Id
    """
    df_sleep = SQL_acquisition(connection, sleep_query)
    
    date_query = """
        SELECT 
            CAST(Id AS INTEGER) AS Id,
            COUNT(DISTINCT ActivityDate) AS UsageDays
        FROM daily_activity
        GROUP BY Id
    """
    df_dates = SQL_acquisition(connection, date_query)

    merged_df = df_daily.copy()

    merge_order = [df_activity, df_hourly, df_sleep, df_dates]
    for df in merge_order:
        if not df.empty and 'Id' in df.columns:
            merged_df = pd.merge(
                merged_df, df, on="Id", how="left", validate="one_to_one")
    
    merged_df = merged_df.fillna(0).replace([np.inf, -np.inf], 0)
    champions = {}
    
    if not merged_df.empty:
        metrics_map = {
            'steps_champion': 'TotalSteps',
            'distance_champion': 'TotalDistance',
            'calories_burned_champion': 'TotalCalories',
        }
        
        for champion_name, col_name in metrics_map.items():
            if col_name in merged_df.columns:
                max_idx = merged_df[col_name].idxmax()
                champions[champion_name] = {
                    'user_id': merged_df.loc[max_idx, 'Id'],
                    'value': merged_df.loc[max_idx, col_name]
                }
    
    return merged_df, champions