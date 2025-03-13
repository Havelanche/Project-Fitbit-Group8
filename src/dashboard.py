import os
import streamlit as st
import pandas as pd

from database import connect_db, get_unique_user_ids
from dashboard_vis import plot_heart_rate, plot_activity_summary, plot_sleep_patterns

# --------------------------
# Configuration
# --------------------------
current_dir = os.path.dirname(__file__)
DB_PATH = os.path.join(current_dir, "..", "data", "fitbit_database.db")

# Page setup
st.set_page_config(
    page_title="Fitbit Dashboard", page_icon="🚸",
    layout="wide", initial_sidebar_state="expanded"
)

# --------------------------
# Database Connection
# --------------------------
try:
    conn = connect_db(DB_PATH)
except Exception as e:
    st.error(f"### Database Connection Error ❌\n**Path:** `{DB_PATH}`\n**Error:** `{str(e)}`")
    st.stop()

# --------------------------
# User Selection
# --------------------------
try:
    user_ids = get_unique_user_ids(conn)
    selected_user = st.sidebar.selectbox("👤 Select User ID:", user_ids)
except Exception as e:
    st.sidebar.error(f"### User Loading Error ⚠️\n`{str(e)}`")
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
    st.header("❤️ Heart Rate Analysis")
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