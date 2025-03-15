import os
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from database import connect_db, get_unique_user_ids
from dashboard_visualization import plot_heart_rate, plot_activity_summary, plot_sleep_patterns
from analysis import merge_and_analyze_data, compute_leader_metrics


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
    
    # lala's leaderboard data (metrics and champions)
    metrics_df, champions = compute_leader_metrics(conn)

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
# Leaderboard
# --------------------------
def leaderboard_page(metrics_df, champions):
    st.header("🏆 User Leaderboard")
    
    # --------------------------
    # Sidebar - Champion Selection
    # --------------------------
    st.sidebar.title("🌟 Champion Filters")
    selected_champs = st.sidebar.multiselect(
        "Select champions to highlight:",
        options=["Most Steps", "Longest Distance", "Best Sleeper"],
        default=["Most Steps"]
    )
    
    # --------------------------
    # Main Metrics Display
    # --------------------------
    if metrics_df.empty:
        st.warning("No metrics data available")
        return
    
    # Create metric columns
    cols = st.columns(5)
    metric_config = {
        'TotalSteps': {'title': 'Total Steps', 'format': '{:,.0f}'},
        'TotalDistance': {'title': 'Total Distance', 'format': '{:.2f} km'},
        'TotalCalories': {'title': 'Calories Burned', 'format': '{:,.0f}'},
        'AverageIntensity': {'title': 'Avg Intensity', 'format': '{:.1f}'},
        'TotalRestfulSleep': {'title': 'Restful Sleep', 'format': '{:,.0f} mins'}
    }
    
    for idx, (col, (metric, config)) in enumerate(zip(cols, metric_config.items())):
        with col:
            if metric in metrics_df.columns:
                avg_value = metrics_df[metric].mean()
                champ_key = f"{metric.split('_')[-1].lower()}_champion"
                
                if champ_key in champions and any(c.lower() in champ_key for c in selected_champs):
                    champ = champions[champ_key]
                    st.metric(
                        label=config['title'],
                        value=config['format'].format(champ['value']),
                        delta=f"Champion: {champ['user_id']}"
                    )
                else:
                    st.metric(
                        label=config['title'],
                        value=config['format'].format(avg_value),
                        help="Average across all users"
                    )
    
    # --------------------------
    # Top Performers Table
    # --------------------------
    st.subheader("🏅 Top 5 Performers")
    if not metrics_df.empty:
        display_df = metrics_df.sort_values('TotalDistance', ascending=False).head()
        st.dataframe(
            display_df,
            column_config={
                "Id": "User ID",
                "TotalSteps": "Total Steps",
                "TotalDistance": st.column_config.NumberColumn(
                    "Distance (km)", 
                    format="%.2f"
                ),
                "TotalRestfulSleep": "Restful Sleep (mins)"
            },
            hide_index=True
        )
    
    # --------------------------
    # Visualization Tabs
    # --------------------------
    tab1, tab2, tab3 = st.tabs(["Distance Analysis", "Activity Metrics", "Sleep Patterns"])
    
    with tab1:
        if not metrics_df.empty:
            st.subheader("Distance Distribution")
            st.bar_chart(metrics_df.set_index('Id')['TotalDistance'])
    
    with tab2:
        if not metrics_df.empty:
            st.subheader("Activity Metrics")
            fig, ax = plt.subplots(figsize=(10, 4))
            metrics_df[['VeryActiveMinutes', 'AverageIntensity']].plot(kind='bar', ax=ax)
            st.pyplot(fig)
    
    with tab3:
        if 'TotalRestfulSleep' in metrics_df.columns and not metrics_df.empty:
            st.subheader("Sleep Quality Analysis")
            st.area_chart(metrics_df.set_index('Id')['TotalRestfulSleep'])
        else:
            st.info("No sleep data available")

# --------------------------
# Individual User Statistics
# --------------------------

# --------------------------
# Sidebar - User Selection and Date Filter
# --------------------------
# st.sidebar.title("🔍 Filters")

# if merged_df is not None:
#     user_ids = merged_df['Id'].unique().tolist()
#     selected_user = st.sidebar.selectbox("Select User ID:", user_ids)

#     date_range = st.sidebar.date_input(
#         "Select Date Range:",
#         [pd.to_datetime(merged_df['ActivityDate'].min()), pd.to_datetime(merged_df['ActivityDate'].max())],
#         pd.to_datetime(merged_df['ActivityDate'].min()),
#         pd.to_datetime(merged_df['ActivityDate'].max())
#     )

#     # Ensure ActivityDate is in datetime format
#     merged_df['ActivityDate'] = pd.to_datetime(merged_df['ActivityDate'], errors='coerce')

#     # Filter by user ID and date range
#     filtered_df = merged_df[
#         (merged_df['Id'] == selected_user) &
#         (merged_df['ActivityDate'] >= pd.Timestamp(date_range[0])) &
#         (merged_df['ActivityDate'] <= pd.Timestamp(date_range[1]))
#     ]

#     st.write("Filtered Data:", filtered_df)
#     # --------------------------
#     # Main Dashboard
#     # --------------------------
#     st.title("📊 Fitbit Dashboard")
#     st.markdown("---")

#     # General Statistics
#     st.header("📈 General Statistics")
#     col1, col2, col3 = st.columns(3)

#     col1.metric("Total Steps", f"{filtered_df['TotalSteps'].sum():,.0f}")
#     col2.metric("Average Sleep (hours)", f"{(filtered_df['SleepMinutes'].mean() / 60):.2f}")
#     col3.metric("Avg Calories Burned", f"{filtered_df['Calories'].mean():,.0f}")

#     # Graphical Summary
#     st.subheader("Activity Over Time")
#     fig = px.line(filtered_df, x='date', y=['TotalSteps', 'Calories'], title="Daily Steps & Calories")
#     st.plotly_chart(fig, use_container_width=True)

#     # Sleep Analysis
#     st.header("💤 Sleep Analysis")
#     sleep_fig = px.bar(filtered_df, x='date', y='SleepMinutes', title="Daily Sleep Duration (minutes)")
#     st.plotly_chart(sleep_fig, use_container_width=True)

#     # Weekend vs Weekday Analysis
#     st.subheader("📅 Weekend vs Weekday Analysis")
#     filtered_df['Weekend'] = filtered_df['DayOfWeek'].isin(['Saturday', 'Sunday'])
#     weekend_df = filtered_df.groupby('Weekend').agg({
#         'TotalSteps': 'mean',
#         'SleepMinutes': 'mean'
#     }).reset_index()

#     weekend_fig = px.bar(weekend_df, x='Weekend', y=['TotalSteps', 'SleepMinutes'],
#                          title="Average Steps and Sleep: Weekdays vs Weekends")
#     st.plotly_chart(weekend_fig, use_container_width=True)

#     st.caption("Fitbit Dashboard - Created with Streamlit 🚀")
# else:
#     st.error("No data available. Please check your database connection.")



# --------------------------
# Navigation logic
# --------------------------
if 'page' not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "activity":
    show_activity_overview(merged_df)

elif st.session_state.page == "top-users":
    st.header("🏅 Top Performers")
    leaderboard_page(metrics_df, champions) 
    st.write("Coming soon!")

elif st.session_state.page == "user-insights":
    st.header("🔍 User Insights")
    st.write("Coming soon!")