import plotly.express as px
import plotly.graph_objects as go

import streamlit as st

def plot_heart_rate(data, user_id):
    """Plot heart rate timeline"""
    if data.empty:
        st.warning("No heart rate data available for this user")
        return None
    
    fig = px.line(
        data,
        x="timestamp",
        y="heart_rate",
        title=f"Heart Rate Timeline for User {user_id}",
        labels={"heart_rate": "Heart Rate (bpm)", "timestamp": "Time"}
    )
    fig.update_layout(hovermode="x unified")
    return fig

def plot_activity_summary(data, user_id):
    """Plot activity metrics and display summary statistics"""
    if data.empty:
        st.warning("No activity data available for this user")
        return None
    
    # Create columns for metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Steps", f"{data['TotalSteps'].sum():,}")
    with col2:
        st.metric("Avg Daily Calories", f"{data['Calories'].mean():,.0f}")

    # Create step count visualization
    fig = px.bar(
        data,
        x="ActivityDate",
        y="TotalSteps",
        title=f"Daily Step Count for User {user_id}",
        labels={"TotalSteps": "Steps", "ActivityDate": "Date"}
    )
    fig.update_xaxes(tickangle=45)
    return fig

def plot_sleep_patterns(data, user_id):
    """Plot sleep duration and metrics"""
    if data.empty:
        st.warning("No sleep data available for this user")
        return None
    
    # Create metrics columns
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Average Sleep", f"{data['sleep_hours'].mean():.1f} hours")
    with col2:
        st.metric("Total Sleep", f"{data['sleep_hours'].sum():.0f} hours")

    # Create sleep visualization
    fig = px.area(
        data,
        x="sleep_date",
        y="sleep_hours",
        title=f"Sleep Duration for User {user_id}",
        labels={"sleep_hours": "Hours", "sleep_date": "Date"}
    )
    fig.update_layout(yaxis_range=[0, 12])
    return fig

def plot_step_distance_relationship(champ_daily_df, user_id):
    if champ_daily_df.empty:
        st.warning("No daily data available for this user.")
        return

    # Ensure the data is sorted by date
    champ_daily_df = champ_daily_df.sort_values(by="ActivityDate")

    fig = go.Figure()
    # Add Steps (Bars)
    fig.add_trace(go.Bar(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["TotalSteps"],
        name="Steps",
        marker_color="blue"
    ))
    # Add Distance (Line)
    fig.add_trace(go.Scatter(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["TotalDistance"],
        name="Distance (km)",
        line=dict(color="orange"),
        yaxis="y2",
        mode="lines+markers"  # Ensures connected points
    ))
    # Update layout
    fig.update_layout(
        title=f"Steps vs. Distance for User {user_id}",
        xaxis=dict(title="Date", showticklabels=False),  # Hides individual dates
        yaxis=dict(title="Steps", side="left"),
        yaxis2=dict(title="Distance (km)", side="right", overlaying="y"),
        hovermode="x unified"
    )

    st.plotly_chart(fig)

def plot_calories_vs_activity(champ_daily_df, user_id):
    if champ_daily_df.empty:
        st.warning("No daily data available for this user.")
        return

    champ_daily_df = champ_daily_df.sort_values(by="ActivityDate")

    fig = go.Figure()
    # Active Minutes (Bar)
    fig.add_trace(go.Bar(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["VeryActiveMinutes"],
        name="Active Minutes",
        marker_color="green"
    ))
    # Calories (Line)
    fig.add_trace(go.Scatter(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["Calories"],
        name="Calories (kcal)",
        line=dict(color="red"),
        yaxis="y2",
        mode="lines+markers"
    ))
    # Layout
    fig.update_layout(
        title=f"Calories vs. Activity for User {user_id}",
        xaxis=dict(title="Date", showticklabels=False),
        yaxis=dict(title="Active Minutes", side="left"),
        yaxis2=dict(title="Calories (kcal)", side="right", overlaying="y"),
        hovermode="x unified"
    )
    st.plotly_chart(fig)

def plot_sleep_distribution(champ_daily_df, user_id):
    if champ_daily_df.empty or "TotalRestfulSleep" not in champ_daily_df:
        st.warning("No sleep data available for this user.")
        return

    champ_daily_df = champ_daily_df.sort_values(by="ActivityDate")

    fig = go.Figure()
    # Sleep Minutes (Bar)
    fig.add_trace(go.Bar(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["TotalRestfulSleep"],
        name="Sleep (mins)",
        marker_color="purple"
    ))
    # Sedentary Minutes (Line)
    fig.add_trace(go.Scatter(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["SedentaryMinutes"],
        name="Sedentary Time (mins)",
        line=dict(color="gray"),
        yaxis="y2",
        mode="lines+markers"
    ))
    # Layout
    fig.update_layout(
        title=f"Sleep vs. Sedentary Time for User {user_id}",
        xaxis=dict(title="Date", showticklabels=False),
        yaxis=dict(title="Sleep (mins)", side="left"),
        yaxis2=dict(title="Sedentary Time (mins)", side="right", overlaying="y"),
        hovermode="x unified"
    )
    st.plotly_chart(fig)