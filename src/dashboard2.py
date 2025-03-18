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
    metrics_df, champions = compute_leader_metrics(conn)
    conn.close()
except Exception as e:
    st.error(f"Failed to load data: {str(e)}")
    st.stop()

# --------------------------
# Page Functions (DEFINED BEFORE USE)
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

def leaderboard_page(metrics_df, champions):
    st.header("🏆 User Leaderboard")
    
    # Sidebar Section
    with st.sidebar:
        st.title("🌟 Choose Your Champion")
        selected_champ = st.radio(
            "Select metric to highlight:", 
            ["Step Count Leader", "Distance Covered Champion", 
             "Active Minutes Record Holder", "Calorie Burn King/Queen", 
             "Sleep Quality Master"]
        )
        
        champ_mapping = {
            "Step Count Leader": "steps_champion",
            "Distance Covered Champion": "distance_champion",
            "Active Minutes Record Holder": "active_minutes_champion",
            "Calorie Burn King/Queen": "calories_burned_champion",
            "Sleep Quality Master": "sleep_quality_champion"
        }
        
        champ_key = champ_mapping[selected_champ]
        champion = champions.get(champ_key, {})
        
        if champion and not metrics_df.empty:
            st.title("📅 Device Usage Stats")
            user_id = champion['user_id']
            
            try:
                user_data = metrics_df[metrics_df['Id'] == user_id].iloc[0]
                first_date = pd.to_datetime(user_data['FirstDate'])
                last_date = pd.to_datetime(user_data['LastDate'])
                usage_days = user_data['UsageDays']
                
                st.write(f"**Tracking Period:**")
                st.caption(f"{first_date.strftime('%b %d, %Y')} - {last_date.strftime('%b %d, %Y')}")
                st.metric("Total Tracked Days", f"{usage_days} days")
                
            except Exception as e:
                st.error(f"Couldn't load calendar data: {str(e)}")

    # Main Content
    if not champion:
        st.warning("No champion data available")
        return
    
    display_titles = {
        "steps_champion": "👟 Step Master",
        "distance_champion": "🏃 Distance Champion",
        "active_minutes_champion": "⚡ Activity King/Queen",
        "calories_burned_champion": "🔥 Calorie Burner",
        "sleep_quality_champion": "💤 Sleep Champion"
    }
    st.subheader(f"{display_titles[champ_key]}: User {champion['user_id']}")
    
    if not metrics_df.empty and 'Id' in metrics_df.columns:
        champ_metrics = metrics_df[metrics_df['Id'] == champion['user_id']].iloc[0]
        cols = st.columns(5)
        
        metric_config = {
            'TotalSteps': ("Steps", "{:,}", "Total number of steps taken."),
            'TotalDistance': ("Distance", "{:.2f} km", "Total kilometers tracked."),
            'TotalCalories': ("Calories", "{:,} kcal", "Total estimated energy expenditure."),
            'AverageIntensity': ("Intensity", "{:.1f}", "Average intensity state."),
            'TotalRestfulSleep': ("Sleep", "{:,} mins", "Total minutes classified as asleep.")
        }
        
        for col, (metric, (title, fmt, help_txt)) in zip(cols, metric_config.items()):
            with col:
                value = fmt.format(champ_metrics[metric]) if metric in champ_metrics else "N/A"
                st.metric(title, value, help=help_txt)
    
    tab1, tab2, tab3 = st.tabs(["Distance Analysis", "Activity Metrics", "Sleep Patterns"])
    
    with tab1:
        if not metrics_df.empty:
            st.subheader("Distance Distribution")
            st.bar_chart(metrics_df.set_index('Id')['TotalDistance'])
    
    with tab2:
        if not metrics_df.empty:
            st.subheader("Activity Metrics Comparison")
            fig, ax = plt.subplots(figsize=(10, 4))
            metrics_df[['VeryActiveMinutes', 'AverageIntensity']].plot(kind='bar', ax=ax)
            st.pyplot(fig)
    
    with tab3:
        if 'TotalRestfulSleep' in metrics_df.columns:
            st.subheader("Sleep Quality Analysis")
            st.area_chart(metrics_df.set_index('Id')['TotalRestfulSleep'])
        else:
            st.info("No sleep data available")


# --------------------------
# Navigation Setup
# --------------------------
PAGE_ORDER = ["activity", "top-users", "user-insights"]
PAGE_CONFIG = {
    "home": {"label": "Home", "icon": "🏠"},
    "activity": {"label": "Activity Overview", "icon": "📊"},
    "top-users": {"label": "Leaderboard", "icon": "🏆"},
    "user-insights": {"label": "Personal Stats", "icon": "🔍"}
}

if 'page' not in st.session_state:
    st.session_state.page = "home"

# --------------------------
# Page Rendering
# --------------------------
if st.session_state.page == "home":
    # Homepage buttons
    st.markdown("## Welcome to the Fitbit Dashboard")
    cols = st.columns(3)
    with cols[0]:
        if st.button(PAGE_CONFIG["activity"]["label"], key="activity", use_container_width=True):
            st.session_state.page = "activity"
    with cols[1]:
        if st.button(PAGE_CONFIG["top-users"]["label"], key="top-users", use_container_width=True):
            st.session_state.page = "top-users"
    with cols[2]:
        if st.button(PAGE_CONFIG["user-insights"]["label"], key="user-insights", use_container_width=True):
            st.session_state.page = "user-insights"

else:
    # Sidebar navigation
    current_page = st.session_state.page
    new_page = st.sidebar.radio(
        "Dashboard Navigation",
        options=PAGE_ORDER,
        format_func=lambda x: PAGE_CONFIG[x]["label"],
        index=PAGE_ORDER.index(current_page)
    )
    
    if new_page != current_page:
        st.session_state.page = new_page
        st.experimental_rerun()

    # Main content
    if st.session_state.page == "activity":
        show_activity_overview(merged_df)
    elif st.session_state.page == "top-users":
        leaderboard_page(metrics_df, champions)
    elif st.session_state.page == "user-insights":
        st.header("🔍 Individual User Statistics")
        user_id = st.sidebar.selectbox("Select User ID", merged_df['Id'].unique())
