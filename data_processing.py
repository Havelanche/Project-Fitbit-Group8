import pandas as pd 

def load_data(filename):
    df = pd.read_csv(filename, sep=';')  
    df.columns = df.columns.str.strip()  
    print("Cleaned Columns:", df.columns.tolist()) 
    if 'ActivityDate' in df.columns:
        df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], errors='coerce')
    else:
        print("Error: 'ActivityDate' column not found!")
    return df

#first-change: add a new parameter "str" to customize the prints data
def get_unique_users(df, str):
    unique_users = df.groupby('Id')[str].sum().reset_index()
    
    # second-change: Let the index start from 1 & change the prints (no '.head()' & name of index column)
    unique_users.insert(0, 'Index', range(1, len(unique_users) + 1))
    unique_users.columns = ['#Users', 'User ID', str]
    print(unique_users)
    return unique_users