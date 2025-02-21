import matplotlib.pyplot as plt
import seaborn as sns

def plot_distance_distribution(df):
    unique_users = df.groupby('Id')['TotalDistance'].sum().reset_index()
    plt.figure(figsize=(12, 6))

    # third-change: add a function call here to generate a new "unique_users", so that the get_unique_users() function can work seperately
    unique_users = unique_users(df, "TotalDistance")
    counts, bins, patches = plt.hist(unique_users['TotalDistance'], bins=10, color='orange', edgecolor='black')
    # plt.xticks(bins, labels=[f"{int(b)}" for b in bins])
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