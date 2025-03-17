import pandas as pd
import plotly.express as px
import streamlit as st

# def plot_heart_rate(data, user_id):
#     """Plot heart rate timeline"""
#     if data.empty:
#         st.warning("No heart rate data available for this user")
#         return None
    
#     fig = px.line(
#         data,
#         x="timestamp",
#         y="heart_rate",
#         title=f"Heart Rate Timeline for User {user_id}",
#         labels={"heart_rate": "Heart Rate (bpm)", "timestamp": "Time"}
#     )
#     fig.update_layout(hovermode="x unified")
#     return fig

# def plot_activity_summary(data, user_id):
#     """Plot activity metrics and display summary statistics"""
#     if data.empty:
#         st.warning("No activity data available for this user")
#         return None
    
#     # Create columns for metrics
#     col1, col2 = st.columns(2)
#     with col1:
#         st.metric("Total Steps", f"{data['TotalSteps'].sum():,}")
#     with col2:
#         st.metric("Avg Daily Calories", f"{data['Calories'].mean():,.0f}")

#     # Create step count visualization
#     fig = px.bar(
#         data,
#         x="ActivityDate",
#         y="TotalSteps",
#         title=f"Daily Step Count for User {user_id}",
#         labels={"TotalSteps": "Steps", "ActivityDate": "Date"}
#     )
#     fig.update_xaxes(tickangle=45)
#     return fig

# def plot_sleep_patterns(data, user_id):
#     """Plot sleep duration and metrics"""
#     if data.empty:
#         st.warning("No sleep data available for this user")
#         return None
    
#     # Create metrics columns
#     col1, col2 = st.columns(2)
#     with col1:
#         st.metric("Average Sleep", f"{data['sleep_hours'].mean():.1f} hours")
#     with col2:
#         st.metric("Total Sleep", f"{data['sleep_hours'].sum():.0f} hours")

#     # Create sleep visualization
#     fig = px.area(
#         data,
#         x="sleep_date",
#         y="sleep_hours",
#         title=f"Sleep Duration for User {user_id}",
#         labels={"sleep_hours": "Hours", "sleep_date": "Date"}
#     )
#     fig.update_layout(yaxis_range=[0, 12])
#     return fig


# def plot_activity_intensity(df):
#     """
#     Pie chart for activity intensity breakdown.
#     """
#     intensity_df = df[['VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes', 'SedentaryMinutes']].sum().reset_index()
#     intensity_df.columns = ['Activity Level', 'Minutes']
#     fig = px.pie(intensity_df, names='Activity Level', values='Minutes', title='Activity Intensity Breakdown')
#     st.plotly_chart(fig, use_container_width=True)

# def plot_hourly_activity(df):
#     """
#     Heatmap of activity trends by hour.
#     """
#     if 'ActivityDate' not in df.columns:
#         st.error("Column 'ActivityDate' not found in the data.")
#         return None
    
#     try:
#         df['Hour'] = pd.to_datetime(df['ActivityDate']).dt.hour
#     except Exception as e:
#         st.error(f"Error converting 'ActivityDate' to datetime: {str(e)}")
#         return None
    
#     hourly_activity = df.groupby('Hour').agg({'TotalSteps': 'sum', 'Calories': 'sum'}).reset_index()
#     fig = px.scatter(hourly_activity, x='Hour', y=['TotalSteps', 'Calories'], title='Hourly Activity Trends')
#     st.plotly_chart(fig, use_container_width=True)
    
# def plot_active_vs_sedentary(df):
#     """
#     Scatter plot of Active vs. Sedentary Minutes.
#     """
#     fig = px.scatter(df, x='SedentaryMinutes', y='VeryActiveMinutes', color='Calories',
#                      title='Active vs. Sedentary Minutes')
#     st.plotly_chart(fig, use_container_width=True)

def filter_by_intensity(df, intensity):
    """
    Filter dataframe based on user intensity level.
    """
    if 'VeryActiveMinutes' not in df.columns:
        st.error("Column 'VeryActiveMinutes' not found in the data.")
        return df
    
    if intensity == 'Heavy':
        return df[df['VeryActiveMinutes'] >= 60]
    elif intensity == 'Moderate':
        return df[(df['VeryActiveMinutes'] >= 30) & (df['VeryActiveMinutes'] < 60)]
    elif intensity == 'Light':
        return df[(df['VeryActiveMinutes'] > 0) & (df['VeryActiveMinutes'] < 30)]
    else:
        return df

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

def plot_activity_summary(data):
    """Plot overall activity metrics"""
    if data.empty:
        st.warning("No activity data available")
        return None
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Steps", f"{data['TotalSteps'].sum():,}")
    col2.metric("Avg Daily Calories", f"{data['Calories'].mean():,.0f}")
    col3.metric("Avg Sleep (mins)", f"{data['SleepMinutes'].mean():,.0f}")

def plot_steps_trends(data):
    """Line chart for steps trends over time"""
    fig = px.histogram(data, x="ActivityDate", y="TotalSteps", title="Daily Step Trends")
    st.plotly_chart(fig, use_container_width=True)

def plot_calories_trends(data):
    """Line chart for calorie trends over time"""
    fig = px.histogram(data, x="ActivityDate", y="Calories", title="Calories Burned Over Time", color= "virgil")
    st.plotly_chart(fig, use_container_width=True)

def plot_sleep_trends(data):
    """Line chart for sleep trends over time"""
    fig = px.histogram(data, x="ActivityDate", y="SleepMinutes", title="Sleep Duration Over Time")
    st.plotly_chart(fig, use_container_width=True)

def plot_activity_intensity(df):
    """Pie chart for activity intensity breakdown."""
    intensity_df = df[['VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes', 'SedentaryMinutes']].sum().reset_index()
    intensity_df.columns = ['Activity Level', 'Minutes']
    fig = px.pie(intensity_df, names='Activity Level', values='Minutes', title='Activity Intensity Breakdown')
    st.plotly_chart(fig, use_container_width=True)

def plot_hourly_activity(df):
    """Heatmap of activity trends by hour."""
    df['Hour'] = pd.to_datetime(df['ActivityDate']).dt.hour
    hourly_activity = df.groupby('Hour').agg({'TotalSteps': 'sum', 'Calories': 'sum'}).reset_index()
    fig = px.line(hourly_activity, x='Hour', y=['TotalSteps', 'Calories'], title='Hourly Activity Trends')
    st.plotly_chart(fig, use_container_width=True)

def plot_active_vs_sedentary(df):
    """Scatter plot of Active vs. Sedentary Minutes."""
    fig = px.scatter(df, x='SedentaryMinutes', y='VeryActiveMinutes', color='Calories',
                     title='Active vs. Sedentary Minutes')
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")

def plot_step_distribution(df):
    """Histogram for step distribution across users."""
    fig = px.histogram(df, x='TotalSteps', nbins=10, title='Step Distribution')
    st.plotly_chart(fig, use_container_width=True)

def plot_steps_vs_calories(df):
    """Scatter plot for steps vs. calories burned."""
    fig = px.scatter(df, x='TotalSteps', y='Calories', title='Steps vs. Calories Burned')
    st.plotly_chart(fig, use_container_width=True)

def plot_sleep_vs_activity(df):
    """Scatter plot for sleep minutes vs activity level."""
    fig = px.scatter(df, x='SleepMinutes', y='VeryActiveMinutes', title='Sleep vs. Activity Level')
    st.plotly_chart(fig, use_container_width=True)

def plot_top_users(df):
    """Leaderboard for top active users."""
    top_users = df.groupby('Id')['TotalSteps'].sum().nlargest(5).reset_index()
    fig = px.bar(top_users, x='Id', y='TotalSteps', title='Top 5 Most Active Users')
    st.plotly_chart(fig, use_container_width=True)