import pandas as pd
import re

def load_and_preview_data(file_path):
    """Loads the CSV file with correct delimiter and previews the data."""
    try:
        df = pd.read_csv(file_path, sep=';', engine='python')
        print("\n Dataset Preview (First 5 Rows):")
        print(df.head())
        
        print("\nColumn names:", df.columns.tolist())

        print("\n Summary Statistics:")
        print(df.describe(include="all"))

        print("\n Data preview completed.")
        return df
    except FileNotFoundError:
        print(f" Error: File not found at {file_path}")
    except pd.errors.ParserError:
        print(" Error: Failed to parse the CSV file. Check the delimiter or file format.")

def clean_and_transform_data(df):
    print(f"\nColumns in dataset: {df.columns}")

    df.columns = df.columns.str.strip().str.replace(';', '').str.replace(' ', '_')
    df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], errors='coerce')

    def clean_distance(value):
        if isinstance(value, str):
            match = re.search(r'\d+(\.\d+)?', value)
            return float(match.group()) if match else None
        return value

    distance_cols = ['TotalDistance', 'TrackerDistance', 'LoggedActivitiesDistance', 
                     'VeryActiveDistance', 'ModeratelyActiveDistance', 'LightActiveDistance', 'SedentaryActiveDistance']

    for col in distance_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_distance)

    numeric_cols = ['TotalSteps', 'Calories', 'VeryActiveMinutes', 'FairlyActiveMinutes',
                    'LightlyActiveMinutes', 'SedentaryMinutes']

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    duplicate_rows = df[df.duplicated(keep=False)]  # Get all duplicate rows (including the original)
    total_duplicates = duplicate_rows.shape[0]
    
    # If duplicates exist, print the total number of duplicates and the duplicate rows
    if total_duplicates > 0:
        print(f"\nTotal duplicate rows found: {total_duplicates}")
        print("Duplicate rows:")
        print(duplicate_rows)
    else:
        print("\nNo duplicate rows found.") 

    df_cleaned = df.drop_duplicates().sort_values(by=["Id", "ActivityDate"])

    print("\n Data cleaning and transformation completed.")
    print(df_cleaned.head())

    return df_cleaned

def summarize_data(df):
    print("\n Summary Statistics of Cleaned Data:")
    print(df.describe(include="all"))

    print("\n Preview of Cleaned Dataset (First 5 Rows):")
    print(df.head())

    print("\n Cleaned data summary completed.")
