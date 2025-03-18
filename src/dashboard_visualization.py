import pandas as pd
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
    
#----------------------------------------------------------------
#----------------------------------------------------------------
    
def plot_steps_trends(data):
    if data.empty:
        st.warning("⚠️ No step data available.")
        return

    fig = px.bar(
        data, 
        x="ActivityDate", 
        y="TotalSteps", 
        title="👟 Daily Step Trends",
        labels={"TotalSteps": "Steps", "ActivityDate": "Date"},
        color_discrete_sequence=['#0000FF']
        )

    fig.update_layout(
        xaxis_title="📅 Date",
        yaxis_title="🚶 Steps Taken",
        # hovermode="x unified",
        template="seaborn"
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

    
def plot_calories_trends(data):
    if data.empty:
        st.warning("⚠️ No calorie data available.")
        return
    # Histogram
    fig = px.histogram(
        data, x="Calories",
        title="🔥 Calories Distribution (Histogram)",
        labels={"Calories": "Calories Burned"},
        color_discrete_sequence=['#008000'],
        nbins=20
    )

    fig.update_layout(
        xaxis_title="🔥 Calories Burned",
        yaxis_title="Frequency",
        template="seaborn"
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

def plot_sleep_trends(data):
    if data.empty:
        st.warning("⚠️ No sleep data available.")
        return

    fig = px.bar(
        data, 
        x="ActivityDate", 
        y="SleepMinutes", 
        title="💤 Sleep Duration Over Time",
        labels={"SleepMinutes": "Minutes Asleep", "ActivityDate": "Date"},
        color_discrete_sequence=['#A020F0']
    )

    fig.update_layout(
        xaxis_title="📅 Date",
        yaxis_title="💤 Sleep Duration (minutes)",
        hovermode="x unified",
        template="seaborn"
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)


def plot_activity_intensity(df):
    # Aggregate total minutes spent in different intensity levels
    intensity_df = df[['VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes', 'SedentaryMinutes']].sum().reset_index()
    intensity_df.columns = ['Activity Level', 'Minutes']

    # Sort values for better visualization
    intensity_df = intensity_df.sort_values(by="Minutes", ascending=False)

    # **DONUT CHART** with better insights
    fig1 = px.pie(
        intensity_df, 
        names='Activity Level', 
        values='Minutes', 
        title='🕒 Activity Intensity Breakdown',
        hole=0.4,  # Converts it into a donut chart
        color='Activity Level',
        color_discrete_map={
            "SedentaryMinutes": "#264653",  # Dark blue
            "LightlyActiveMinutes": "#2A9D8F",  # Teal
            "FairlyActiveMinutes": "#E9C46A",  # Yellow
            "VeryActiveMinutes": "#E63946"  # Red
        }
    )

    # **Enhance labels with percentages**
    fig1.update_traces(
        textinfo="percent+label",
        pull=[0.1 if m == intensity_df['Minutes'].max() else 0 for m in intensity_df['Minutes']]  # Highlight highest value
    )

    st.plotly_chart(fig1, use_container_width=True)  # Donut Chart

def plot_heart_rate_trends(df):
    if 'ActivityDate' not in df.columns or 'HeartRate' not in df.columns:
        st.warning("No heart rate data available.")
        return

    df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], errors='coerce')
    daily_heart_rate = df.groupby('ActivityDate')['HeartRate'].mean().reset_index()
    daily_heart_rate_filtered = daily_heart_rate[daily_heart_rate['HeartRate'] != 66]

    if daily_heart_rate_filtered.empty:
        st.warning("Filtered heart rate data is empty. Most values are 66 BPM.")
        return

    fig = px.line(
        daily_heart_rate_filtered, x='ActivityDate', y='HeartRate',
        title='💓 Heart Rate Trends (Excluding 66 BPM)',
        labels={'HeartRate': 'Heart Rate (BPM)', 'ActivityDate': 'Date'},
        color_discrete_sequence=['#d62728']
    )

    fig.update_layout(
        xaxis_title="📅 Date",
        yaxis_title="❤️ Heart Rate (BPM)",
        font=dict(family="Arial", size=14, color="black"),
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_active_vs_sedentary(df):
    fig = px.scatter(
        df, 
        x='SedentaryMinutes', 
        y='VeryActiveMinutes', 
        color='Calories',
        title="⚡ Active vs. Sedentary Minutes",
        labels={"SedentaryMinutes": "Sedentary Minutes", "VeryActiveMinutes": "Very Active Minutes"},
        color_continuous_scale="blues"
    )

    fig.update_layout(
        xaxis_title="🛋️ Sedentary Minutes",
        yaxis_title="🏃 Very Active Minutes",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_step_distribution(df):
    fig = px.histogram(
        df, 
        x='TotalSteps', 
        nbins=20, 
        title="Step Distribution",
        color_discrete_sequence=['#0000FF']
    )

    fig.update_layout(
        xaxis_title="👟Total Steps",
        yaxis_title="Frequency",
        template="seaborn"
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)


def plot_steps_vs_calories(df):
    fig = px.scatter(
        df, 
        x='TotalSteps', 
        y='Calories', 
        title="🏃 Steps vs. Calories Burned",
        labels={"TotalSteps": "Total Steps", "Calories": "Calories Burned"},
        color="Calories",
        color_continuous_scale="greens"
    )

    fig.update_layout(
        xaxis_title="👟 Steps Taken",
        yaxis_title="🔥 Calories Burned",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_sleep_vs_activity(df):
    fig = px.scatter(
        df, 
        x='SleepMinutes', 
        y='VeryActiveMinutes', 
        title="💤 Sleep vs. Activity Level",
        labels={"SleepMinutes": "Minutes Asleep", "VeryActiveMinutes": "Very Active Minutes"},
        color="VeryActiveMinutes",
        color_continuous_scale="purples"
    )

    fig.update_layout(
        xaxis_title="💤 Sleep Minutes",
        yaxis_title="🏃 Very Active Minutes",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

