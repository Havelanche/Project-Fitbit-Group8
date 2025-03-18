# Fitbit Data Analysis Project

## Project Overview
This project analyzes Fitbit data collected from 33 respondents in an Amazon survey (2016). The study involves statistical analysis, data visualization, and the development of a Streamlit dashboard to explore insights from the dataset.

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
Ensure you have **Python 3.8+** installed & imported along with the following dependencies:
```bash
os pandas numpy matplotlib seaborn statsmodels sqlite3 streamlit traceback stats  matplotlib.cm matplotlib.pyplot statsmodels.api shapiro plotly.express statsmodels.formula.api 
```
### Opening Files in Visual Studio Code
**Open your terminal and navigate to the project directory**.
**Make sure doing cd in orders !!!! e.g. You put the cloned file on desktop: desktop--> fitbit project--> src**
```bash
cd path/to/your/project
```
**until**
```bash
ls
```
**terminal shows the**
```bash 
Readme.md     data    src
```
**then goes to**
```bash
cd src
```
Now you are at the right folder!
### Running the Analysis
To execute the analysis and generate visualizations, run:
```bash
python fitbit-main.py
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




## Contributors

- **[Havelanche]**
- **[Honglin]**
- **[Lala]**
- **[Chenshuo]**
