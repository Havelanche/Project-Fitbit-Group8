import os
import streamlit as st
import pandas as pd
from database import connect_db
from dashboard_visualization import (plot_active_vs_sedentary, plot_activity_intensity, plot_calories_trends, plot_heart_rate_trends, plot_sleep_efficiency, plot_sleep_trends, plot_sleep_vs_activity, plot_step_distance_relationship, plot_calories_vs_activity, plot_sleep_distribution, plot_sleep_correlations, plot_step_distribution_for_all_user, plot_steps_trends, plot_steps_vs_calories, plot_steps_vs_sleep, show_calories_plot, show_sleep_plot, show_steps_plot, plot_individual_metrics, plot_steps_champion_chart, plot_distance_champion_chart, plot_calories_champion_chart)
from analysis import merge_and_analyze_data, compute_leader_metrics


# --------------------------
# Page setup (must be FIRST Streamlit command)
st.set_page_config(page_title="Fitbit Health & Activity Dashboard", layout="wide", page_icon=":material/sprint:")

# --------------------------
# Configuration
current_dir = os.path.dirname(__file__)
DB_PATH = os.path.join(current_dir, "..", "data", "fitbit_database.db")

# --------------------------
try:
    conn = connect_db(DB_PATH)
    merged_df, user_summaries = merge_and_analyze_data(conn)
    
    metrics_df, champions = compute_leader_metrics(conn)

    conn.close()
except Exception as e:
    st.error(f"Failed to load data: {str(e)}")
    st.stop()

if "page" not in st.session_state:
    st.session_state.page = "Home"
# --------------------------
# Homepage setup
# --------------------------
def display_activity_metrics(merged_df):
    
    numeric_cols = merged_df.select_dtypes(include=["number"]).columns  
    daily_avg = merged_df.groupby("ActivityDate")[numeric_cols].mean()


    avg_steps = daily_avg["TotalSteps"].mean()
    avg_calories = daily_avg["Calories"].mean()
    avg_sleep_minutes = daily_avg["SleepMinutes"].mean()
    avg_active_minutes = daily_avg["VeryActiveMinutes"].mean()

    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(":material/steps: Steps", f"{avg_steps:,.0f} ", help="Average number of steps taken daily.")
    col2.metric(":material/local_fire_department: Calories", f"{avg_calories:,.0f} kcal", help="Average daily calories burned.")
    col3.metric(":material/bolt: Active Minutes", f"{avg_active_minutes:,.0f} min", help="Average active minutes per day.")
    col4.metric(":material/bedtime: Sleep", f"{avg_sleep_minutes:.1f} min", help="Average sleep duration per night.")


    st.markdown("---")
    
def show_home(merged_df):
    """Homepage with navigation buttons"""
    st.markdown("<h1 style='text-align: center;'> Fitbit Health & Activity Dashboard</h1>", unsafe_allow_html=True)
    # --------------------------
    # About This Dashboard
    # --------------------------
    st.markdown(f"""
    ### :material/info: About
    This dashboard analyzes Fitbit health and activity data from 35 users (33 users with valid activity records) over a one-month period (March-April 2016), 
    
    providing statistical summaries, interactive visualizations, and meaningful insights into user trends and behaviors.
                
    The Fitbit app collects data from Fitbit’s wearables, providing key metrics on:
    - **Physical Activity** (steps, active minutes, exercise intensity)
    - **Sleep Tracking** (sleep duration, quality)
    - **Heart Rate Monitoring** (resting and active heart rates)
    - **Caloric Expenditure** (calories burned, metabolic trends)
    - **Weight & BMI Logs** (tracking weight and fat percentage)

    Fitbit Premium enhances the user experience by offering **personalized health reports and advanced insights**, helping users improve their overall well-being.
    """)
    
    st.markdown("---")
    st.markdown("### :material/pin_drop: Navigation (click twice)")
     # --------------------------
    # the buttons to the other pages
    # --------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Community Summary", key="Users_Summary", help="View average statistics like calories, steps, and sleep", use_container_width=True, icon=":material/groups:"):
            st.session_state.page = "Users Summary"

    with col2:
        if st.button("Leaderboard", key="Leaderboard", help="View the top-performing users across various metrics", use_container_width=True, icon=":material/trophy:"):
            st.session_state.page = "Leaderboard"

    with col3:
        if st.button("Personal Stats", key="user-insights", help="Search for a user to view their specific stats", use_container_width=True, icon=":material/account_circle:"):
            st.session_state.page = "User Insights"
         
    # --------------------------
    # Numerical Summary (Key Metrics)
    # --------------------------
    st.markdown("---")
    st.markdown("### :material/bar_chart: General Overview")
    display_activity_metrics(merged_df)
    # --------------------------
    # 3 plots
    # --------------------------   
    st.markdown("### :material/trending_up: Data Visualization")
    
    tab1, tab2, tab3 = st.tabs(["Steps Over Time", "Calories Over Time", "Sleep Over Time"])
    
    with tab1:
        st.plotly_chart(show_steps_plot(merged_df), use_container_width=True)
    
    with tab2:
        st.plotly_chart(show_calories_plot(merged_df), use_container_width=True)
    
    with tab3:
        st.plotly_chart(show_sleep_plot(merged_df), use_container_width=True)
    
    # --------------------------
    # Footer Section
    # --------------------------
    st.markdown("---")
    st.markdown("<p style='text-align: center; font-size: 16px;'>  "
    "Developed by Honglin Zhu, Havelanche Troenokromo, Qianying Zhao (Lala) and Chenshuo Zhang </p>", unsafe_allow_html=True)
    add_footer()

# --------------------------
# Sidebar Navigation
# --------------------------
def setup_sidebar():
    with st.sidebar:
        st.markdown("## :material/pin_drop: Navigation")

        pages = {
            "Home": "Home",
            "Users Summary": "Community Summary",
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
def setup_sidebar_Users_Summary():
    with st.sidebar:
        setup_sidebar() 
        st.title(":material/filter_alt: Choose Your Group")

        selected_intensity = st.radio(
            "Select Group to explore:",
            ["All Users", "Heavy (60+ min vigorous exercise)", "Moderate (30-59 min moderate activity)", "Light (1-29 min light movement)"],
            index=0
        )
    
        return selected_intensity

def add_footer():
    st.divider()
    st.caption('''
        :material/warning: *Data Availability Note:*  
        \nSome metrics may show incomplete records due to inherent gaps in wearable device data collection.  
        \nMissing values occur when: Users didn't wear their device; Specific activities weren't tracked; Sleep/wake states couldn't be determined.  
        \nAll analyses use available data.
    ''')

# --------------------------
# Users Summary
# --------------------------
def show_Users_Summary(merged_df):
    st.header(":material/groups: Community Summary") 

    selected_intensity = setup_sidebar_Users_Summary()

    filtered_df = merged_df.copy()
    
    heavy_count = merged_df[merged_df["Class"] == "Heavy"]["Id"].nunique()
    moderate_count = merged_df[merged_df["Class"] == "Moderate"]["Id"].nunique()
    light_count = merged_df[merged_df["Class"] == "Light"]["Id"].nunique()


    if selected_intensity == "Heavy (60+ min vigorous exercise)":
            filtered_df = filtered_df[filtered_df["Class"] == "Heavy"]
            intensity_desc = (
            "**Heavy Activity** users engage in **intense workouts** "
            "(e.g., running, HIIT, intense cycling) for over 60 minutes daily.  \n"
            f"**Heavy:** `{heavy_count}` users (+ 60 min Very Active)"
        )
    elif selected_intensity == "Moderate (30-59 min moderate activity)":
        filtered_df = filtered_df[filtered_df["Class"] == "Moderate"]
        intensity_desc = (
            "**Moderate Activity** users engage in **brisk walking, jogging, or moderate sports** "
            "for 30-59 minutes daily.  \n"
            f"**Moderate:** `{moderate_count}` users (30-59 min Very Active)"
        )
    elif selected_intensity == "Light (1-29 min light movement)":
        filtered_df = filtered_df[filtered_df["Class"] == "Light"]
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
    st.subheader("Dynamic Activity Averages")
    display_activity_metrics(filtered_df)
    
    st.subheader(":material/bolt: Very Active vs. Sedentary Minutes")
    col1, col2 = st.columns([2, 1])

    with col1:
        plot_active_vs_sedentary(filtered_df)

    with col2:
        # Extract summary statistics from the filtered data
        avg_sedentary = filtered_df["SedentaryMinutes"].mean()
        avg_active = filtered_df["VeryActiveMinutes"].mean()
        max_active = filtered_df["VeryActiveMinutes"].max()
        sedentary_category = "Low" if avg_sedentary < 600 else "High"

        st.markdown(f"""
        **Data Breakdown**  
        - **Avg. Sedentary Time:** `{avg_sedentary:.1f}` min/day (**{sedentary_category} Sedentary Lifestyle**)  
        - **Avg. Active Time:** `{avg_active:.1f}` min/day  
        - **Max Active Minutes Recorded:** `{max_active}` min  

        **:material/pin_drop: Insights**  
        - **More movement = Less sedentary time!**  
        - **Darker dots in the graph?** More calories burned!  
        - **Too much sitting?** Try standing/stretching breaks!  
        """)
        
    avg_steps = filtered_df["TotalSteps"].mean()
    avg_calories = filtered_df["Calories"].mean()
    avg_sleep = filtered_df["SleepMinutes"].mean() / 60  # Convert minutes to hours
    top_step_users = filtered_df["TotalSteps"].quantile(0.90)  # Top 10% step count
    
    tab1, tab2, tab3 = st.tabs(["Steps Over Time", " Calories Burned", "Sleep Duration"])
    with tab1:
        st.subheader(":material/monitoring: Steps Over Time: Daily & 7-Day Rolling Average")
        plot_steps_trends(filtered_df)
        
        st.markdown(f'''
        **Step Insights for {selected_intensity}:**  
        1. The **average daily step count** is `{avg_steps:,.0f}` steps.  
        2. The **top 10% most active users** take at least `{top_step_users:,.0f}` steps daily.  
        3. **Step consistency** plays a bigger role than occasional high-step days.  
        ''')
        
    with tab2:
        st.subheader(":material/monitoring: Sweat Equity: How Movement Drives Calorie Burn")
        plot_calories_trends(filtered_df)
        
        st.markdown(f'''
        **Calorie Burn Insights for {selected_intensity}:**  
          Users burn an average of **`{avg_calories:,.0f}` kcal per day**.  
        ''')

    with tab3:
        st.subheader(":material/monitoring: Restful Nights, Active Days: Breaking the Sedentary Cycle")
        plot_sleep_trends(filtered_df)
        
        st.markdown(f'''
        **Sleep Insights for {selected_intensity}:**  
          Users sleep an average of **`{avg_sleep:.1f}` hours per night**.  
        ''')

    avg_active_minutes = filtered_df["VeryActiveMinutes"].mean()
    avg_sedentary_minutes = filtered_df["SedentaryMinutes"].mean()
    avg_heart_rate = filtered_df["HeartRate"].mean() if "HeartRate" in filtered_df.columns else None
    step_variability = filtered_df["TotalSteps"].std()
    
    tab4, tab5, tab6 = st.tabs(["Activity Intensity", "Heart Rate Trends", "Step Distribution"])
    
    with tab4:
        st.subheader(":material/monitoring: Finding the Balance: Activity Intensity Patterns")
        plot_activity_intensity(filtered_df)
        
        st.markdown(f'''
        **Activity Intensity Insights for {selected_intensity}:**  
        1. Users in this category average **`{avg_active_minutes:.0f}` minutes** of vigorous activity daily.  
        2. The average sedentary time for this group is **`{avg_sedentary_minutes:.0f}` minutes per day**.  
        ''')

    with tab5:
        st.subheader(":material/monitoring: Heart Rate & Activity: Fitness Levels in Motion")
        plot_heart_rate_trends(filtered_df)
        
        if avg_heart_rate is not None:
            st.markdown(f'''
            **Heart Rate Insights for {selected_intensity}:**  
              The **average heart rate** for this group is **`{avg_heart_rate:.0f}` BPM**.  
            ''')
        else:
            st.warning(" No heart rate data available for this category.")

    with tab6:
        st.subheader(":material/monitoring: Step Distribution: Who Walks the Most?")
        plot_step_distribution_for_all_user(filtered_df)
        
        st.markdown(f'''
        **Step Distribution Insights for {selected_intensity}:**  
          The step count variation for this group is **`{step_variability:,.0f}` steps** (higher = inconsistent movement).   
        ''')
        
    with st.expander("Relationships Between Metrics"):
        col1, col2 = st.columns(2)
        with col1:
            plot_steps_vs_calories(filtered_df)
        with col2:
            plot_sleep_vs_activity(filtered_df)
  
    add_footer() 

# --------------------------
# Leaderboard
def leaderboard_page(metrics_df, champions):
    st.header(":material/trophy: Leaderboard")
    # --------------------------
    # Sidebar Section
    with st.sidebar:
        setup_sidebar() 
        st.title(":material/filter_alt: Choose Your Champion")
        
        # Champion selection radio buttons
        selected_champ = st.radio(
            "Select metric to highlight:", 
            ["Step Master", "Distance Champion",  "Calorie Burner"]
        )
        
        # Map selection to champion keys
        champ_mapping = {
            "Step Master": "steps_champion",
            "Distance Champion": "distance_champion",
            "Calorie Burner": "calories_burned_champion"
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
        "calories_burned_champion": ":material/local_fire_department: Calorie Burner"
    }
    st.subheader(f"{display_titles[champ_key]}: User {user_id}")
    
    # Metrics columns
    if not metrics_df.empty and 'Id' in metrics_df.columns:
        champ_metrics = metrics_df[metrics_df['Id'] == user_id].iloc[0]
        cols = st.columns(5)
        
        metric_config = {
            'TotalSteps': (":material/steps: Total Steps", "{:,.0f}", "Total number of steps taken"),
            'TotalDistance': (":material/distance: Total Distance", "{:.2f} km", "Total kilometers tracked"),
            'TotalCalories': (":material/local_fire_department: Total Calories", "{:,.0f} kcal", "Total estimated energy expenditure"),
            'AverageIntensity': (":material/bolt: Total Average Intensity", "{:.2f}", "Average intensity state during active hours"),
            'TotalRestfulSleep': (":material/bedtime: Total Deep Sleep", "{:,.0f} mins", "Total minutes classified as asleep")
        }
        
        for col, (metric, (title, fmt, help_txt)) in zip(cols, metric_config.items()):
            with col:
                value = fmt.format(champ_metrics[metric]) if metric in champ_metrics else "N/A"
                st.metric(title, value, help=help_txt)

    # =================================================================
    # NEW: Champion vs Average Performance Visualization Section
    st.divider()
    st.subheader(":material/compare_arrows: Champion Performance vs. Community Average")
    
    # Display appropriate chart based on selected champion type
    try:
        if champ_key == "steps_champion":
            fig = plot_steps_champion_chart(conn, user_id)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("""
            **Step Master Analysis:**
            - Compare the champion's daily step count (bars) against the community average (dashed line)
            - Identify consistent patterns and peak performance days
            """)
            
        elif champ_key == "distance_champion":
            fig = plot_distance_champion_chart(conn, user_id)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("""
            **Distance Champion Analysis:**
            - Compare the champion's daily distance covered (bars) against the community average (dashed line)
            - Identify longer journeys and consistent training patterns
            """)
            
        elif champ_key == "calories_burned_champion":
            fig = plot_calories_champion_chart(conn, user_id)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("""
            **Calorie Burner Analysis:**
            - Compare the champion's daily calorie burn (bars) against the community average (dashed line)
            - Identify high-energy expenditure days and patterns
            """)

    except Exception as e:
        st.error(f"Error generating champion comparison chart: {str(e)}")

    # =================================================================
    # Visualization Tabs
    tab1, tab2, tab3 = st.tabs(["Movement Metrics", "Calorie Intensity", "Rest Rhythm"])
    
    with tab1:
        st.subheader(":material/monitoring: Every Step Counts: Pedestrian Activity Correlation")
        plot_step_distance_relationship(champ_daily_df)
        st.markdown('''
                    Key Observations:
                    1. **Strong positive correlation** between step count and distance traveled  
                    2. **Consistent patterns**: Peaks/dips align across both metrics''')

    with tab2:  
        st.subheader(":material/monitoring: Sweat Equity: How Vigorous Movement Drives Calorie Burn") 
        plot_calories_vs_activity(champ_daily_df)
        st.markdown('''
                    Activity-Energy Relationship:
                    1. **Intensity matters**: High active minutes consistently drive calorie expenditure peaks  
                    2. **Consistency beats intensity**: Regular moderate activity > sporadic peaks''')

    with tab3:  
        st.subheader(":material/monitoring: Restful Nights, Active Days: Breaking the Sedentary Cycle")
        plot_sleep_distribution(champ_daily_df)
        st.markdown('''
                    Key Sleep Patterns:
                    1. Consistent deep sleep maintenance → Lower sedentary time variability
                    2. **Sleep debt cycles**: 3+ poor sleep days → Progressive sedentary increases''')

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
    st.subheader(":material/ssid_chart: Walk Hard, Sleep Hard: Movement-Recovery Relationship")
    plot_steps_vs_sleep(champ_daily_df)
    st.markdown('''
                Key Observations:
                1. **Acute Phase Alignment**: 
                Simultaneous peaks in activity and sleep metrics indicate immediate exercise-sleep reciprocity, driven by adenosine metabolism and thermal regulation processes.
                2. **Delayed Recovery Signaling**: 
                Offset patterns (activity→sleep lag) reveal multi-stage recovery needs, particularly after high-intensity intervals requiring glycogen replenishment and muscle repair.''')
    
    add_footer() 

# --------------------------
# Individual User Statistics
def individual_users():
    st.header(":material/account_circle: Personal Stats")
    
    # --------------------------
    # Sidebar Section
    with st.sidebar:
        setup_sidebar()
        st.title(":material/filter_alt: Choose Your User ID")

        user_ids = merged_df['Id'].unique().tolist()
        clean_user_ids = [int(user_id) for user_id in user_ids]
        selected_user_clean = st.sidebar.selectbox("Select User ID:", sorted(clean_user_ids))
        selected_user = float(selected_user_clean)
    
    user_specific_df = merged_df[merged_df['Id'] == selected_user]
    if not user_specific_df.empty:
        user_min_date = pd.to_datetime(user_specific_df['ActivityDate']).min().date()
        user_max_date = pd.to_datetime(user_specific_df['ActivityDate']).max().date()
    else:
        user_min_date = pd.to_datetime(merged_df['ActivityDate']).min().date()
        user_max_date = pd.to_datetime(merged_df['ActivityDate']).max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range:",
        [user_min_date, user_max_date],
        min_value=user_min_date,
        max_value=user_max_date,
        key="activity_date_range"
        )

    if st.sidebar.button("Select All Dates"):
        date_range = [user_min_date, user_max_date]

    st.sidebar.info(f"This user has valid date range is from {user_min_date.strftime('%b %d, %Y')} to {user_max_date.strftime('%b %d, %Y')}")
    
    if len(date_range) == 2:
        user_df = merged_df[
            (merged_df['Id'] == selected_user) & 
            (merged_df['ActivityDate'] >= pd.to_datetime(date_range[0])) & 
            (merged_df['ActivityDate'] <= pd.to_datetime(date_range[1]))
        ]
    else:
        user_df = merged_df[merged_df['Id'] == selected_user]
 
    total_steps = user_df['TotalSteps'].sum()
    total_calories = user_df['Calories'].sum()
    total_sleep = user_df['TotalMinutesAsleep'].sum() if 'TotalMinutesAsleep' in user_df.columns else user_df['SleepMinutes'].sum()
    total_distance = user_df['TotalDistance'].sum()
    total_intensive_minute = user_df['VeryActiveMinutes'].sum()

    average_steps = user_df['TotalSteps'].mean()
    average_calories = user_df['Calories'].mean()
    average_sleep = user_df['TotalMinutesAsleep'].mean() if 'TotalMinutesAsleep' in user_df.columns else user_df['SleepMinutes'].mean()
    average_distance = user_df['TotalDistance'].mean()
    average_intensive_minute = user_df['VeryActiveMinutes'].mean()

    st.subheader(f":material/bar_chart: Highlights: User {selected_user_clean}")

    total_cols = st.columns(5) 

    with total_cols[0]:
        st.metric(
            label=":material/steps: Total Steps",
            value=f"{total_steps:,}",
            help="Total number of steps recorded in the selected period"
        )
    with total_cols[1]:
        st.metric(
            label=":material/distance: Total Distance",
            value=f"{total_distance:.2f} km",
            help="Total distance traveled in kilometers during the selected period"
        )
    with total_cols[2]:
        st.metric(
            label=":material/local_fire_department: Total Calories",
            value=f"{total_calories:,} kcal",
            help="Total calories burned during the selected period"
        )
    with total_cols[3]:
        st.metric(
            label=":material/bolt: Total Intensive Activity",
            value=f"{total_intensive_minute:,} mins",
            help="Total minutes of very active/intensive exercise during the selected period"
        )
    with total_cols[4]:
        st.metric(
            label=":material/bedtime: Total Sleep",
            value=f"{total_sleep:,} mins",
            help="Total minutes of sleep recorded during the selected period"
        )

    avg_cols = st.columns(5)  

    with avg_cols[0]:
        st.metric(
            label=":material/steps: Daily Steps",
            value=f"{average_steps:,.0f}",
            help="Average daily step count"
        )
    with avg_cols[1]:
        st.metric(
            label=":material/distance: Daily Distance",
            value=f"{average_distance:.2f} km",
            help="Average daily distance traveled in kilometers"
        )
    with avg_cols[2]:
        st.metric(
            label=":material/local_fire_department: Daily Calories",
            value=f"{average_calories:,.0f} kcal",
            help="Average daily calories burned"
        )
    with avg_cols[3]:
        st.metric(
            label=":material/bolt: Daily Intensive Activity",
            value=f"{average_intensive_minute:.0f} mins",
            help="Average daily minutes of very active/intensive exercise"
        )
    with avg_cols[4]:
        st.metric(
            label=":material/bedtime: Daily Sleep",
            value=f"{average_sleep:,.0f} mins",
            help="Average daily sleep duration in minutes"
        )
     
    st.divider()
  
    plot_individual_metrics(user_df) 
    
    display_df = user_df.copy()
    display_df['ActivityDate'] = pd.to_datetime(display_df['ActivityDate']).dt.strftime('%B %d, %Y')

    columns_to_remove = ['BMI', 'WeightKg', 'Id', 'HeartRate', 'Class', 'StepTotal', 'AverageIntensity', 'FairlyActiveMinutes']
    display_columns = [col for col in display_df.columns if col not in columns_to_remove]
    display_df = display_df[display_columns]
    column_display_names = {
    'ActivityDate': 'Date',
    'TotalSteps': 'Steps',
    'Calories': 'Calories Burned',
    'TotalDistance': 'Distance (km)',
    'VeryActiveMinutes': 'Active Minutes',
    'TotalMinutesAsleep': 'Sleep Duration',
    'SedentaryMinutes': 'Inactive Time',
    'LightlyActiveMinutes': 'Lightly Active Time',
    'HourlyCalories': 'Kcal / hour',
    'TotalIntensity': 'Intensity Minutes',
    'SleepMinutes': 'Sleep Duration'
    }

    valid_renames = {k: v for k, v in column_display_names.items() if k in display_df.columns}
    display_df = display_df.rename(columns=valid_renames)

    display_df.index = range(1, len(display_df) + 1)
    display_df.index.name = "Days"  

    st.subheader(f":material/search: Detailed Stats: User {selected_user_clean}")
    with st.expander(f"Click to Check"):
     st.dataframe(display_df)
    add_footer()

# --------------------------
# Navigation logic
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Determine which page to show
if st.session_state.page == "Home":
    show_home(merged_df)
elif st.session_state.page == "Users Summary":
    show_Users_Summary(merged_df)
elif st.session_state.page == "Leaderboard":
    leaderboard_page(metrics_df, champions)
elif st.session_state.page == "User Insights":
    individual_users()
