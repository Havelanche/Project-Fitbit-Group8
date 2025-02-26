import statsmodels.formula.api as smf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

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
    # fourth-change: DELETE " 'Id': user_counts.index, " for cutting the redundancy
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
    correlation = merged_df['Total Distance'].corr(merged_df['Activity Days'])
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

def analyze_correlation(unique_user_distance, user_activity_days):
    # Merge the dataframes on 'User ID' to combine Total Distance and Activity Days
    merged_df = pd.merge(unique_user_distance, user_activity_days, on='User ID')

    # Calculate Pearson correlation between Total Distance and Activity Days
    correlation = merged_df['Total Distance'].corr(merged_df['Activity Days'])
    print(f"\nPearson correlation between Total Distance and Activity Days: {correlation}")

    # Scatter plot to visualize the relationship
    plt.figure(figsize=(12, 6))
    plt.scatter(merged_df['Activity Days'], merged_df['Total Distance'], c=merged_df['Total Distance'], cmap='YlOrRd', edgecolor='black')
    plt.colorbar(label='Total Distance')  # Add color bar to indicate distance
    plt.xlabel('Activity Days')
    plt.ylabel('Total Distance')
    plt.title('Scatter Plot of Total Distance vs. Activity Days')
    plt.grid(True)
    plt.show()

    return merged_df
