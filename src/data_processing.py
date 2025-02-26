import pandas as pd 

def load_data(filename):
    df = pd.read_csv(filename)
    df['ActivityDate'] = pd.to_datetime(df['ActivityDate'])
    return df

#first-change: add a new parameter "str" to customize the prints data
def get_unique_users(df, str):
    unique_users = df.groupby('Id')[str].sum().reset_index()
    unique_users.insert(0, 'Index', range(1, len(unique_users) + 1))
    unique_users.columns = ['#Users', 'User ID', str]
    print(unique_users)
    return unique_users

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