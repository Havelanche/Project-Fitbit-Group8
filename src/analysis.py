import traceback
import numpy as np
from scipy import stats
from visualization import plot_sleep_vs_activity, plot_sleep_vs_sedentary, plot_residuals,plot_heart_rate_and_intensity_by_id
import statsmodels.formula.api as smf
from scipy.stats import shapiro
import statsmodels.api as sm
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
    # Merge the dataframes on 'User ID' to combine Total Distance and Activity Days
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

def SQL_acquisition(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])
        return df
    except Exception as e:
        print(f"An error occurred while executing the SQL query: {e}")
        return pd.DataFrame()
    
def analyze_sleep_vs_activity(connection):
    query_sleep = """
        SELECT Id, date AS ActivityDate, SUM(value) AS SleepDuration
        FROM minute_sleep
        WHERE value > 0
        GROUP BY Id, ActivityDate
    """
    df_sleep = SQL_acquisition(connection, query_sleep)
    df_sleep["SleepDuration"] = df_sleep["SleepDuration"] / 60

    query_activity = """
        SELECT Id, ActivityDate, 
               (VeryActiveMinutes + FairlyActiveMinutes + LightlyActiveMinutes) AS TotalActiveMinutes
        FROM daily_activity
    """
    df_activity = SQL_acquisition(connection, query_activity)

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
        df_sleep = SQL_acquisition(connection, query_sleep)
        df_sleep["SleepDuration"] = df_sleep["SleepDuration"] / 60

        query_sedentary = """
            SELECT Id, ActivityDate, SedentaryMinutes
            FROM daily_activity
        """
        df_sedentary = SQL_acquisition(connection, query_sedentary)

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
    # Fetch activity & distance data from database
    df_activity = SQL_acquisition(connection, query_active)
    df_distance = SQL_acquisition(connection, query_distance)
    df_steps = SQL_acquisition(connection, query_steps)

    # Ensure date format consistency
    df_activity['ActivityDate'] = pd.to_datetime(df_activity['ActivityDate'])
    df_distance['ActivityDate'] = pd.to_datetime(df_distance['ActivityDate'])
    df_steps['ActivityDate'] = pd.to_datetime(df_steps['ActivityDate'])

    df_weather['datetime'] = pd.to_datetime(df_weather['datetime'])
    
    # Merge activity & weather data
    df_activity_merged = df_activity.merge(df_weather[['datetime', 'temp']], left_on='ActivityDate', right_on='datetime', how='inner')
    df_distance_merged = df_distance.merge(df_weather[['datetime', 'temp']], left_on='ActivityDate', right_on='datetime', how='inner')
    df_steps_merged = df_steps.merge(df_weather[['datetime', 'temp']], left_on='ActivityDate', right_on='datetime', how='inner')
    # Step 4: Create temperature bins
    temp_bins = list(range(int(df_weather['temp'].min()), int(df_weather['temp'].max()) + 5, 5))
    temp_labels = [f"{t}-{t+5}" for t in temp_bins[:-1]]

    df_activity_merged['temp_bin'] = pd.cut(df_activity_merged['temp'], bins=temp_bins, labels=temp_labels)
    df_distance_merged['temp_bin'] = pd.cut(df_distance_merged['temp'], bins=temp_bins, labels=temp_labels)
    df_steps_merged['temp_bin'] = pd.cut(df_steps_merged['temp'], bins=temp_bins, labels=temp_labels)

    # Step 5: Group by temperature bins
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
        daily_activity = pd.read_sql("SELECT Id, ActivityDate, TotalSteps, Calories, SedentaryMinutes FROM daily_activity", connection)
        minute_sleep = pd.read_sql("SELECT Id, date, value AS SleepMinutes FROM minute_sleep", connection)
        weight_log = pd.read_sql("SELECT Id, Date, WeightKg, BMI FROM weight_log", connection)

        # Convert dates to datetime (strip time for weight_log and minute_sleep)
        daily_activity['ActivityDate'] = pd.to_datetime(daily_activity['ActivityDate'], format='%m/%d/%Y', errors='coerce')
        minute_sleep['ActivityDate'] = pd.to_datetime(minute_sleep['date'].str.split().str[0], format='%m/%d/%Y', errors='coerce')
        weight_log['ActivityDate'] = pd.to_datetime(weight_log['Date'].str.split().str[0], format='%m/%d/%Y', errors='coerce')

        # Aggregate sleep minutes by Id and ActivityDate
        minute_sleep = minute_sleep.groupby(['Id', 'ActivityDate']).agg({'SleepMinutes': 'sum'}).reset_index()

        # Merge dataframes
        merged_df = pd.merge(daily_activity, minute_sleep, on=['Id', 'ActivityDate'], how='left')
        merged_df = pd.merge(merged_df, weight_log[['Id', 'ActivityDate', 'WeightKg', 'BMI']], on=['Id', 'ActivityDate'], how='left')

        print("Columns after merge:", merged_df.columns)

        # Handle missing values
        merged_df['SleepMinutes'] = merged_df['SleepMinutes'].fillna(0)
        merged_df['WeightKg'] = merged_df['WeightKg'].fillna(merged_df['WeightKg'].median(skipna=True))
        merged_df['BMI'] = merged_df['BMI'].fillna(merged_df['BMI'].median(skipna=True))

        # User-level summaries
        user_summaries = merged_df.groupby('Id').agg({
            'TotalSteps': 'mean',
            'Calories': 'mean',
            'SedentaryMinutes': 'mean',
            'SleepMinutes': 'mean',
            'WeightKg': 'mean',
            'BMI': 'mean'
        }).reset_index()

        print("\nUser-Level Activity and Health Summaries (new merge):")
        print(user_summaries)
        plt.figure(figsize=(12, 10))
        correlation_matrix = user_summaries.select_dtypes(include=[np.number]).corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                    square=True, linewidths=0.5, cbar_kws={"shrink": .8})
        plt.title('Correlation between User Metrics')
        plt.tight_layout()
        plt.show()

        return merged_df, user_summaries

    except Exception as e:
        print(f"Error in merge_and_analyze_data: {e}")
        traceback.print_exc()
        return None, None

#Task 10: weekdays
def activity_vs_sleep_insights(df):
    try:
        # Ensure DayOfWeek column exists
        if 'DayOfWeek' not in df.columns:
            print("Error: 'DayOfWeek' column not found in merged data.")
            print("Available columns:", df.columns)
            return None

        # Define weekends
        df['Weekend'] = df['DayOfWeek'].isin(['Saturday', 'Sunday'])

        # Aggregate metrics by Weekend
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
    weight_df = pd.read_sql_query(query, connection)

    # Handle missing values by filling with mean per Id
    for col in ['WeightKg', 'Fat', 'BMI']:
        weight_df[col] = weight_df.groupby('Id')[col].transform(lambda x: x.fillna(x.mean()))


    # Visualize weight distribution by user
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Id', y='WeightKg', data=weight_df)
    plt.title('Weight Distribution by User')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Show descriptive statistics for weight log
    print("\nWeight Log Descriptive Statistics:")
    print(weight_df.groupby('Id')[['WeightKg', 'Fat', 'BMI']].describe())

    return weight_df

# lala's leaderboard dataframe funtion
def compute_user_metrics(connection):
    # Get daily activity metrics
    daily_query = """
        SELECT 
            Id,
            SUM(TotalDistance) AS TotalDistance,
            SUM(VeryActiveDistance) AS VeryActiveDistance,
            SUM(VeryActiveMinutes) AS VeryActiveMinutes,
            SUM(Calories) AS TotalCalories
        FROM daily_activity
        GROUP BY Id
    """
    df_daily = SQL_acquisition(connection, daily_query)
    
    # Get hourly intensity metrics
    hourly_query = """
        SELECT 
            Id,
            SUM(TotalIntensity) AS TotalIntensity
        FROM hourly_intensity
        GROUP BY Id
    """
    df_hourly = SQL_acquisition(connection, hourly_query)
    
    # Get sleep metrics (count of value=1)
    sleep_query = """
        SELECT 
            Id,
            COUNT(*) AS TotalRestfulSleep
        FROM minute_sleep
        WHERE value = 1
        GROUP BY Id
    """
    df_sleep = SQL_acquisition(connection, sleep_query)
    
    # Check for empty results
    if df_daily.empty and df_hourly.empty and df_sleep.empty:
        print("No data found in any tables")
        return pd.DataFrame()
    
    # Merge all dataframes
    merged_df = df_daily.copy()
    
    # Convert IDs to string type for consistency
    for df in [merged_df, df_hourly, df_sleep]:
        if not df.empty:
            df["Id"] = df["Id"].astype(str)
    
    # Perform merges
    if not df_hourly.empty:
        merged_df = pd.merge(merged_df, df_hourly, on="Id", how="left")
    if not df_sleep.empty:
        merged_df = pd.merge(merged_df, df_sleep, on="Id", how="left")
    
    # Fill missing values with 0
    merged_df = merged_df.fillna(0)
    
    # Find user with maximum distance
    if not merged_df.empty:
        max_distance_user = merged_df.loc[merged_df['TotalDistance'].idxmax()]
        print(f"User with longest total distance: {max_distance_user['Id']} ({max_distance_user['TotalDistance']} km)")
    
    return merged_df
