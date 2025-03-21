import matplotlib.cm as cm
import matplotlib.pyplot as plt
import statsmodels.api as sm
import seaborn as sns
import numpy as np
import traceback 

def ensure_columns(df, required_columns):
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Missing columns: {missing_columns}")
    return df

def plot_distance_distribution(df):
    if df.empty: 
        print('No data available.')
        return
    
    plt.figure(figsize=(12, 6))
    counts, bins, patches = plt.hist(df['Total Distance'], bins=10, edgecolor='black')
    for i in range(len(patches)):
        color = cm.YlOrRd(counts[i] / max(counts))  # Normalize count to range [0, 1] for colormap
        patches[i].set_facecolor(color)

    plt.xticks(bins, labels=[f"{int(b)}" for b in bins])
    plt.xlabel('Total Distance (km)')
    plt.ylabel('Number of Users')
    plt.title('Distribution of Total Distances Covered by 35 Users')
    plt.subplots_adjust(bottom=0.25)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.subplots_adjust(bottom=0.25)
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
    plt.subplots_adjust(bottom=0.25)
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
    plt.grid()
    plt.subplots_adjust(bottom=0.25)
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
    plt.grid()
    plt.subplots_adjust(bottom=0.25)
    plt.show()
       
def plot_sleep_vs_activity(df_merged):
    if df_merged.empty:
        print('No data available for sleep vs. activity graph.')
        return
    plt.figure(figsize=(12, 6))
    sns.regplot(x=df_merged["TotalActiveMinutes"], y= df_merged["SleepDuration"], scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    plt.xlabel("Total Active Minutes")
    plt.ylabel("Sleep Duration (hours)")
    plt.title("Regression: Sleep Duration vs. Active Minutes")
    plt.grid()
    plt.subplots_adjust(bottom=0.25)
    plt.show()
    
def plot_sleep_vs_sedentary(df_merged):
    if df_merged.empty:
        print('No data available for sleep vs. sedentary graph.')
        return
    plt.figure(figsize=(12, 6))
    sns.regplot(x=df_merged["SedentaryMinutes"], y=df_merged["SleepDuration"], scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
    plt.xlabel("Sedentary Minutes")
    plt.ylabel("Sleep Duration (hours)")
    plt.title("Regression: Sleep Duration vs. Sedentary Minutes")
    plt.grid()
    plt.subplots_adjust(bottom=0.25)
    plt.show()
        
def plot_residuals(model):
    residuals = model.resid
    if residuals.empty:
        print("No residual data available for plotting.")
        return

    plt.figure(figsize=(12, 6))
    sns.histplot(residuals, kde=True, bins=30)
    plt.xlabel("Residuals")
    plt.ylabel("Frequency")
    plt.title("Residual Distribution (Normality Check)")
    plt.grid()
    plt.subplots_adjust(bottom=0.25)
    plt.show()

    sm.qqplot(residuals, line="45", fit=True)
    plt.title("Q-Q Plot of Residuals (Normality Check)")
    plt.grid()
    plt.subplots_adjust(bottom=0.25)
    plt.show()
        
#task 5
def plot_activity_by_time_blocks(avg_steps, avg_calories, avg_sleep, labels):
    if not (avg_steps and avg_calories and avg_sleep):
        print("No data available for time block plots.")
        return
    
    x = np.arange(len(labels))
    bar_width = 0.4

    fig, axs = plt.subplots(1, 3, figsize=(12, 6))

    # Plot 1: Steps
    axs[0].bar(x, avg_steps, bar_width, color='r', label='Steps')
    axs[0].set_xlabel('Time Block')
    axs[0].set_ylabel('Steps')
    axs[0].set_title('Average Steps per 4-Hour Block')
    axs[0].set_xticks(x)
    axs[0].set_xticklabels(labels)
    axs[0].legend()

    # Plot 2: Calories
    axs[1].bar(x, avg_calories, bar_width, color='b', label='Calories')
    axs[1].set_xlabel('Time Block')
    axs[1].set_ylabel('Calories')
    axs[1].set_title('Average Calories per 4-Hour Block')
    axs[1].set_xticks(x)
    axs[1].set_xticklabels(labels)
    axs[1].legend()

    # Plot 3: Sleep
    axs[2].bar(x, avg_sleep, bar_width, color='g', label='Sleep (mins)')
    axs[2].set_xlabel('Time Block')
    axs[2].set_ylabel('Minutes')
    axs[2].set_title('Average Sleep per 4-Hour Block')
    axs[2].set_xticks(x)
    axs[2].set_xticklabels(labels)
    axs[2].legend()

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.25)
    plt.show()

#task 6    
def plot_heart_rate_and_intensity_by_id(heart_rate_df, hourly_intensity_df, user_id):
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
    plt.subplots_adjust(bottom=0.25)
    plt.show()

# Task 7
def plot_weather_and_daily_activity(df_final_activity, df_final_distance, df_final_steps):
    # Plot 1: Activity Minutes vs. Temperature
    df_final_activity.set_index("temp_bin").plot(kind="bar", stacked=False, figsize=(12,6), colormap="viridis")
    plt.xlabel("Temperature (°F)")
    plt.ylabel("Average Active Minutes")
    plt.title("Impact of Temperature on Daily Activity Levels")
    plt.xticks(rotation=45)
    plt.legend(title="Activity Type")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    # Plot 2: Total Distance vs. Temperature
    df_final_distance.set_index("temp_bin").plot(kind="bar", stacked=False, figsize=(12,6), colormap="plasma")
    plt.xlabel("Temperature (°F)")
    plt.ylabel("Average Total Distance (miles)")
    plt.title("Impact of Temperature on Daily Running Distance")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    # Ploy 3: Total Steps vs. Temp
    df_final_steps.set_index("temp_bin").plot(kind="bar", stacked=False, figsize=(12,6), colormap="plasma")
    plt.xlabel("Temperature (°F)")
    plt.ylabel("Average Total Steps")
    plt.title("Impact of Temperature on Daily Steps")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
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
    metrics = ['TotalSteps', 'Calories', 'SedentaryMinutes', 'SleepMinutes', 'WeightKg', 'BMI']

    valid_metrics = [metric for metric in metrics if metric in df_summary.columns]

    if not valid_metrics:
        print("No valid metrics to plot. Skipping visualization.")
        return

    plt.figure(figsize=(10, 5))
    for metric in valid_metrics:
        sns.lineplot(x=df_summary[group_by], y=df_summary[metric], label=metric)

    plt.xticks(rotation=45)
    plt.title(f'Statistics by {group_by}')
    plt.xlabel(group_by)
    plt.ylabel('Values')

    if valid_metrics:
        plt.legend(title='Metrics')

    plt.tight_layout()
    plt.show()
    
def plot_weekend_vs_weekday(df):
    try:
        if 'DayOfWeek' not in df.columns:
            print("Error: 'DayOfWeek' column not found in DataFrame.")
            print("Available columns:", df.columns)
            return
        
        df['Weekend'] = df['DayOfWeek'].isin(['Saturday', 'Sunday'])

        weekend_data = df.groupby('Weekend').agg({
            'TotalSteps': 'mean',
            'SleepMinutes': 'mean'
        }).reset_index()

        plt.figure(figsize=(8, 5))
        sns.barplot(x='Weekend', y='TotalSteps', data=weekend_data, color='skyblue')
        plt.title('Average Steps: Weekends vs Weekdays')
        plt.show()

        # Plot Sleep Minutes
        plt.figure(figsize=(8, 5))
        sns.barplot(x='Weekend', y='SleepMinutes', data=weekend_data, color='green')
        plt.title('Average Sleep Minutes: Weekends vs Weekdays')
        plt.show()

    except Exception as e:
        print(f"Error in plot_weekend_vs_weekday: {e}")
        traceback.print_exc()
