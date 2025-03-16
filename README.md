# Fitbit Data Analysis Project

## Project Overview
This project analyzes Fitbit data collected from **33 respondents** in an Amazon survey (2016). The study involves statistical analysis, data visualization, and the development of a **Streamlit dashboard** to explore insights from the dataset.

## Dataset
The dataset consists of multiple CSV files and an SQLite database containing the following tables:
- **daily_activity**: Daily statistics on steps, distance, and calories burnt.
- **heart_rate**: Heart rate measurements taken every 5 seconds.
- **hourly_calories**: Calories burned per hour.
- **hourly_intensity**: Exercise intensity per hour.
- **hourly_steps**: Steps taken per hour.
- **minute_sleep**: Sleep duration logs.
- **weight_log**: Weight, BMI, and fat percentage logs.

## Project Objectives
1. **Data Cleaning & Exploration**:
   - Count unique users and compute total distances.
   - Visualize daily calorie burns with date filters.
   - Analyze workout frequency by day of the week.
2. **Statistical Analysis & Regression Models**:
   - Investigate the relationship between steps taken and calories burned.
   - Perform regression analysis to estimate calorie burn.
   - Explore correlations between sleep duration and activity levels.
3. **Database Interaction**:
   - Categorize users as Light, Moderate, or Heavy users based on Fitbit activity.
   - Execute SQL queries to analyze sleep patterns, active minutes, and heart rate.
4. **Data Visualization & Insights**:
   - Create bar plots of steps, calories, and sleep duration per time block.
   - Investigate the impact of weather conditions on activity.
5. **Dashboard Development**:
   - Implement a **Streamlit dashboard** to interactively explore the data.
   - Provide individual user statistics, time-based filtering, and sleep analysis.

## Installation & Setup
### Prerequisites
Ensure you have **Python 3.8+** installed along with the following dependencies:
```bash
pip install pandas numpy matplotlib seaborn statsmodels sqlite3 streamlit
```
### Running the Analysis
To execute the analysis and generate visualizations, run:
```bash
python fitbit_analysis.py
```
### Running the Dashboard
To start the **Streamlit dashboard**, execute:
```bash
streamlit run dashboard.py
```

## Features of the Dashboard
- **General Statistics**: Overview of Fitbit users' activity levels.
- **User-Specific Analysis**: Select an individual to view their fitness trends.
- **Time-Based Filtering**: Filter data by date range or time of day.
- **Sleep & Activity Correlation**: Explore how sleep patterns relate to daily activity.
- **Visual Insights**: Interactive graphs to analyze step count, heart rate, and calorie burn.


## Deployment
- The dashboard will be deployed on **Streamlit Cloud**.
- To make the repository public, navigate to GitHub settings > Change visibility.
- Once deployed, access the dashboard at: [Dashboard Link]


## Contributors

- **[Havelanche]**
- **[Honglin]**
- **[Lala]**
- **[Chenshuo]**
