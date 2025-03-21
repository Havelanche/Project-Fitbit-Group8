# Fitbit Data Analytics & Dashboard Project

## Project Overview
This project analyzes Fitbit data collected from 33 respondents in an Amazon survey (2016). The study involves data wrangling, statistical analysis, data visualization, and the development of a Streamlit dashboard to explore insights from the dataset.

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
```bash
data/
├── Chicago_Weather.csv         # online real weather dataset from Chicago
├── daily_activity.csv          # raw dataset
├── fitbit_database.db          # fitbit database
src/
│
├── Fitbit-main.py              # Main script to run the data analysis pipeline
├── dashboard.py                # Streamlit-based interactive dashboard
├── database.py                 # SQLite-based data interaction layer
├── visualization.py            # Generic data visualizations
├── creative_analysis.py        # Unique and creative correlations or patterns
├── csv_data_wrangling.py       # Cleans and transforms raw CSV Fitbit data
├── dashboard_visualization.py  # Dashboard-specific plots and figures
├── analysis.py                 # Core analysis functions (e.g., behavior trends)
```

## Installation & Setup
### Prerequisites
Ensure you have **Python 3.8 & streamlit-1.43.2** installed & imported along with the following dependencies:
```bash
os pandas numpy seaborn statsmodels sqlite3 streamlit traceback stats  matplotlib.cm matplotlib.pyplot statsmodels.api shapiro plotly.express statsmodels.formula.api 
```
## Getting Started
**Clone the Repository**
```bash
https://github.com/Havelanche/Project-Fitbit-Group8
```
You can clone and download it to your desktop.

### Opening Files in Visual Studio Code
**Open your terminal and navigate to the project directory**.
```bash
cd path/to/your/project
```
Make sure you are in the correct folder to run the code by entering **ls** in the terminal to check
```bash
ls
```
Until your terminal shows the
```bash 
Readme.md     data    src
```
Then navigate to
```bash
cd src
```
Now you are in the correct folder!
### Running the Analysis in Fitbit-main.py
To execute the analysis and generate visualizations, run:
```bash
python Fitbit-main.py
```
### Running the Dashboard in dashboard.py
To start the **Streamlit dashboard**, execute:
```bash
streamlit run dashboard.py
```
If it shows errors and not the latest version of streamlit (go to the terminal and enter **streamlit --version** to check the version of streamlit).
**Upgrade** Streamlit to the latest version in the terminal below.
```bash
pip install --upgrade streamlit
```
After reviewing the dashboard, you need to close it in the terminal **manually** by pressing **Control + Z** otherwise it will keep operating!

## Features of the Dashboard
- **General Statistics**: Overview of Fitbit users' activity levels & sleep time.
- **Community Summary**: Choose your group of interest from Heavy, Moderate, or Light users based on the daily activity length, and explore various fitness insights.
- **Leaderboard**: The Leaderboard page showcases top-performing users in the following categories:
**Sleep Master**, **Distance Champion**, **Calorie Burner**.
These highlights offer a fun, competitive way to recognize outstanding users, present correlations between activity, health and sleep metrics, and help users improve their overall well-being.
- **User-Specific Analysis**: Select an individual user with a date range to view their fitness data and activity trends, ie: distance, step count, heart rate, and calories.





## Contributors  

- **Havelanche Troenokromo**  
- **Honglin Zhu**  
- **Qianying Zhao (Lala)**  
- **Chenshuo Zhang**   

*Supervised by dr. ir. M. A. (Marc) Corstanje*  
*Developed as part of the Data Engineering Group Assignment from BSc Business Analytics program at Vrije Universiteit Amsterdam.*  
