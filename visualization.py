import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from database import SQL_acquisition
import statsmodels.api as sm


def plot_distance_distribution(df):
    plt.figure(figsize=(12, 6))
    counts, bins, patches = plt.hist(df['TotalDistance'], bins=10, color='orange', edgecolor='black')
    plt.xticks(bins.round(1))

    plt.xlabel('Total Distance')
    plt.ylabel('Number of Users')
    plt.title('Distribution of Total Distances Covered by 35 Users')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

def calories_burned_per_day(df, user_id, start_date=None, end_date=None):
    user_data = df[df['Id'] == user_id]
    if start_date and end_date:
        user_data = user_data[(user_data['ActivityDate']>=start_date) &  (user_data['ActivityDate'] <= end_date)]
    
    plt.figure(figsize=(12,6))
    plt.plot(user_data['ActivityDate'], user_data['Calories'], marker='o',linestyle='-')
    plt.xlabel('Day')
    plt.ylabel('Total calories burned')
    plt.title(f'Total calories burned by User {user_id}')
    plt.xticks(rotation=45) 
    plt.grid()
    plt.show()
    
def plot_workout(df):
    df['DayOfWeek'] = df['ActivityDate'].dt.day_name()
    plt.figure(figsize=(12, 6))
    sns.countplot(x='DayOfWeek', data=df, order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], palette='pastel', hue='DayOfWeek', legend=False)
    plt.xlabel('Day of the week')
    plt.ylabel('Workout Count by Day')
    plt.title('Weekly Workout Frequency')
    plt.xticks(rotation=45) 
    plt.show()

def plot_LRM(df, user_id):
    user = df[df['Id'] == str(user_id)]
    plt.figure(figsize=(12,6))
    sns.regplot(x='TotalSteps', y='Calories', data=user, scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    plt.xlabel('Total Steps')
    plt.ylabel('Calories Burned')
    plt.title(f'Calories vs. Steps for User {user_id}')
    plt.show()
    
def time_block_analysis(connection):
    query = '''
    SELECT strftime('%H', ActivityHour) AS hour_block, 
           AVG(StepTotal) AS avg_steps,
           AVG(Calories) AS avg_calories
    FROM hourly_steps
    JOIN hourly_calories USING (Id, ActivityHour)
    GROUP BY hour_block
    ORDER BY hour_block
    '''
    df = SQL_acquisition(connection, query)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x='hour_block', y='avg_steps', data=df, color='blue', label='Avg Steps')
    plt.twinx()
    sns.lineplot(x='hour_block', y='avg_calories', data=df, color='orange', label='Avg Calories')
    plt.title('Average Steps and Calories by Time Block')
    plt.show()

def plot_heart_rate_intensity(connection, user_id):
    query = f'''
    SELECT h.Time, h.Value AS HeartRate, i.TotalIntensity
    FROM heart_rate h
    JOIN hourly_intensity i ON h.Id = i.Id 
    AND strftime('%H:%M', h.Time) = strftime('%H:%M', i.ActivityHour)
    WHERE h.Id = "{user_id}"
    '''
    df = SQL_acquisition(connection, query)

    if df.empty:
        print(f"No heart rate or intensity data found for user {user_id}.")
        return

    # Convert Time to datetime for plotting
    df['Time'] = pd.to_datetime(df['Time'])

    plt.figure(figsize=(12, 6))
    plt.plot(df['Time'], df['HeartRate'], label='Heart Rate', color='red')
    plt.plot(df['Time'], df['TotalIntensity'], label='Total Intensity', color='blue')
    plt.title(f'Heart Rate and Intensity for User {user_id}')
    plt.legend()
    plt.xticks(rotation=45)
    plt.show()
def calories_vs_heart_rate(connection):
    query = '''
    SELECT hr.Id, hr.Time, hr.Value AS HeartRate, hc.Calories
    FROM heart_rate hr
    JOIN hourly_calories hc ON hr.Id = hc.Id AND strftime('%H:%M', hr.Time) = strftime('%H:%M', hc.ActivityHour)
    '''
    df = SQL_acquisition(connection, query)
    model = sm.OLS(df['Calories'], sm.add_constant(df['HeartRate'])).fit()
    print(model.summary())
    sns.scatterplot(data=df, x='HeartRate', y='Calories')
    plt.title('Calories vs. Heart Rate')
    plt.show()
    
def time_block_analysis(connection):
    query = '''
    SELECT strftime('%H', ActivityHour) AS hour_block, 
           AVG(StepTotal) AS avg_steps,
           AVG(Calories) AS avg_calories
    FROM hourly_steps
    JOIN hourly_calories USING (Id, ActivityHour)
    GROUP BY hour_block
    ORDER BY hour_block
    '''
    df = SQL_acquisition(connection, query)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x='hour_block', y='avg_steps', data=df, color='blue', label='Avg Steps')
    plt.twinx()
    sns.lineplot(x='hour_block', y='avg_calories', data=df, color='orange', label='Avg Calories')
    plt.title('Average Steps and Calories by Time Block')
    plt.show()

def plot_heart_rate_intensity(connection, user_id):
    query = f'''
    SELECT h.Time, h.Value AS HeartRate, i.TotalIntensity
    FROM heart_rate h
    JOIN hourly_intensity i ON h.Id = i.Id AND strftime('%H:%M', h.Time) = strftime('%H:%M', i.ActivityHour)
    WHERE h.Id = "{user_id}"
    '''
    df = SQL_acquisition(connection, query)
    
    if df.empty:
        print(f"No heart rate or intensity data found for user {user_id}.")
        return

    df['Time'] = pd.to_datetime(df['Time'])

    plt.figure(figsize=(12, 6))
    plt.plot(df['Time'], df['HeartRate'], label='Heart Rate', color='red')
    plt.plot(df['Time'], df['TotalIntensity'], label='Total Intensity', color='blue')
    plt.title(f'Heart Rate and Intensity for User {user_id}')
    plt.legend()
    plt.xticks(rotation=45)
    plt.show()