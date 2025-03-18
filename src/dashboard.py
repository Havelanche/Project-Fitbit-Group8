import os
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from database import connect_db, get_unique_user_ids
from dashboard_visualization import (plot_active_vs_sedentary, plot_activity_intensity, plot_calories_trends, plot_heart_rate_trends, plot_sleep_efficiency, plot_sleep_trends, plot_sleep_vs_activity, plot_step_distance_relationship, plot_calories_vs_activity, plot_sleep_distribution, plot_sleep_correlations, plot_step_distribution_for_all_user, plot_steps_trends, plot_steps_vs_calories, plot_steps_vs_sleep)
from analysis import merge_and_analyze_data, compute_leader_metrics


# --------------------------
# Page setup (must be FIRST Streamlit command)
st.set_page_config(page_title="Fitbit Dashboard", layout="wide", page_icon=":material/sprint:")

# --------------------------
# Configuration
current_dir = os.path.dirname(__file__)
DB_PATH = os.path.join(current_dir, "..", "data", "fitbit_database.db")

# --------------------------
# Load and prepare data
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
# Ensure session state is set
# --------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"

# --------------------------
# Homepage setup
# --------------------------
def show_home(merged_df):
    """Homepage with navigation buttons"""
    st.markdown("<h1 style='text-align: center;'> Fitbit Health & Activity Dashboard</h1>", unsafe_allow_html=True)
     # --------------------------
    # the buttons to the other pages
    # --------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Health & Activity Summary", key="activity", help="View average statistics like calories, steps, and sleep", use_container_width=True, icon=":material/groups:"):
            st.session_state.page = "Activity Overview"

    with col2:
        if st.button("Leaderboard", key="top-users", help="View the top-performing users across various metrics", use_container_width=True, icon=":material/trophy:"):
            st.session_state.page = "top-users"

    with col3:
        if st.button("Personal Stats", key="user-insights", help="Search for a user to view their specific stats", use_container_width=True, icon=":material/account_circle:"):
            st.session_state.page = "User Insights"
         
    # --------------------------
    # Numerical Summary (Key Metrics)
    # --------------------------
    st.markdown("---")
    st.markdown("### :material/trophy: Key Fitbit Statistics")

    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(" :material/steps: Steps", f"{merged_df['TotalSteps'].mean():,.0f}", help="Average number of steps taken daily.")
    col2.metric(" :material/local_fire_department: Calories", f"{merged_df['Calories'].mean():,.0f}", help="Average daily calories burned.")
    col3.metric(" :material/bedtime: Sleep (hrs)", f"{merged_df['SleepMinutes'].mean() / 60:.1f}", help="Average sleep duration per night.")
    col4.metric(":material/bolt: Active Minutes", f"{merged_df['VeryActiveMinutes'].mean():,.0f}", help="Average active minutes per day.")

    # --------------------------
    # Visualization Section (Example: Average Steps Over Time)
    # --------------------------
    st.markdown("---")
    st.markdown("### :material/monitoring: Average Steps Over Time")

    # Ensure 'ActivityDate' is in datetime format and grouped
    merged_df['ActivityDate'] = pd.to_datetime(merged_df['ActivityDate'])
    daily_avg = merged_df.groupby("ActivityDate")["TotalSteps"].mean().reset_index()

    fig = px.line(daily_avg, x="ActivityDate", y="TotalSteps",
                  title="Average Steps Over Time",
                  labels={"TotalSteps": "Avg Steps", "ActivityDate": "Date"},
                  template="plotly_dark")
    
    st.plotly_chart(fig, use_container_width=True)   
    # --------------------------
    # Informative Section Below Buttons
    # --------------------------
    st.markdown("---")
    st.markdown("### About This Dashboard")
    st.markdown("""
    The dashboard presents visualizations and analysis of Fitbit fitness and health tracking data collected from **MM DD, 2016 to 12 April, 2016**.

    This dashboard explores relationships between fitness and health metrics, it not only states data summaries but aims to present data purposefully.

    The Fitbit app and Fitbit Premium subscription service form an integrated health platform. The Fitbit app collects data from Fitbit’s wearables, providing metrics on **physical activity, sleep, heart rate, and nutrition**. Fitbit Premium enhances the user experience with **personalized health reports and advanced insights**.
    """)
    # --------------------------
    # Footer Section
    # --------------------------
    st.markdown("---")
    st.markdown("<p style='text-align: center; font-size: 16px;'>  Developed by Students at VU</p>", unsafe_allow_html=True)

# --------------------------
# Sidebar Navigation
# --------------------------
def setup_sidebar():
    with st.sidebar:
        st.markdown("## Navigation")

        pages = {
            "Home": "Home",
            "Activity Overview": "Activity Overview",
            "Leaderboard": "Leaderboard",
            "User Insights": "Personal Stats"
        }

        selected_page = st.radio(
            "Go to:",
            options=list(pages.keys()),
            format_func=lambda x: pages[x], 
            index=list(pages.keys()).index(st.session_state.page)  
        )

        if selected_page != st.session_state.page:
            st.session_state.page = selected_page
            st.rerun()  
            
# --------------------------
# Sidebar activity overview page
# --------------------------
def setup_sidebar_activity_overview():
    with st.sidebar:
        setup_sidebar() 

        st.title(":material/monitoring: Activity Filters")

        date_range = st.date_input(
            ":material/calendar_month: Select Date Range:",
            [pd.to_datetime(merged_df['ActivityDate'].min()), pd.to_datetime(merged_df['ActivityDate'].max())],
            key="activity_date_range"
        )
        selected_intensity = st.radio(
            ":material/filter_alt: Filter Users by Intensity:",
            ["All", "Heavy (≥ 60 min Very Active)", "Moderate (30-59 min Very Active)", "Light (1-29 min Very Active)"],
            index=0
        )

        total_days = merged_df["ActivityDate"].nunique()
        st.subheader(":material/calendar_month: Total Days Tracked")
        st.info(f"Data covers **{total_days} days** of Fitbit activity.")
        
        return selected_intensity, date_range

# --------------------------
# Activity Overview Page
# --------------------------
def show_activity_overview():
    st.header("Health & Activity Summary") 

    selected_intensity, date_range = setup_sidebar_activity_overview()

    filtered_df = merged_df[
        (merged_df['ActivityDate'] >= pd.to_datetime(date_range[0])) &
        (merged_df['ActivityDate'] <= pd.to_datetime(date_range[1]))
    ] if date_range else merged_df
    
    heavy_count = merged_df[merged_df["VeryActiveMinutes"] >= 60].shape[0]
    moderate_count = merged_df[(merged_df["VeryActiveMinutes"] >= 30) & (merged_df["VeryActiveMinutes"] < 60)].shape[0]
    light_count = merged_df[(merged_df["VeryActiveMinutes"] > 0) & (merged_df["VeryActiveMinutes"] < 30)].shape[0]

    # **Apply Activity Level Filter**
    if selected_intensity == "Heavy (≥ 60 min Very Active)":
        filtered_df = filtered_df[filtered_df['VeryActiveMinutes'] >= 60]
        intensity_desc = (
            "**Heavy Activity** users engage in **intense workouts** "
            "(e.g., running, HIIT, intense cycling) for over 60 minutes daily.  \n"
            f"**Heavy:** `{heavy_count}` users (≥ 60 min Very Active)"
        )
    elif selected_intensity == "Moderate (30-59 min Very Active)":
        filtered_df = filtered_df[(filtered_df['VeryActiveMinutes'] >= 30) & (filtered_df['VeryActiveMinutes'] < 60)]
        intensity_desc = (
            "**Moderate Activity** users engage in **brisk walking, jogging, or moderate sports** "
            "for 30-59 minutes daily.  \n"
            f"**Moderate:** `{moderate_count}` users (30-59 min Very Active)"
        )
    elif selected_intensity == "Light (30-59 min Very Active)":
        filtered_df = filtered_df[(filtered_df['VeryActiveMinutes'] > 0) & (filtered_df['VeryActiveMinutes'] < 30)]
        intensity_desc = (
            "**Light Activity** users focus on **short walks, household chores, or standing activities** "
            "for 1-29 minutes daily.  \n"
            f"**Light:** `{light_count}` users (1-29 min Very Active)"
        )
    else:
        intensity_desc = (
            "This section provides insights into **all activity levels** combined.  \n"
            f"**Heavy:** `{heavy_count}` users  \n"
            f"**Moderate:** `{moderate_count}` users  \n"
            f"**Light:** `{light_count}` users"
        )

    st.info(intensity_desc)

    col1, col2 = st.columns([1.2, 2])
    with col1:
        st.subheader(":material/bolt: Very Active vs. Sedentary Minutes")
        st.markdown("""
        - This graph compares **Very active vs. sedentary** time.  
        - **Sedentary Minutes (:material/weekend:)**: Time spent sitting or with little movement.  
        - **Very Active Minutes (:material/directions_run:)**: Time spent doing high-intensity activities.  
        - **Higher Active Minutes** = More movement, better fitness!  
        - **More Sedentary Time?** Consider adding short walks or stretching!  
        """)

    with col2:
        plot_active_vs_sedentary(filtered_df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(" :material/steps: Steps", f"{merged_df['TotalSteps'].mean():,.0f}", help="Average number of steps taken daily.")
    col2.metric(" :material/local_fire_department: Calories", f"{merged_df['Calories'].mean():,.0f}", help="Average daily calories burned.")
    col3.metric(" :material/bedtime: Sleep (hrs)", f"{merged_df['SleepMinutes'].mean() / 60:.1f}", help="Average sleep duration per night.")
    col4.metric(":material/bolt: Active Minutes", f"{merged_df['VeryActiveMinutes'].mean():,.0f}", help="Average active minutes per day.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        plot_steps_trends(filtered_df)
    with col2:
        plot_calories_trends(filtered_df)
    with col3:
        plot_sleep_trends(filtered_df)

    col4, col5, col6 = st.columns(3)
    with col4:
        plot_activity_intensity(filtered_df)
    with col5:
        plot_heart_rate_trends(filtered_df)
    with col6:
        plot_step_distribution_for_all_user(filtered_df)
   
    col7, col8 = st.columns(2)
    with col7:
        plot_steps_vs_calories(filtered_df)
    with col8:
        plot_sleep_vs_activity(filtered_df)
        
    add_footer() 



# --------------------------
# Leaderboard
def leaderboard_page(metrics_df, champions):
    st.header(":material/trophy: Leaderboard")
    
    # --------------------------
    # Sidebar Section
    with st.sidebar:
        st.title(":material/search: Choose Your Champion")
        
        # Champion selection radio buttons
        selected_champ = st.radio(
            "Select metric to highlight:", 
            ["Step Master", "Distance Champion", 
             "Activity King/Queen", "Calorie Burner", 
             "Sleep Master"]
        )
        
        # Map selection to champion keys
        champ_mapping = {
            "Step Master": "steps_champion",
            "Distance Champion": "distance_champion",
            "Activity King/Queen": "active_minutes_champion",
            "Calorie Burner": "calories_burned_champion",
            "Sleep Master": "sleep_quality_champion"
        }
        
        # Get selected champion data
        champ_key = champ_mapping[selected_champ]
        champion = champions.get(champ_key, {})
        
        # Simplified usage stats
        if champion and not metrics_df.empty:
            st.title(":material/devices_wearables: Device Usage Stats")
            try:
                user_data = metrics_df[metrics_df['Id'] == champion['user_id']].iloc[0]
                st.metric("Total Tracked Days", 
                         f"{int(user_data['UsageDays'])} days",  
                         help="Days with recorded activity.")
            except Exception as e:
                st.error(f"Couldn't load data: {str(e)}")

    # --------------------------
    # Main Content
    if not champion:
        st.warning("No champion data available")
        return
    
    # Get selected user ID
    user_id = champion['user_id']
    
    # =================================================================
    # FETCH INDIVIDUAL USER'S DAILY DATA (UPDATED)
    try:
        conn = connect_db(DB_PATH)
        
        # Get daily activity data
        champ_query = f"""
            SELECT ActivityDate, TotalSteps, TotalDistance, Calories, 
                VeryActiveMinutes, SedentaryMinutes
            FROM daily_activity
            WHERE Id = {user_id}
            ORDER BY ActivityDate
        """
        champ_daily_df = pd.read_sql(champ_query, conn)
        
        # Ensure date column is in datetime format for merging
        champ_daily_df["ActivityDate"] = pd.to_datetime(champ_daily_df["ActivityDate"]).dt.date

        # Get sleep data
        champ_sleep_query = f"""
            SELECT date AS raw_datetime, value
            FROM minute_sleep
            WHERE Id = {user_id}
        """
        champ_sleep_raw = pd.read_sql(champ_sleep_query, conn)

        # Convert to datetime and floor to minute
        champ_sleep_raw["datetime"] = pd.to_datetime(
            champ_sleep_raw["raw_datetime"], 
            errors="coerce",  # Handle possible format issues
            format="mixed"
        ).dt.floor("min")

        # Extract date only for aggregation
        champ_sleep_raw["ActivityDate"] = champ_sleep_raw["datetime"].dt.date

        # Aggregate sleep states by date
        champ_sleep_df = champ_sleep_raw.groupby("ActivityDate")["value"].value_counts().unstack(fill_value=0)

        # Rename columns to match sleep states
        champ_sleep_df = champ_sleep_df.rename(columns={
            1: "AsleepMinutes",
            2: "RestlessMinutes",
            3: "AwakeMinutes"
        }).reset_index()

        # Ensure all sleep state columns exist, even if missing
        for col in ["AsleepMinutes", "RestlessMinutes", "AwakeMinutes"]:
            if col not in champ_sleep_df.columns:
                champ_sleep_df[col] = 0

        # Merge with daily activity data
        champ_daily_df = champ_daily_df.merge(champ_sleep_df, on="ActivityDate", how="left")

        # Sort data by date
        champ_daily_df = champ_daily_df.sort_values(by="ActivityDate")

        # Fill missing values and convert to integers
        sleep_cols = ["AsleepMinutes", "RestlessMinutes", "AwakeMinutes"]
        champ_daily_df[sleep_cols] = champ_daily_df[sleep_cols].fillna(0).astype(int)

    except Exception as e:
        st.error(f"Failed to load user data: {str(e)}")
        st.stop()

    # Champion Header & Metrics 
    display_titles = {
        "steps_champion": ":material/steps: Step Master",
        "distance_champion": ":material/distance: Distance Champion",
        "active_minutes_champion": ":material/sprint: Activity King/Queen",
        "calories_burned_champion": ":material/local_fire_department: Calorie Burner",
        "sleep_quality_champion": ":material/sleep_score: Sleep Champion"
    }
    st.subheader(f"{display_titles[champ_key]}: User {user_id}")
    
    # Metrics columns
    if not metrics_df.empty and 'Id' in metrics_df.columns:
        champ_metrics = metrics_df[metrics_df['Id'] == user_id].iloc[0]
        cols = st.columns(5)
        
        metric_config = {
            'TotalSteps': ("Steps", "{:,.0f}", "Total number of steps taken."),
            'TotalDistance': ("Distance", "{:.2f} km", "Total kilometers tracked."),
            'TotalCalories': ("Calories", "{:,.0f} kcal", "Total estimated energy expenditure."),
            'AverageIntensity': ("Intensity", "{:.1f}", "Average intensity state during active hours."),
            'TotalRestfulSleep': ("Sleep", "{:,.0f} mins", "Total minutes classified as asleep.")
        }
        
        for col, (metric, (title, fmt, help_txt)) in zip(cols, metric_config.items()):
            with col:
                value = fmt.format(champ_metrics[metric]) if metric in champ_metrics else "N/A"
                st.metric(title, value, help=help_txt)

    # =================================================================
    # Visualization Tabs
    tab1, tab2, tab3 = st.tabs(["Analysis 1", "Analysis 2", "Analysis 3"])
    
    with tab1:
        st.subheader(":material/monitoring: Step-Distance Relationship")
        plot_step_distance_relationship(champ_daily_df)
        st.markdown('''
                    Key Observations:
                    1. **Strong positive correlation** between step count and distance traveled  
                    2. **Consistent patterns**: Peaks/dips align across both metrics''')

    with tab2:  
        st.subheader(":material/monitoring: Calories vs. Very Active Minutes") 
        plot_calories_vs_activity(champ_daily_df)
        st.markdown('''
                    Activity-Energy Relationship:
                    1. **Intensity matters**: High active minutes consistently drive calorie expenditure peaks  
                    2. **Metabolic lag**: Max calorie burns often follow activity spikes by 12-24 hours  
                    3. **Consistency beats intensity**: Regular moderate activity > sporadic peaks ''')

    with tab3:  
        st.subheader(":material/monitoring: Sleep Quality Distribution")
        plot_sleep_distribution(champ_daily_df)
        st.markdown('''
                    Key Sleep Patterns:
                    1. Consistent deep sleep maintenance → Lower sedentary time variability
                    2. **Weekend recovery**: Saturday activity drops → Sunday sleep quality gains  
                    3. **Sleep debt cycles**: 3+ poor sleep days → Progressive sedentary increases''')

    # =================================================================
    # Additional Sleep Analysis Section
    st.divider()
    st.subheader(":material/add_chart: Advanced Sleep Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        plot_sleep_correlations(champ_daily_df)
        st.markdown(''' 
                    Typical relationships: 
                    - Sedentary hours ⬆ → Sleep time ⬇ (strong negative)  
                    - Active minutes ⬆ → Sleep quality ⬆ (moderate positive)  
                    - Step consistency ↔ Regular sleep cycles''')    
        
    with col2:
        plot_sleep_efficiency(champ_daily_df)
        st.markdown('''
                    Key Insights:
                    - Each bubble represents one day's activity-sleep relationship  
                    - Color intensity → Step count (darker = more steps)  
                    - Bubble size → Calories burned (larger = higher burn)  
                    - Trend line shows overall pattern direction''')
    
    st.divider()
    st.subheader(":material/ssid_chart: Temporal Comparisons")
    plot_steps_vs_sleep(champ_daily_df)
    st.markdown('''
                Key Observations:
                1. **Acute Phase Alignment**: 
                Simultaneous peaks in activity and sleep metrics indicate immediate exercise-sleep reciprocity, driven by adenosine metabolism and thermal regulation processes.
                2. **Delayed Recovery Signaling**: 
                Offset patterns (activity→sleep lag) reveal multi-stage recovery needs, particularly after high-intensity intervals requiring glycogen replenishment and muscle repair.
                3. **Habitual Rhythm Encoding**: 
                Repeating weekly/monthly cycles demonstrate entrainment of biological rhythms to lifestyle patterns through consistent behavioral reinforcement.''')
    add_footer() 


def add_footer():
    st.divider()
    st.caption('''
        :material/warning: *Data Availability Note:*  
        \nSome metrics may show incomplete records due to inherent gaps in wearable device data collection.  
        \nMissing values occur when: Users didn't wear their device; Specific activities weren't tracked; Sleep/wake states couldn't be determined.  
        \nAll analyses use available data.
    ''')
# --------------------------
# Individual User Statistics

# --------------------------
# Navigation logic
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Determine which page to show
if st.session_state.page == "Home":
    show_home(merged_df)
elif st.session_state.page == "Activity Overview":
    show_activity_overview()
elif st.session_state.page == "Leaderboard":
    leaderboard_page(metrics_df, champions)
elif st.session_state.page == "user-insights":
    st.header("🔍 User Insights")
    st.write("Coming soon!")
