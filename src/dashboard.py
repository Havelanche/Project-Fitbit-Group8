import os
import streamlit as st
import pandas as pd
import plotly.express as px
from database import connect_db, get_unique_user_ids
from dashboard_visualization import plot_active_vs_sedentary, plot_activity_intensity, plot_calories_trends, plot_heart_rate, plot_activity_summary, plot_hourly_activity, plot_sleep_trends, plot_sleep_vs_activity, plot_step_distribution, plot_steps_trends, plot_steps_vs_calories, plot_top_users
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
# Ensure session state is set
# --------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"

# --------------------------
# Homepage setup
# --------------------------
def show_home():
    """Homepage with navigation buttons"""
    st.markdown("## Welcome to the Fitbit Dashboard")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Activity Overview", key="activity", help="View average statistics like calories, steps, and sleep", use_container_width=True, icon=":material/groups:"):
            st.session_state.page = "Activity Overview"

    with col2:
        if st.button("Leaderboard", key="top-users", help="View the top-performing users across various metrics", use_container_width=True, icon=":material/stars:"):
            st.session_state.page = "Leaderboard"

    with col3:
        if st.button("Personal Stats", key="user-insights", help="Search for a user to view their specific stats", use_container_width=True, icon=":material/account_circle:"):
            st.session_state.page = "User Insights"
  
# --------------------------
# Activity Overview Page
# --------------------------
def show_activity_overview():
    st.header("Activity Overview")
    
    # Home button (small, top-left)
    if st.button("Home", key="home_button", help="Go back to the homepage", use_container_width=False, icon=":material/home:"):
        st.session_state.page = "Home"

    st.sidebar.subheader("Filter Options")
    date_range = st.sidebar.date_input(
        "Select Date Range:",
        [pd.to_datetime(merged_df['ActivityDate'].min()), pd.to_datetime(merged_df['ActivityDate'].max())],
        key="activity_date_range"
    )
    
    if date_range:
        filtered_df = merged_df[
            (merged_df['ActivityDate'] >= pd.to_datetime(date_range[0])) & 
            (merged_df['ActivityDate'] <= pd.to_datetime(date_range[1]))
        ]
    else:
        filtered_df = merged_df

    # Display Key Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Steps", f"{filtered_df['TotalSteps'].mean():,.0f}")
    col2.metric("Avg Calories", f"{filtered_df['Calories'].mean():,.0f}")
    col3.metric("Avg Sleep (mins)", f"{filtered_df['SleepMinutes'].mean():,.0f}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        plot_steps_trends(merged_df)
    with col2:
        plot_calories_trends(merged_df)
    with col3:
        plot_sleep_trends(merged_df)
    
    col4, col5, col6 = st.columns(3)
    with col4:
        plot_activity_intensity(merged_df)
    with col5:
        plot_hourly_activity(merged_df)
    with col6:
        plot_active_vs_sedentary(merged_df)
    
    col7, col8, col9 = st.columns(3)
    with col7:
        plot_step_distribution(merged_df)
    with col8:
        plot_steps_vs_calories(merged_df)
    with col9:
        plot_sleep_vs_activity(merged_df)


# --------------------------
# Leaderboard
# --------------------------
def show_leaderboard():
    st.header("🏅 Leaderboard")

    # Home button
    if st.button("Home", key="home_button", help="Go back to the homepage", use_container_width=False, icon=":material/home:"):
        st.session_state.page = "Home"

    st.write("Coming soon!")

# --------------------------
# Individual User Statistics
# --------------------------
def show_user_insights():
    st.header("🔍 User Insights")

    # Home button
    if st.button("Home", key="home_button", help="Go back to the homepage", use_container_width=False, icon=":material/home:"):
        st.session_state.page = "Home"

    st.write("Coming soon!")

# --------------------------
# Navigation Logic
# --------------------------
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Determine which page to show
if st.session_state.page == "Home":
    show_home()
elif st.session_state.page == "Activity Overview":
    show_activity_overview()
elif st.session_state.page == "Top Users":
    show_leaderboard()
elif st.session_state.page == "Individual User":
    show_user_insights()

# Cleanup connection
conn.close()