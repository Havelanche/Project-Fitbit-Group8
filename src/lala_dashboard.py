from database import get_unique_user_ids, get_unique_user_ids
from dashboard_visualization import plot_heart_rate, plot_activity_summary, plot_sleep_patterns

# --------------------------
# Database Connection
# --------------------------
try:
    conn = connect_db(DB_PATH)
except Exception as e:
    st.error(f"### Database Connection Error ❌\n*Path:* {DB_PATH}\n*Error:* {str(e)}")
    st.stop()

# --------------------------
# User Selection
# --------------------------
try:
    user_ids = get_unique_user_ids(conn)
    selected_user = st.sidebar.selectbox("👤 Select User ID:", user_ids)
except Exception as e:
    st.sidebar.error(f"### User Loading Error ⚠\n`{str(e)}`")
    st.stop()

# --------------------------
# Dashboard Layout
# --------------------------
st.title("Fitbit Activity Dashboard")
st.markdown("---")

# Main content columns
col1, col2 = st.columns([3, 2])

# Heart Rate Analysis
with col1:
    st.header("❤ Heart Rate Analysis")
    try:
        heart_df = pd.read_sql_query(f"""
            SELECT datetime(Time) AS timestamp, Value AS heart_rate
            FROM heart_rate WHERE Id = {selected_user}
            ORDER BY timestamp
        """, conn)
        fig = plot_heart_rate(heart_df, selected_user)
        if fig: st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Heart Rate Error: {str(e)}")

# Activity Summary
with col2:
    st.header("📊 Activity Summary")
    try:
        activity_df = pd.read_sql_query(f"""
            SELECT ActivityDate, TotalSteps, Calories
            FROM daily_activity WHERE Id = {selected_user}
            ORDER BY ActivityDate
        """, conn)
        fig = plot_activity_summary(activity_df, selected_user)
        if fig: st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Activity Error: {str(e)}")

# Sleep Analysis
st.markdown("---")
st.header("💤 Sleep Patterns")
try:
    sleep_df = pd.read_sql_query(f"""
        SELECT date AS sleep_date, SUM(value) AS sleep_minutes
        FROM minute_sleep WHERE Id = {selected_user}
        GROUP BY sleep_date
    """, conn)
    sleep_df["sleep_hours"] = sleep_df["sleep_minutes"] / 60
    fig = plot_sleep_patterns(sleep_df, selected_user)
    if fig: st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Sleep Error: {str(e)}")

# Cleanup
conn.close()
st.markdown("---")
st.caption("Fitbit Dashboard - Created with Streamlit 🚀")


def opening_page_text:
    # below the three main bottom

    # text block 1
    # data acknowledgement:
    # The dashboard presents visualizations and analysis of Fitbit fitness and health tracking data 
    # collected from my Fitbit Charge 4 from November 1, 2021 to March 3, 2022. 
    # The Fitbit app and Fitbit Premium subscription service form an integrated health platform. 

    # text block 2
    # The Fitbit app collects data from Fitbit’s wearables, providing metrics on physical activity, sleep, heart rate, and nutrition. 
    # Fitbit Premium enhances the user experience with personalized health reports and advanced insights. 