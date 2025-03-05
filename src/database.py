import sqlite3 as sql
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import seaborn as sns


# db_name="fitbit_database.db"

def connect_db(db_name): 
    return sql.connect(db_name)


def SQL_acquisition(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])
    return df
    

def verify_total_steps(df, connection):
    df_database = SQL_acquisition(connection, f"SELECT Id, sum(StepTotal) AS total_steps FROM hourly_steps GROUP BY Id")
    df_csv = df.groupby('Id')['TotalSteps'].sum().reset_index()

    identical = df_database['total_steps'].equals(df_csv['TotalSteps'])
    print("If the total steps in csv file is indentical as in database?:", identical)
    

def safe_sql_query(connection, query, params=None):
    try:
        df = SQL_acquisition(connection, query)
        return df
    except Exception as e:
        print(f"An error occurred while executing the SQL query: {e}")
        return pd.DataFrame()
    

def compute_sleep_duration(connection):
    query = """
        SELECT Id, logId, COUNT(*) AS SleepDuration
        FROM minute_sleep
        GROUP BY Id, logId
        ORDER BY Id, logId
    """
    df_sleep = safe_sql_query(connection, query)

    if df_sleep.empty:
        print("No sleep data found in database.")
        return pd.DataFrame()
    
    df_sleep["logId"] = df_sleep["logId"].astype(str)
    df_sleep["Id"] = df_sleep["Id"].astype(str)
    print("Computed Sleep Duration per User and Session:")
    print(df_sleep.head(10))

    return df_sleep


def analyze_sleep_vs_activity(connection):
    """Analyze the relationship between sleep duration and total active minutes."""

    # Query: Compute daily sleep duration in minutes
    query_sleep = """
        SELECT Id, date AS ActivityDate, SUM(value) AS SleepDuration
        FROM minute_sleep
        WHERE value > 0
        GROUP BY Id, ActivityDate
    """
    df_sleep = pd.read_sql_query(query_sleep, connection)

    # Convert sleep duration to hours for better interpretation
    df_sleep["SleepDuration"] = df_sleep["SleepDuration"] / 60  

    # Query: Compute total active minutes per day
    query_activity = """
        SELECT Id, ActivityDate, 
               (VeryActiveMinutes + FairlyActiveMinutes + LightlyActiveMinutes) AS TotalActiveMinutes
        FROM daily_activity
    """
    df_activity = pd.read_sql_query(query_activity, connection)

    # Convert Id and ActivityDate to string for safe merging
    df_sleep["Id"] = df_sleep["Id"].astype(str)
    df_activity["Id"] = df_activity["Id"].astype(str)
    df_sleep["ActivityDate"] = pd.to_datetime(df_sleep["ActivityDate"]).dt.date.astype(str)
    df_activity["ActivityDate"] = pd.to_datetime(df_activity["ActivityDate"]).dt.date.astype(str)

    # Merge datasets on Id and ActivityDate
    df_merged = df_activity.merge(df_sleep, on=["Id", "ActivityDate"], how="inner")

    # Perform regression analysis: SleepDuration ~ TotalActiveMinutes
    model = smf.ols("SleepDuration ~ TotalActiveMinutes", data=df_merged).fit()
    print(model.summary())

    # Plot regression results
    plt.figure(figsize=(8, 5))
    sns.regplot(x=df_merged["TotalActiveMinutes"], y=df_merged["SleepDuration"], 
                scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    plt.xlabel("Total Active Minutes")
    plt.ylabel("Sleep Duration (hours)")
    plt.title("Regression: Sleep Duration vs. Active Minutes")
    plt.show()

    return df_merged, model


def analyze_sleep_vs_sedentary(connection):
    try:
        
        # Query: Compute daily sleep duration in minutes
        query_sleep = """
            SELECT Id, date AS ActivityDate, SUM(value) AS SleepDuration
            FROM minute_sleep
            WHERE value > 0
            GROUP BY Id, ActivityDate
        """
        df_sleep = pd.read_sql_query(query_sleep, connection)

        # Convert sleep duration to hours
        df_sleep["SleepDuration"] = df_sleep["SleepDuration"] / 60  

        # Query: Compute daily sedentary minutes
        query_sedentary = """
            SELECT Id, ActivityDate, SedentaryMinutes
            FROM daily_activity
        """
        df_sedentary = pd.read_sql_query(query_sedentary, connection)

        # Convert Id and ActivityDate to string for safe merging
        df_sleep["Id"] = df_sleep["Id"].astype(str)
        df_sedentary["Id"] = df_sedentary["Id"].astype(str)
        df_sleep["ActivityDate"] = pd.to_datetime(df_sleep["ActivityDate"]).dt.date.astype(str)
        df_sedentary["ActivityDate"] = pd.to_datetime(df_sedentary["ActivityDate"]).dt.date.astype(str)

        # Merge datasets on Id and ActivityDate
        df_merged = df_sedentary.merge(df_sleep, on=["Id", "ActivityDate"], how="inner")

        # Check if merge resulted in an empty dataset
        if df_merged.empty:
            print(" Error: Merged dataframe is empty! Check date format in `minute_sleep` and `daily_activity`.")
            return None

        # Perform regression analysis: SleepDuration ~ SedentaryMinutes
        model = smf.ols("SleepDuration ~ SedentaryMinutes", data=df_merged).fit()

        # Display regression summary
        print(model.summary())

        # Plot regression results
        plt.figure(figsize=(8, 5))
        sns.regplot(x=df_merged["SedentaryMinutes"], y=df_merged["SleepDuration"], 
                    scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
        plt.xlabel("Sedentary Minutes")
        plt.ylabel("Sleep Duration (hours)")
        plt.title("Regression: Sleep Duration vs. Sedentary Minutes")
        plt.show()

        # Residual analysis to check normality
        residuals = model.resid

        # Histogram of residuals
        plt.figure(figsize=(8, 5))
        sns.histplot(residuals, kde=True, bins=30)
        plt.xlabel("Residuals")
        plt.ylabel("Frequency")
        plt.title("Residual Distribution (Normality Check)")
        plt.show()

        # Q-Q plot to check normality visually
        sm.qqplot(residuals, line="45", fit=True)
        plt.title("Q-Q Plot of Residuals (Normality Check)")
        plt.show()

        # Perform Shapiro-Wilk test for normality
        shapiro_test_stat, shapiro_p_value = shapiro(residuals.sample(5000, random_state=42))  # Take a sample to avoid large data issue
        print(f"\nShapiro-Wilk Test for Normality:")
        print(f"Test Statistic = {shapiro_test_stat:.4f}, p-value = {shapiro_p_value:.6f}")

        if shapiro_p_value < 0.05:
            print(" Residuals are normally distributed (p-value < 0.05). Consider transformations or a different model.")
        else:
            print(" Residuals appear normally distributed (p-value >= 0.05).")

        return model

    except Exception as e:
        print(f"⚠️ An error occurred: {e}")
        return None
    

def plot_activity_by_time_blocks_from_db(connection):
 
    # Query the hourly steps, calories, and minute sleep data
    hourly_steps_query = "SELECT * FROM hourly_steps;"
    hourly_calories_query = "SELECT * FROM hourly_calories;"
    minute_sleep_query = "SELECT * FROM minute_sleep;"
    
    # Load the data into DataFrames
    hourly_steps_df = pd.read_sql(hourly_steps_query, connection)
    hourly_calories_df = pd.read_sql(hourly_calories_query, connection)
    minute_sleep_df = pd.read_sql(minute_sleep_query, connection)
        
    # Convert ActivityHour and date to datetime format for easier processing
    hourly_steps_df['ActivityHour'] = pd.to_datetime(hourly_steps_df['ActivityHour'])
    hourly_calories_df['ActivityHour'] = pd.to_datetime(hourly_calories_df['ActivityHour'])
    minute_sleep_df['date'] = pd.to_datetime(minute_sleep_df['date'])

    # Extract hour from the 'ActivityHour' for hourly data and from 'date' for minute sleep data
    hourly_steps_df['hour'] = hourly_steps_df['ActivityHour'].dt.hour
    hourly_calories_df['hour'] = hourly_calories_df['ActivityHour'].dt.hour
    minute_sleep_df['hour'] = minute_sleep_df['date'].dt.hour

    # Define the 4-hour time blocks
    time_blocks = [(0, 4), (4, 8), (8, 12), (12, 16), (16, 20), (20, 24)]

    # Initialize lists to store the average steps, calories, and sleep per block
    avg_steps = []
    avg_calories = []
    avg_sleep = []

    # Calculate average steps per block
    for start, end in time_blocks:
        block_steps = hourly_steps_df[(hourly_steps_df['hour'] >= start) & (hourly_steps_df['hour'] < end)]
        avg_steps.append(block_steps['StepTotal'].mean())

    # Calculate average calories per block
    for start, end in time_blocks:
        block_calories = hourly_calories_df[(hourly_calories_df['hour'] >= start) & (hourly_calories_df['hour'] < end)]
        avg_calories.append(block_calories['Calories'].mean())

    # Calculate average sleep minutes per block
    for start, end in time_blocks:
        block_sleep = minute_sleep_df[(minute_sleep_df['hour'] >= start) & (minute_sleep_df['hour'] < end)]
        avg_sleep.append(block_sleep['value'].sum() / 60)  # Converting to minutes by dividing by 60

    # Plotting the results
    labels = [f"{start}-{end}" for start, end in time_blocks]
    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(10, 6))

    bar_width = 0.2
    ax.bar(x - bar_width, avg_steps, bar_width, label='Steps', color='b')
    ax.bar(x, avg_calories, bar_width, label='Calories', color='g')
    ax.bar(x + bar_width, avg_sleep, bar_width, label='Sleep (mins)', color='r')

    # Adding labels and title
    ax.set_xlabel('Time Block')
    ax.set_ylabel('Average')
    ax.set_title('Average Steps, Calories, and Sleep per 4-Hour Block')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    # Show the plot
    plt.tight_layout()
    plt.show()   


def plot_heart_rate_and_intensity_by_id(connection, user_id):
    
    # Query the heart rate and hourly intensity data for the specific user
    heart_rate_query = f"SELECT * FROM heart_rate WHERE Id = {user_id};"
    hourly_intensity_query = f"SELECT * FROM hourly_intensity WHERE Id = {user_id};"
    
    # Load the data into DataFrames
    heart_rate_df = pd.read_sql(heart_rate_query, connection)
    hourly_intensity_df = pd.read_sql(hourly_intensity_query, connection)
    
    # Convert the 'Time' column in heart rate data to datetime
    heart_rate_df['Time'] = pd.to_datetime(heart_rate_df['Time'])
    
    # Convert 'ActivityHour' column in intensity data to datetime
    hourly_intensity_df['ActivityHour'] = pd.to_datetime(hourly_intensity_df['ActivityHour'])
    
    # Plotting the heart rate and total intensity on the same figure
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Plot the heart rate data (in blue)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Heart Rate (bpm)', color='b')
    ax1.plot(heart_rate_df['Time'], heart_rate_df['Value'], color='b', label='Heart Rate')
    ax1.tick_params(axis='y', labelcolor='b')
    
    # Create a second y-axis for total intensity
    ax2 = ax1.twinx()
    ax2.set_ylabel('Total Intensity', color='g')
    ax2.plot(hourly_intensity_df['ActivityHour'], hourly_intensity_df['TotalIntensity'], color='g', label='Total Intensity')
    ax2.tick_params(axis='y', labelcolor='g')
    
    # Adding a title
    fig.suptitle(f'Heart Rate and Total Exercise Intensity for User {user_id}', fontsize=14)
    
    # Show the plot
    plt.tight_layout()
    plt.show()

    # Return the figure
    return fig



import pandas as pd
import matplotlib.pyplot as plt

def discover_weather_impact(connection, CHICAGO_WEATHER):
    query_active = """
    SELECT ActivityDate, AVG(LightlyActiveMinutes) AS LightlyActive, 
    AVG(FairlyActiveMinutes) AS FairlyActive, 
    AVG(VeryActiveMinutes) AS VeryActive
    FROM daily_activity GROUP BY ActivityDate
    """
    query_distance = """
    SELECT ActivityDate, AVG(TotalDistance) AS TotalDistance FROM daily_activity GROUP BY ActivityDate
    """

    # Fetch activity & distance data from database
    df_activity = SQL_acquisition(connection, query_active)
    df_distance = SQL_acquisition(connection, query_distance)

    # Load weather data from CSV
    df_weather = pd.read_csv(CHICAGO_WEATHER)  

    # Ensure date format consistency
    df_activity['ActivityDate'] = pd.to_datetime(df_activity['ActivityDate'])
    df_distance['ActivityDate'] = pd.to_datetime(df_distance['ActivityDate'])  # Fix: Use df_distance, not df_activity
    df_weather['datetime'] = pd.to_datetime(df_weather['datetime'])
    
    # Merge activity & weather data
    df_activity_merged = df_activity.merge(df_weather[['datetime', 'temp']], left_on='ActivityDate', right_on='datetime', how='inner')
    df_distance_merged = df_distance.merge(df_weather[['datetime', 'temp']], left_on='ActivityDate', right_on='datetime', how='inner')

    # Step 4: Create temperature bins
    temp_bins = list(range(int(df_weather['temp'].min()), int(df_weather['temp'].max()) + 5, 5))
    temp_labels = [f"{t}-{t+5}" for t in temp_bins[:-1]]

    df_activity_merged['temp_bin'] = pd.cut(df_activity_merged['temp'], bins=temp_bins, labels=temp_labels)
    df_distance_merged['temp_bin'] = pd.cut(df_distance_merged['temp'], bins=temp_bins, labels=temp_labels)

    # Step 5: Group by temperature bins
    df_final_activity = df_activity_merged.groupby('temp_bin')[['LightlyActive', 'FairlyActive', 'VeryActive']].mean().reset_index()
    df_final_distance = df_distance_merged.groupby('temp_bin')[['TotalDistance']].mean().reset_index()

    # **Plot 1: Activity Minutes vs. Temperature**
    df_final_activity.set_index("temp_bin").plot(kind="bar", stacked=False, figsize=(12,6), colormap="viridis")
    plt.xlabel("Temperature (°F)")
    plt.ylabel("Average Active Minutes")
    plt.title("Impact of Temperature on Daily Activity Levels")
    plt.xticks(rotation=45)
    plt.legend(title="Activity Type")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    # **Plot 2: Total Distance vs. Temperature**
    df_final_distance.set_index("temp_bin").plot(kind="bar", stacked=False, figsize=(12,6), colormap="plasma")
    plt.xlabel("Temperature (°F)")
    plt.ylabel("Average Total Distance (miles)")
    plt.title("Impact of Temperature on Daily Running Distance")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()
