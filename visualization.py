import traceback
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
import matplotlib.cm as cm
import seaborn as sns
import numpy as np
from database import SQL_acquisition

def plot_distance_distribution(df):
    if df.empty: 
        print('No data available.')
        return
    
    plt.figure(figsize=(12, 6))
    counts, bins, patches = plt.hist(df['Total Distance'], bins=10, edgecolor='black')
    # Apply colormap to each patch based on its height (the number of users in each bin)
    for i in range(len(patches)):
        color = cm.YlOrRd(counts[i] / max(counts))  # Normalize count to range [0, 1] for colormap
        patches[i].set_facecolor(color)

    plt.xticks(bins, labels=[f"{int(b)}" for b in bins])
    plt.xlabel('Total Distance (km)')
    plt.ylabel('Number of Users')
    plt.title('Distribution of Total Distances Covered by 35 Users')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

def calories_burned_per_day(df, user_id, start_date=None, end_date=None):
    user_data = df[df['Id'] == user_id]
    if start_date and end_date:
        user_data = user_data[(user_data['ActivityDate']>=start_date) &  (user_data['ActivityDate'] <= end_date)]
    
    if user_data.empty:
        print(f'No data available for User {user_id} between {start_date} and {end_date}.')
        return
    
    plt.figure(figsize=(12,6))
    plt.plot(user_data['ActivityDate'], user_data['Calories'], marker='o',linestyle='-')
    plt.xlabel('Day')
    plt.ylabel('Total calories burned')
    plt.title(f'Total calories burned by User {user_id}')
    plt.xticks(rotation=45) 
    plt.grid()
    plt.show()
    
def plot_workout(df):
    if df.empty:
        print('No data available for workout graph.')
        return
    
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
    
    if user.empty:
        print(f'No data available for User {user_id}.')
        return
    
    plt.figure(figsize=(12,6))
    sns.regplot(x='TotalSteps', y='Calories', data=user, scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    plt.xlabel('Total Steps')
    plt.ylabel('Calories Burned')
    plt.title(f'Calories vs. Steps for User {user_id}')
    plt.show()
       
def plot_sleep_vs_activity(df_merged):
    if df_merged.empty:
        print('No data available for sleep vs. activity graph.')
        return
    plt.figure(figsize=(8, 5))
    sns.regplot(x=df_merged["TotalActiveMinutes"], y= df_merged["SleepDuration"], scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    plt.xlabel("Total Active Minutes")
    plt.ylabel("Sleep Duration (hours)")
    plt.title("Regression: Sleep Duration vs. Active Minutes")
    plt.show()
    
def plot_sleep_vs_sedentary(df_merged):
    if df_merged.empty:
        print('No data available for sleep vs. sedentary graph.')
        return
    plt.figure(figsize=(8, 5))
    sns.regplot(x=df_merged["SedentaryMinutes"], y=df_merged["SleepDuration"], scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    plt.xlabel("Sedentary Minutes")
    plt.ylabel("Sleep Duration (hours)")
    plt.title("Regression: Sleep Duration vs. Sedentary Minutes")
    plt.show()
        
def plot_residuals(model):
    residuals = model.resid
    if residuals.empty:
        print("No residual data available for plotting.")
        return

    plt.figure(figsize=(8, 5))
    sns.histplot(residuals, kde=True, bins=30)
    plt.xlabel("Residuals")
    plt.ylabel("Frequency")
    plt.title("Residual Distribution (Normality Check)")
    plt.show()

    sm.qqplot(residuals, line="45", fit=True)
    plt.title("Q-Q Plot of Residuals (Normality Check)")
    plt.show()
        
#task 5
def plot_activity_by_time_blocks(avg_steps, avg_calories, avg_sleep, labels):
    if not (avg_steps and avg_calories and avg_sleep):
        print("No data available for time block plots.")
        return
    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(10, 6))

    bar_width = 0.2
    ax.bar(x - bar_width, avg_steps, bar_width, label='Steps', color='r')
    ax.bar(x, avg_calories, bar_width, label='Calories', color='b')
    ax.bar(x + bar_width, avg_sleep, bar_width, label='Sleep (mins)', color='g')

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

#task 6    
def plot_heart_rate_and_intensity_by_id(heart_rate_df, hourly_intensity_df, user_id):
    # if heart_rate_df.empty or hourly_intensity_df.empty:
    #     print(f"No heart rate or intensity data available for User {user_id}.")
    #     return
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.set_xlabel('Time')
    ax1.set_ylabel('Heart Rate (bpm)', color='b')
    ax1.plot(heart_rate_df['Time'], heart_rate_df['Value'], color='b', label='Heart Rate')
    ax1.tick_params(axis='y', labelcolor='b')
    ax2 = ax1.twinx()
    ax2.set_ylabel('Total Intensity', color='g')
    ax2.plot(hourly_intensity_df['ActivityHour'], hourly_intensity_df['TotalIntensity'], color='g', label='Total Intensity')
    ax2.tick_params(axis='y', labelcolor='g')

    fig.suptitle(f'Heart Rate and Total Exercise Intensity for User {user_id}', fontsize=14)
    plt.tight_layout()
    plt.show()
    
def plot_grouped_data(df_grouped, metric='TotalSteps', group_by='Id'):
    plt.figure(figsize=(12, 6))
    sns.barplot(x=group_by, y=metric, hue=group_by, data=df_grouped, palette='viridis', legend=False)
    plt.xticks(rotation=45)
    plt.title(f'Average {metric} by {group_by}')
    plt.xlabel(group_by)
    plt.ylabel(f'Average {metric}')
    plt.tight_layout()
    plt.show()

def plot_statistical_summary(df_summary, group_by='Id'):
    metrics = ['TotalSteps_mean', 'Calories_mean', 'SedentaryMinutes_mean', 'SleepMinutes_mean', 'WeightKg_mean', 'BMI_mean']

    plt.figure(figsize=(10, 5))
    for metric in metrics:
        if metric in df_summary.columns:
            sns.lineplot(x=df_summary[group_by], y=df_summary[metric], label=metric)

    plt.xticks(rotation=45)
    plt.title(f'Statistics by {group_by}')
    plt.xlabel(group_by)
    plt.ylabel('Values')
    plt.legend(title='Metrics')
    plt.tight_layout()
    plt.show()

def calories_vs_heart_rate(connection):
    try:
        print("Running calories_vs_heart_rate...")

        query = '''
        SELECT hr.Id, hr.Time, hr.Value AS HeartRate, hc.Calories
        FROM heart_rate hr
        JOIN hourly_calories hc ON hr.Id = hc.Id 
        AND strftime('%H:%M', hr.Time) = strftime('%H:%M', hc.ActivityHour)
        '''
        df = SQL_acquisition(connection, query)
        if df.empty:
            print("No data available for Calories vs. Heart Rate.")
            return

        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        df.dropna(subset=['HeartRate', 'Calories'], inplace=True)

        if df[['HeartRate', 'Calories']].isnull().all().any():
            print("Insufficient data for modeling.")
            return

        model = sm.OLS(df['Calories'], sm.add_constant(df['HeartRate'])).fit()
        print(model.summary())

        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df, x='HeartRate', y='Calories', color='blue', alpha=0.6)
        sns.regplot(data=df, x='HeartRate', y='Calories', scatter=False, color='red')
        plt.title('Calories vs. Heart Rate')
        plt.xlabel('Heart Rate (bpm)')
        plt.ylabel('Calories Burned')
        plt.grid(True)
        plt.tight_layout() 
        plt.show()

    except Exception as e:
        print(f"Error in calories_vs_heart_rate: {e}")
        traceback.print_exc()
        
def plot_weekend_vs_weekday(df):
    try:
        plt.figure(figsize=(8, 5))
        sns.barplot(x='Weekend', y='TotalSteps_mean', data=df)
        plt.title('Average Steps: Weekends vs Weekdays')
        plt.show()

        plt.figure(figsize=(8, 5))
        sns.barplot(x='Weekend', y='SleepMinutes_mean', data=df)
        plt.title('Average Sleep Minutes: Weekends vs Weekdays')
        plt.show()
    
    except Exception as e:
        print(f"Error in plot_weekend_vs_weekday: {e}")