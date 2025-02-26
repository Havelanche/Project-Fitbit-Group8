from visualization import plot_sleep_vs_activity, plot_sleep_vs_sedentary, plot_residuals,plot_heart_rate_and_intensity_by_id, plot_activity_by_time_blocks
from data_processing import calculate_time_block_averages
import statsmodels.formula.api as smf
from scipy.stats import shapiro
import pandas as pd


def classify_user(df):
    user_counts = df.groupby('Id').size()
    categories = pd.cut(user_counts, bins=[0, 10, 15, float('inf')], labels=['Light', 'Moderate', 'Heavy'])
    return pd.DataFrame({'Class': categories})

def linear_regression(df):
    df['Id'] = df['Id'].astype(str)
    model = smf.ols('Calories ~ TotalSteps + C(Id)', data=df).fit()
    return model

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

        # Merge and format data
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

def get_activity_by_time_blocks(connection):
    hourly_steps_query = "SELECT * FROM hourly_steps;"
    hourly_calories_query = "SELECT * FROM hourly_calories;"
    minute_sleep_query = "SELECT * FROM minute_sleep;"

    hourly_steps_df = pd.read_sql(hourly_steps_query, connection)
    hourly_calories_df = pd.read_sql(hourly_calories_query, connection)
    minute_sleep_df = pd.read_sql(minute_sleep_query, connection)

    hourly_steps_df['ActivityHour'] = pd.to_datetime(hourly_steps_df['ActivityHour'])
    hourly_calories_df['ActivityHour'] = pd.to_datetime(hourly_calories_df['ActivityHour'])
    minute_sleep_df['date'] = pd.to_datetime(minute_sleep_df['date'])
    
    hourly_steps_df['hour'] = hourly_steps_df['ActivityHour'].dt.hour
    hourly_calories_df['hour'] = hourly_calories_df['ActivityHour'].dt.hour
    minute_sleep_df['hour'] = minute_sleep_df['date'].dt.hour

    avg_steps, avg_calories, avg_sleep, labels = calculate_time_block_averages(
        hourly_steps_df, hourly_calories_df, minute_sleep_df
    )

    plot_activity_by_time_blocks(avg_steps, avg_calories, avg_sleep, labels)
    return hourly_steps_df, hourly_calories_df, minute_sleep_df


# TASK 6: HEART RATE & INTENSITY
def get_heart_rate_and_intensity(connection, user_id):
    heart_rate_query = f"SELECT * FROM heart_rate WHERE Id = {user_id};"
    hourly_intensity_query = f"SELECT * FROM hourly_intensity WHERE Id = {user_id};"

    heart_rate_df = pd.read_sql(heart_rate_query, connection)
    hourly_intensity_df = pd.read_sql(hourly_intensity_query, connection)

    heart_rate_df['Time'] = pd.to_datetime(heart_rate_df['Time'])
    hourly_intensity_df['ActivityHour'] = pd.to_datetime(hourly_intensity_df['ActivityHour'])

    plot_heart_rate_and_intensity_by_id(heart_rate_df, hourly_intensity_df, user_id)
