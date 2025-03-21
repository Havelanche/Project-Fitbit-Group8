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
     
## Project Structure

**fitbit-main.py:** The main script that processes the dataset and generates insights.

**dashboard.py:** The Streamlit-based dashboard for interactive data visualization.

**database.py:** Handles database interactions using SQLite.

**visualization.py:** Contains data plots and visual images.

**creative_analysis.py:** Looks for relations in a unique way.

**csv_data_wrangling.py:** Loads, cleans, and transforms raw Fitbit data from CSV files into a structured format for analysis.

**dashboard_visualization.py:** Contains functions for creating visualizations within the Streamlit dashboard.

**analysis.py:** Contains functions for analyzing different behaviors & correlations of users.


## Installation & Setup
### Prerequisites
Ensure you have **Python 3.8 & streamlit-1.43.2** installed & imported along with the following dependencies:
```bash
os pandas numpy matplotlib seaborn statsmodels sqlite3 streamlit traceback stats  matplotlib.cm matplotlib.pyplot statsmodels.api shapiro plotly.express statsmodels.formula.api 
```
## Getting Started
**Clone the Repository**
```bash
https://github.com/Havelanche/Project-Fitbit-Group8
```
You can simply clone and download it to desktop.

### Opening Files in Visual Studio Code
**Open your terminal and navigate to the project directory**.
```bash
cd path/to/your/project
```
Make sure you are at the right folder to run the code by typing **ls** in terminal to check
```bash
ls
```
**Until terminal shows the**
```bash 
Readme.md     data    src
```
**Then goes to**
```bash
cd src
```
Now you are at the right folder!
### Running the Analysis in fitbit-main.py
To execute the analysis and generate visualizations, run:
```bash
python fitbit-main.py
```
### Running the Dashboard in dashboard.py
To start the **Streamlit dashboard**, execute:
```bash
streamlit run dashboard.py
```
If it shows errors and not the lastest version of streamlit(go to the terminal and enter **streamlit --version** to check the version of streamlit)
go get the **newest** version of streamlit in the terminal below
```bash
pip install --upgrade streamlit
```
After reviewing the dashboard, you need to close it in terminal **manually** by pressing **Control + Z** otherwise it will keep operating!

## Features of the Dashboard
- **General Statistics**: Overview of Fitbit users' activity levels & sleep time.
- **Group Analysis**:take a closer look of three different type of users(heavy, moderate and light).
- **leadboard system**:The Leaderboard page showcases top-performing users in the following categories:
**💤 Sleep Master**/**🏃 Distance Champion**/**🔥 Calorie Burner**.
These highlights offer a fun, competitive way to recognize outstanding users based on real health and activity metrics.
- **User-Specific Analysis**: Select an individual to view their fitness trends.
- **Time-Based Filtering**: Filter data by date range or time of day.
- **Sleep & Activity Correlation**: Explore how sleep patterns relate to daily activity.
- **Visual Insights**: Interactive graphs to analyze step count, heart rate, and calorie burn.




## Contributors

- **[Havelanche]**
- **[Honglin]**
- **[Lala]**
- **[Chenshuo]**
