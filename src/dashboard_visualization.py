import plotly.express as px
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

def plot_individual_steps_calories(user_df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add steps trace (primary y-axis)
    fig.add_trace(
        go.Scatter(
            x=user_df['ActivityDate'],
            y=user_df['TotalSteps'],
            name="Steps",
            line=dict(color="blue")
        ),
        secondary_y=False
    )
    
    # Add calories trace (secondary y-axis)
    fig.add_trace(
        go.Scatter(
            x=user_df['ActivityDate'],
            y=user_df['Calories'],
            name="Calories",
            line=dict(color="red")
        ),
        secondary_y=True
    )
    
    # Set titles
    fig.update_layout(
        title_text="Daily Steps and Calories Burned",
        xaxis_title="Date"
    )
    
    # Set y-axes titles
    fig.update_yaxes(title_text="Steps", secondary_y=False)
    fig.update_yaxes(title_text="Calories", secondary_y=True)
    
    # Display the combined chart
    st.plotly_chart(fig, use_container_width=True)
