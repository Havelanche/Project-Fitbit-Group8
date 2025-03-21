import pandas as pd

def load_and_preview_data(df):
    df = pd.read_csv(df)  
    print("\nFirst 5 rows of the dataset:")
    print(df.head())
    print("\nSummary Statistics:")
    print(df.describe(include="all"))
    print("\nOriginal Data Preview Done.")
    return df

def clean_and_transform_data(df):
    print(f"\nColumns in dataset: {df.columns}")
    
    if "ActivityDate" not in df.columns:
        raise ValueError("Column 'ActivityDate' not found. Check dataset headers.")
    
    if df["TrackerDistance"].equals(df["TotalDistance"]):
        print("\nTrackerDistance is identical to TotalDistance, dropping TrackerDistance column.")
        df = df.drop(columns=["TrackerDistance"])

    duplicate_rows = df[df.duplicated(keep=False)] 
    total_duplicates = duplicate_rows.shape[0]
    
    if total_duplicates > 0:
        print(f"\nTotal duplicate rows found: {total_duplicates}")
        print("Duplicate rows:")
        print(duplicate_rows)
    else:
        print("\nNo duplicate rows found.")
    
    df_cleaned = (
        df.copy()
        .drop_duplicates()
        .assign(ActivityDate=lambda df: pd.to_datetime(df["ActivityDate"], format="%m/%d/%Y"))
        .sort_values(by=["Id", "ActivityDate"])  
    )
    
    df_cleaned["TotalSteps"] = df_cleaned["TotalSteps"].astype(int)  # Ensure steps are integers
    df_cleaned["TotalDistance"] = df_cleaned["TotalDistance"].astype(float)  # Ensure distance is a float
    
    return df_cleaned

def summarize_data(df):
    print("\nSummary Statistics of Cleaned Data:")
    print(df.describe(include="all"))
    print("\nFirst 5 rows of the cleaned dataset:")
    print(df.head())
    print("\nCleaned Data Preview Done.")