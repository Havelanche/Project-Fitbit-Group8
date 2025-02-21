# Project Fitbit Group 8

## Project Description

This project analyzes Fitbit data using Python and SQL. It provides various functions for data processing, visualization, and validation to understand user activity patterns.

## Installation

To run this project, install the required dependencies:

```bash
pip install numpy pandas matplotlib seaborn statsmodels sqlite3
```

## Usage

### 1. Load Data

```python
load_data(filename)
```

**Description:** Converts a CSV file into a Pandas DataFrame for analysis.\
**Parameters:**

- `filename` *(str)*: The path to the CSV file.\
  **Returns:**
- A DataFrame containing the loaded data.

### 2. Get Unique Users

```python
get_unique_users(df, column_name)
```

**Description:** Finds distinct user IDs and aggregates data (e.g., Total Steps, Total Distance).\
**Parameters:**

- `df` *(DataFrame)*: The dataset to analyze.
- `column_name` *(str)*: The column to sum up for each user.\
  **Returns:**
- A DataFrame of unique users with aggregated data.

### 3. Plot Distance Distribution

```python
plot_distance_distribution(unique_users)
```

**Description:** Plots a histogram showing the distribution of total distances run by users.\
**Parameters:**

- `unique_users` *(DataFrame)*: The DataFrame returned by `get_unique_users()`.

### 4. Calories Burned Per Day

```python
calories_burned_per_day(df, user_id, start_date=None, end_date=None)
```

**Description:** Plots a user's daily calorie burn over a specified time range.\
**Parameters:**

- `df` *(DataFrame)*: The dataset.
- `user_id` *(int)*: The user ID to analyze.
- `start_date` *(str, optional)*: Start date (format: YYYY-MM-DD).
- `end_date` *(str, optional)*: End date (format: YYYY-MM-DD).

### 5. Plot Weekly Workout Distribution

```python
plot_workout(df)
```

**Description:** Visualizes workout frequency across weekdays using a bar chart.\
**Parameters:**

- `df` *(DataFrame)*: The dataset.

### 6. Plot Linear Regression Model

```python
plot_LRM(df, user_id)
```

**Description:** Creates a regression plot showing the relationship between total steps and calories burned.\
**Parameters:**

- `df` *(DataFrame)*: The dataset.
- `user_id` *(int)*: The user ID to analyze.

### 7. Classify Users

```python
classify_user(df)
```

**Description:** Categorizes users into 'Light', 'Moderate', or 'Heavy' based on activity frequency.\
**Parameters:**

- `df` *(DataFrame)*: The dataset.\
  **Returns:**
- A DataFrame with user classifications.

### 8. SQL Data Acquisition

```python
SQL_acquisition(query)
```

**Description:** Runs an SQL query and returns the result as a Pandas DataFrame.\
**Parameters:**

- `query` *(str)*: SQL query string.\
  **Returns:**
- A DataFrame with query results.

### 9. Verify Total Steps

```python
verify_total_steps(df)
```

**Description:** Compares total steps recorded in the CSV file and database to check for discrepancies.\
**Parameters:**

- `df` *(DataFrame)*: The dataset.

## Contributors

- **[Havelanche, Honglin, Lala, Chenshuo]** - Project Lead
- **[Other Contributors]**
