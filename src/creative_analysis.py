import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

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

# ---- Main Execution ----

user_activity_days, top_5_users = check_activity_days(cleaned_data)
merge_df_distance_days = distance_days_correlation(unique_user_distance, user_activity_days)
# analyze_correlation(unique_user_distance, user_activity_days)