import os
import streamlit as st
import pandas as pd
import plotly.express as px
from database import connect_db, get_unique_user_ids
from dashboard_visualization import plot_heart_rate, plot_activity_summary, plot_individual_steps_calories
from analysis import SQL_acquisition, merge_and_analyze_data


# --------------------------
# Page setup (must be FIRST Streamlit command)
# --------------------------
st.set_page_config(page_title="Fitbit Dashboard", layout="wide", page_icon=":material/sprint:")

# --------------------------
# Configuration
# --------------------------
current_dir = os.path.dirname(__file__)
DB_PATH = os.path.join(current_dir, "..", "data", "fitbit_database.db")

# --------------------------
# Load and prepare data
# --------------------------
try:
    conn = connect_db(DB_PATH)
    merged_df, user_summaries = merge_and_analyze_data(conn)
    conn.close()
except Exception as e:
    st.error(f"Failed to load data: {str(e)}")
    st.stop()

# --------------------------
# Homepage setup
# --------------------------
page = st.sidebar.radio("Navigation", ["Home", "Activity Overview", "Top Users", "Individual User"])

if page == "Home":
    st.markdown("## Welcome to the Fitbit Dashboard")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Activity Overview", key="activity", help="View average statistics like calories, steps, and sleep", use_container_width=True, icon=":material/groups:"):
            st.session_state.page = "activity"

    with col2:
        if st.button("Leaderboard", key="top-users", help="View the top-performing users across various metrics", use_container_width=True, icon=":material/stars:"):
            st.session_state.page = "top-users"

    with col3:
        if st.button("Personal Stats", key="user-insights", help="Search for a user to view their specific stats", use_container_width=True, icon=":material/account_circle:"):
            st.session_state.page = "user-insights"
            
# --------------------------
# Activity Overview Page
# --------------------------
def show_activity_overview(merged_df):
    st.header("📊 Activity Overview")

    # Sidebar filters
    st.sidebar.subheader("Filter Options")
    user_ids = merged_df['Id'].unique().tolist()
    selected_user = st.sidebar.selectbox("Select User ID:", user_ids)

    date_range = st.sidebar.date_input(
        "Select Date Range:",
        [pd.to_datetime(merged_df['ActivityDate'].min()), pd.to_datetime(merged_df['ActivityDate'].max())],
        pd.to_datetime(merged_df['ActivityDate'].min()),
        pd.to_datetime(merged_df['ActivityDate'].max())
    )

    compare_to_avg = st.sidebar.checkbox("Compare with Baseline Averages")

    # Filter data based on user and date range
    filtered_df = merged_df[
        (merged_df['Id'] == selected_user) &
        (merged_df['ActivityDate'] >= pd.to_datetime(date_range[0])) &
        (merged_df['ActivityDate'] <= pd.to_datetime(date_range[1]))
    ]

    # Calculate user stats
    avg_steps = filtered_df['TotalSteps'].mean()
    avg_calories = filtered_df['Calories'].mean()
    avg_sleep = filtered_df['SleepMinutes'].mean()

    # Display user stats
    st.metric("Average Steps", f"{avg_steps:.0f}")
    st.metric("Average Calories", f"{avg_calories:.0f}")
    st.metric("Average Sleep (minutes)", f"{avg_sleep:.0f}")

    if compare_to_avg:
        overall_avg_steps = merged_df['TotalSteps'].mean()
        overall_avg_calories = merged_df['Calories'].mean()
        overall_avg_sleep = merged_df['SleepMinutes'].mean()

        step_diff = ((avg_steps - overall_avg_steps) / overall_avg_steps) * 100
        calorie_diff = ((avg_calories - overall_avg_calories) / overall_avg_calories) * 100
        sleep_diff = ((avg_sleep - overall_avg_sleep) / overall_avg_sleep) * 100

        st.markdown("### 📈 Comparison to Averages:")
        st.write(f"*Steps:* {'+' if step_diff >= 0 else ''}{step_diff:.1f}% compared to all users.")
        st.write(f"*Calories:* {'+' if calorie_diff >= 0 else ''}{calorie_diff:.1f}% compared to all users.")
        st.write(f"*Sleep:* {'+' if sleep_diff >= 0 else ''}{sleep_diff:.1f}% compared to all users.")

# --------------------------
# Top Users
# --------------------------

# --------------------------
# Individual User Statistics
# --------------------------

def individual_users():
    st.header("🏃‍➡️ Individual User")
    st.sidebar.subheader("Filter Options")

    # Clean up user IDs by removing decimals
    user_ids = merged_df['Id'].unique().tolist()
    clean_user_ids = [int(user_id) for user_id in user_ids]
    selected_user_clean = st.sidebar.selectbox("Select User ID:", sorted(clean_user_ids))
    selected_user = float(selected_user_clean)
    
    # 1. Dynamic date range based on selected user
    # First filter by user to get their specific date range
    user_specific_df = merged_df[merged_df['Id'] == selected_user]
    if not user_specific_df.empty:
        user_min_date = pd.to_datetime(user_specific_df['ActivityDate']).min().date()
        user_max_date = pd.to_datetime(user_specific_df['ActivityDate']).max().date()
    else:
        # Fallback to overall min/max if no data for selected user
        user_min_date = pd.to_datetime(merged_df['ActivityDate']).min().date()
        user_max_date = pd.to_datetime(merged_df['ActivityDate']).max().date()
    
    # Date range selection with user-specific limits
    
    date_range = st.sidebar.date_input(
        "Select Date Range:",
        [user_min_date, user_max_date],
        min_value=user_min_date,
        max_value=user_max_date,
        key="activity_date_range"
        )

    if st.sidebar.button("Select All Dates"):
        date_range = [user_min_date, user_max_date]

    # Show date range info to user
    st.sidebar.info(f"This user has data from {user_min_date.strftime('%b %d, %Y')} to {user_max_date.strftime('%b %d, %Y')}")
    
    # Filter by date range and selected user
    if len(date_range) == 2:
        user_df = merged_df[
            (merged_df['Id'] == selected_user) & 
            (merged_df['ActivityDate'] >= pd.to_datetime(date_range[0])) & 
            (merged_df['ActivityDate'] <= pd.to_datetime(date_range[1]))
        ]
    else:
        user_df = merged_df[merged_df['Id'] == selected_user]
    
    # Calculate aggregated metrics for the selected user
    total_steps = user_df['TotalSteps'].sum()
    total_calories = user_df['Calories'].sum()
    total_sleep = user_df['TotalMinutesAsleep'].sum() if 'TotalMinutesAsleep' in user_df.columns else user_df['SleepMinutes'].sum()
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Running Steps", f"{total_steps:,}")
    col2.metric("Total Burned Calories", f"{total_calories:,}")
    col3.metric("Total Sleep Duration (mins)", f"{total_sleep:,}")
    
    # Display user activity over time
    st.subheader(f"Activity Trends for User {selected_user_clean}")
    
    # Create a combined chart with dual y-axes for steps and calories
    plot_individual_steps_calories(user_df) 
    
    display_df = user_df.copy()
    display_df['ActivityDate'] = pd.to_datetime(display_df['ActivityDate']).dt.strftime('%B %d, %Y')
    
    # Remove specified columns
    columns_to_remove = ['BMI', 'WeightKg', 'Id']
    display_columns = [col for col in display_df.columns if col not in columns_to_remove]
    display_df = display_df[display_columns]
    
    # Reset index to start from 1 instead of 0
    display_df.index = range(1, len(display_df) + 1)
    
    # Display the raw data table
    st.subheader(f"Activity data for user {selected_user_clean}")
    st.dataframe(display_df)
# --------------------------
# Navigation logic
# --------------------------
if 'page' not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "activity":
    show_activity_overview(merged_df)

elif st.session_state.page == "top-users":
    st.header("🏅 Top Performers")
    st.write("Coming soon!")


elif st.session_state.page == "user-insights":
    individual_users()
