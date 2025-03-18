import os
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from database import connect_db, get_unique_user_ids
from dashboard_visualization import plot_active_vs_sedentary, plot_activity_intensity, plot_calories_trends, plot_calories_vs_activity, plot_heart_rate, plot_activity_summary, plot_heart_rate_trends, plot_sleep_distribution, plot_sleep_trends, plot_sleep_vs_activity, plot_step_distance_relationship, plot_step_distribution, plot_steps_vs_calories, plot_steps_trends
from analysis import SQL_acquisition, merge_and_analyze_data, merge_and_analyze_data, compute_leader_metrics


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
# Ensure session state is set
# --------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"

# --------------------------
# Homepage setup
# --------------------------
def show_home():
    """Homepage with navigation buttons"""
    st.markdown("<h1 style='text-align: center;'>🏆 Fitbit Health & Activity Dashboard</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Activity Overview", key="activity", help="View average statistics like calories, steps, and sleep", use_container_width=True, icon=":material/groups:"):
            st.session_state.page = "Activity Overview"

    with col2:
        if st.button("Leaderboard", key="Leaderboard", help="View the top-performing users across various metrics", use_container_width=True, icon=":material/stars:"):
            st.session_state.page = "Leaderboard"

    with col3:
        if st.button("Personal Stats", key="user-insights", help="Search for a user to view their specific stats", use_container_width=True, icon=":material/account_circle:"):
            st.session_state.page = "User Insights"
            
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
    # Footer Section with Name
    # --------------------------
    st.markdown("---")
    st.markdown("<p style='text-align: center; font-size: 16px;'>📌 Developed by Students at VU</p>", unsafe_allow_html=True)

# --------------------------
# Sidebar Navigation
# --------------------------
def setup_sidebar():
    """Sidebar Navigation using Radio Buttons for Stability"""
    with st.sidebar:
        st.markdown("## Navigation")

        pages = {
            "Home": "Home",
            "Activity Overview": "Activity Overview",
            "Leaderboard": "Leaderboard",
            "User Insights": "Personal Stats"
        }

        # Use radio buttons for stable navigation
        selected_page = st.radio(
            "Go to:",
            options=list(pages.keys()),
            format_func=lambda x: pages[x],  # Display formatted text with emojis
            index=list(pages.keys()).index(st.session_state.page)  # Keep current selection
        )

        # Update session state only if selection changes
        if selected_page != st.session_state.page:
            st.session_state.page = selected_page
            st.rerun()  # Efficient page switch

# --------------------------
# Activity Overview Page
# --------------------------
def show_activity_overview():
    st.header("Activity Overview") 

    # # Sidebar Filters
    with st.sidebar:
        setup_sidebar()
             
        st.title("Choose A Date")
        # Date range filter
        date_range = st.date_input(
            "📅 Select Date Range:",
            [pd.to_datetime(merged_df['ActivityDate'].min()), pd.to_datetime(merged_df['ActivityDate'].max())],
            key="activity_date_range"
        )

        st.subheader("📌 Filter Users by Activity Level")
        # Activity Level Filter
        selected_intensity = st.radio(
            "Filter by Activity Intensity:",
            ["All", "Heavy", "Moderate", "Light"],
            index=0
        )
    if date_range:
        filtered_df = merged_df[
            (merged_df['ActivityDate'] >= pd.to_datetime(date_range[0])) & 
            (merged_df['ActivityDate'] <= pd.to_datetime(date_range[1]))
        ]
    else:
        filtered_df = merged_df  

    # Filtering logic based on selection
    if selected_intensity == "Heavy":
        filtered_df = merged_df[merged_df['VeryActiveMinutes'] >= 60]
    elif selected_intensity == "Moderate":
        filtered_df = merged_df[(merged_df['VeryActiveMinutes'] >= 30) & (merged_df['VeryActiveMinutes'] < 60)]
    elif selected_intensity == "Light":
        filtered_df = merged_df[(merged_df['VeryActiveMinutes'] > 0) & (merged_df['VeryActiveMinutes'] < 30)]
    else:
        filtered_df = merged_df  # Show all users if "All" is selected

    # Display Key Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("👟 Avg Steps", f"{filtered_df['TotalSteps'].mean():,.0f}", help="Average steps")
    col2.metric("🔥 Avg Calories", f"{filtered_df['Calories'].mean():,.0f}", help="Average Calories")
    col3.metric("💤 Avg Sleep", f"{filtered_df['SleepMinutes'].mean():,.0f}", help="Average Sleep")
    # Display Graphs
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
        plot_active_vs_sedentary(filtered_df)
   
    col7, col8, col9 = st.columns(3)
    with col7:
        plot_step_distribution(filtered_df)
    with col8:
        plot_steps_vs_calories(filtered_df)
    with col9:
        plot_sleep_vs_activity(filtered_df)


# --------------------------
# Leaderboard
# --------------------------
def leaderboard_page(metrics_df, champions):
    st.header("🏆 User Leaderboard")
    
    # --------------------------
    # Sidebar Section
    with st.sidebar:
        setup_sidebar()
            
        st.title("🌟 Choose Your Champion")
        # Champion selection radio buttons
        selected_champ = st.radio(
            "Select metric to highlight:", 
            ["Step Count Leader", "Distance Covered Champion", 
             "Active Minutes Record Holder", "Calorie Burn King/Queen", 
             "Sleep Quality Master"]
        )
        
        # Map selection to champion keys
        champ_mapping = {
            "Step Count Leader": "steps_champion",
            "Distance Covered Champion": "distance_champion",
            "Active Minutes Record Holder": "active_minutes_champion",
            "Calorie Burn King/Queen": "calories_burned_champion",
            "Sleep Quality Master": "sleep_quality_champion"
        }
          
          # Get selected champion data
        champ_key = champ_mapping[selected_champ]
        champion = champions.get(champ_key, {})
        
        # Simplified usage stats
        if champion and not metrics_df.empty:
            st.title("📅 Device Usage Stats")
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
# STEP 1: FETCH INDIVIDUAL USER'S DAILY DATA (UPDATED)
# =================================================================
    # FETCH INDIVIDUAL USER'S DAILY DATA
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
        champ_daily_df = SQL_acquisition(conn, champ_query)
        print("checkcheck: daily_df")        
        print(champ_daily_df.head())

        # Get sleep data - count sleep minutes (value=1) per date --这个地方可能得考虑成 “value>0”
        champ_sleep_query = f"""
            SELECT 
                date AS ActivityDate,  -- Rename to match activity data
                value AS TotalRestfulSleep
            FROM minute_sleep
            WHERE Id = {user_id} AND value > 0 -- 取所有大于0的数据，然后再根据不同的颜色运用到一条bar上去划分睡眠质量
            GROUP BY date  -- Correct grouping by actual date column
            ORDER BY date
        """
        champ_sleep_df = SQL_acquisition(conn, champ_sleep_query)
        print("checkcheck: sleep_df")
        print(champ_sleep_df.head())

        # First, convert ActivityDate to datetime in both dataframes````````
        champ_daily_df['ActivityDate'] = pd.to_datetime(champ_daily_df['ActivityDate'])

        # For the sleep dataframe, extract just the date part and sum up the sleep values by date
        champ_sleep_df['ActivityDate'] = pd.to_datetime(champ_sleep_df['ActivityDate']).dt.date
        champ_sleep_df = champ_sleep_df.groupby('ActivityDate', as_index=False)['TotalRestfulSleep'].sum()

        # Convert back to datetime for proper merging
        champ_sleep_df['ActivityDate'] = pd.to_datetime(champ_sleep_df['ActivityDate'])

        # Now merge the dataframes
        merged_df = pd.merge(
            champ_daily_df,
            champ_sleep_df,
            on="ActivityDate",
            how="left"  # Keep all activity dates even with no sleep data
        )

        # Fill NaN values with 0
        merged_df['TotalRestfulSleep'] = merged_df['TotalRestfulSleep'].fillna(0)

        # Convert numeric columns
        numeric_cols = ['TotalSteps', 'TotalDistance', 'Calories', 
                    'VeryActiveMinutes', 'SedentaryMinutes']
        merged_df[numeric_cols] = merged_df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        
        conn.close()
    except Exception as e:
        st.error(f"Failed to load user data: {str(e)}")
        st.stop()


    # Champion Header & Metrics 
    display_titles = {
        "steps_champion": "👟 Step Master",
        "distance_champion": "🏃 Distance Champion",
        "active_minutes_champion": "⚡ Activity King/Queen",
        "calories_burned_champion": "🔥 Calorie Burner",
        "sleep_quality_champion": "💤 Sleep Champion"
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
        st.subheader("📈 Step-Distance Relationship")
        plot_step_distance_relationship(merged_df, user_id)

    with tab2:  
        st.subheader("🔥 Calories vs. Active Minutes") 
        plot_calories_vs_activity(merged_df, user_id)

    with tab3:  
        st.subheader("💤 Sleep Quality Distribution")
        plot_sleep_distribution(merged_df, user_id)

# --------------------------
# Individual User Statistics
# --------------------------
def show_user_insights():
    st.header(" User Insights")

    setup_sidebar()

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
elif st.session_state.page == "Leaderboard":
    leaderboard_page(metrics_df, champions) 
    st.write("Work in Progress!")
elif st.session_state.page == "User Insights":
    show_user_insights()

# Cleanup connection
conn.close()
