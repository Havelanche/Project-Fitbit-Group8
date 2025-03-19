import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def show_steps_plot(merged_df):
    daily_avg = merged_df.groupby("ActivityDate")["TotalSteps"].mean().reset_index()
    fig = px.line(daily_avg, x="ActivityDate", y="TotalSteps",
                  title="Average Steps Over Time",
                  labels={"TotalSteps": "Avg Steps", "ActivityDate": "Date"},
                  template="plotly_dark")
    return fig

def show_calories_plot(merged_df):
    daily_calories = merged_df.groupby("ActivityDate")["Calories"].mean().reset_index()
    fig = px.line(daily_calories, x="ActivityDate", y="Calories",
                  title="Average Calories Burned Over Time",
                  labels={"Calories": "Avg Calories", "ActivityDate": "Date"},
                  template="plotly_dark")
    return fig

def show_sleep_plot(merged_df):
    daily_sleep = merged_df.groupby("ActivityDate")["SleepMinutes"].mean().reset_index()
    fig = px.line(daily_sleep, x="ActivityDate", y="SleepMinutes",
                  title="Average Sleep Duration Over Time",
                  labels={"SleepMinutes": "Avg Sleep Minutes", "ActivityDate": "Date"},
                  template="plotly_dark")
    return fig

def plot_step_distance_relationship(champ_daily_df):
    if champ_daily_df.empty:
        st.warning("No daily data available for this user.")
        return

    fig = go.Figure()
    # Add Distance (Line)
    fig.add_trace(go.Scatter(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["TotalDistance"],
        name="Distance (km)",
        line=dict(color="orange"),
        yaxis="y2",
        mode="lines+markers"
    ))
    # Add Steps (Bars)
    fig.add_trace(go.Bar(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["TotalSteps"],
        name="Steps",
        marker_color="blue"
    ))
    # Update layout
    fig.update_layout(
        title=f"Steps vs. Distance",
        xaxis=dict(
            title="Dates",
            showticklabels=False,
            type='category'  # Added to match other plots
        ),
        yaxis=dict(
            title="Steps",
            side="left",
            rangemode='tozero'  # Added axis range behavior
        ),
        yaxis2=dict(
            title="Distance (km)",
            side="right",
            overlaying="y",
            rangemode='tozero'  # Added axis range behavior
        ),
        hovermode="x unified",
        # Added horizontal legend configuration
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,  # Positions above plot
            xanchor="right",
            x=1  # Right-aligned
        )
    )

    st.plotly_chart(fig)

def plot_calories_vs_activity(champ_daily_df):
    if champ_daily_df.empty:
        st.warning("No daily data available for this user.")
        return

    champ_daily_df = champ_daily_df.sort_values(by="ActivityDate")

    fig = go.Figure()
    
    # Calories (Line)
    fig.add_trace(go.Scatter(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["Calories"],
        name="Calories (kcal)",
        line=dict(color="red"),
        yaxis="y2",
        mode="lines+markers"
    ))
    # Active Minutes (Bar)
    fig.add_trace(go.Bar(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["VeryActiveMinutes"],
        name="Very Active Minutes",
        marker_color="green"
    ))
    # Layout
    fig.update_layout(
        title=f"Calories vs. Very Active Minutes",
        xaxis=dict(
            title="Dates",
            showticklabels=False,
            type='category'  # Added to match first plot's date handling
        ),
        yaxis=dict(
            title="Very Active Minutes",
            side="left",
            rangemode='tozero'  # Added to match axis behavior
        ),
        yaxis2=dict(
            title="Calories (kcal)",
            side="right",
            overlaying="y",
            rangemode='tozero'  # Added to match axis behavior
        ),
        hovermode="x unified",
        # Added legend configuration to match first plot
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,  # Positions legend just above the plot
            xanchor="right",
            x=1  # Right-aligns legend
        )
    )
    st.plotly_chart(fig)

def plot_sleep_distribution(champ_daily_df):
    # Check for required columns
    required_cols = ['AsleepMinutes', 'RestlessMinutes', 'AwakeMinutes', 'SedentaryMinutes']
    if champ_daily_df.empty or not all(col in champ_daily_df for col in required_cols):
        st.warning("No sleep data available for this user.")
        return

    # Sort data by date
    champ_daily_df = champ_daily_df.sort_values(by="ActivityDate")

    # Create figure
    fig = go.Figure()
    
    # Add stacked sleep state bars
    fig.add_trace(go.Bar(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["AsleepMinutes"],
        name='Deep Sleep',
        marker_color='#2ca02c',  # Green
        hoverinfo='y+name'
    ))
    
    fig.add_trace(go.Bar(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["RestlessMinutes"],
        name='Restless Sleep',
        marker_color='#ff7f0e',  # Orange
        hoverinfo='y+name'
    ))
    
    fig.add_trace(go.Bar(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["AwakeMinutes"],
        name='Awake Time',
        marker_color='#d62728',  # Red
        hoverinfo='y+name'
    ))
    
    # Add sedentary line
    fig.add_trace(go.Scatter(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["SedentaryMinutes"],
        name='Sedentary Time',
        line=dict(color="blue", width=2),  # Gray
        yaxis='y2',
        mode='lines+markers',
        hoverinfo='y+name'
    ))
    
    # Update layout
    fig.update_layout(
        barmode='stack',  # Stack sleep states
        title=f"Sleep Quality vs. Sedentary Time",
        xaxis=dict(
            title="Dates",
            showticklabels=False,
            type='category'  # Prevent date interpolation
        ),
        yaxis=dict(
            title="Sleep Minutes",
            side="left",
            rangemode='tozero'
        ),
        yaxis2=dict(
            title="Sedentary Minutes",
            side="right",
            overlaying="y",
            rangemode='tozero'
        ),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig)

def plot_sleep_correlations(champ_daily_df):
    # Select relevant columns
    corr_df = champ_daily_df[['TotalSteps', 'TotalDistance', 'VeryActiveMinutes', 
                            'SedentaryMinutes', 'Calories', 'AsleepMinutes']]
    
    # Calculate correlations
    corr_matrix = corr_df.corr()
    
    fig = px.imshow(
        corr_matrix,
        labels=dict(color="Correlation"),
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        color_continuous_scale='RdBu',
        zmin=-1,
        zmax=1)
    
    # Update layout for better label placement
    fig.update_layout(
        title="Sleep-Activity Correlation Matrix",
        xaxis=dict(
            side='bottom',  # Move x-axis labels to top
            tickangle=-15  # Angle labels for better readability
        ),
        yaxis=dict(
            side='left',  # Keep y-axis on left
            tickangle=-15
        ),
        margin=dict(l=10, r=10, t=50, b=20) ) # Adjust margins
    
    # Improve text visibility
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    
    st.plotly_chart(fig)

def plot_sleep_efficiency(champ_daily_df):
    # Calculate sleep efficiency metric
    champ_daily_df['SleepEfficiency'] = champ_daily_df['AsleepMinutes'] / (
        champ_daily_df['AsleepMinutes'] + champ_daily_df['RestlessMinutes'] + champ_daily_df['AwakeMinutes'])
    
    fig = px.scatter(
    champ_daily_df,
    x='VeryActiveMinutes',
    y='SleepEfficiency',
    trendline='lowess',
    color='TotalSteps',
    size='Calories',
    hover_data=['ActivityDate'],
    labels={
        'VeryActiveMinutes': 'Very Active Minutes',
        'SleepEfficiency': 'Sleep Efficiency (%)',
        'TotalSteps': 'Daily Steps'
    },
    color_continuous_scale=["white", "lightblue", "blue"]  # Color scale change
    )
    
    # Optional: Add explicit colorbar title
    fig.update_layout(
        title='Sleep Efficiency vs Physical Activity',
        coloraxis_colorbar=dict(
            title='Daily Steps',
            tickvals=[5000, 10000, 15000],
            ticktext=['5k', '10k', '15k']),
        margin=dict(l=10, r=10, t=50, b=20)) # Adjust margins
    
    st.plotly_chart(fig)

def plot_steps_vs_sleep(champ_daily_df):
    fig = go.Figure()
    
    # Add steps trace
    fig.add_trace(go.Scatter(
        x=champ_daily_df['ActivityDate'],
        y=champ_daily_df['TotalSteps'],
        name='Steps',
        line=dict(color='blue'),
        yaxis='y1', mode="lines+markers"
    ))
    
    # Add sleep trace
    fig.add_trace(go.Scatter(
        x=champ_daily_df['ActivityDate'],
        y=champ_daily_df['AsleepMinutes'],
        name='Sleep Minutes',
        line=dict(color='green'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='Daily Steps vs Sleep Duration',
        yaxis=dict(title='Steps', side='left', rangemode='tozero'),
        yaxis2=dict(title='Sleep Minutes', side='right', overlaying='y', rangemode='tozero'),
        hovermode='x unified',
                # Added horizontal legend configuration
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,  # Positions above plot
            xanchor="right",
            x=1  # Right-aligned
        )
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
        title="Daily Step Trends",
        labels={"TotalSteps": "Steps", "ActivityDate": "Date"},
        color_discrete_sequence=["#1f77b4"]  # Blue color
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Steps Taken",
        hovermode="x unified",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_calories_trends(data):
    fig = px.histogram(
        data, x="Calories",
        title="Calories Burned Over Time",
        labels={"Calories": "Calories Burned"},
        color_discrete_sequence=["#ff5733"],
        nbins=20
    )

    fig.update_layout(
        xaxis_title="Calories Burned",
        yaxis_title="Frequency",
        template="seaborn"
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_sleep_trends(data):
    if data.empty:
        st.warning("No sleep data available.")
        return

    fig = px.bar(
        data, 
        x="ActivityDate", 
        y="SleepMinutes", 
        title="Sleep Duration Over Time",
        labels={"SleepMinutes": "Minutes Asleep", "ActivityDate": "Date"},
        color_discrete_sequence=["#4B0082"]  # Purple color
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Minutes Asleep",
        hovermode="x unified",
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_activity_intensity(df):
    # Aggregate total minutes spent in different intensity levels
    intensity_df = df[['VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes', 'SedentaryMinutes']].sum().reset_index()
    intensity_df.columns = ['Activity Level', 'Minutes']

    # Sort values for better visualization
    intensity_df = intensity_df.sort_values(by="Minutes", ascending=False)

    # *DONUT CHART* with better insights
    fig1 = px.pie(
        intensity_df, 
        names='Activity Level', 
        values='Minutes', 
        hole=0.4, 
        color='Activity Level',
        title="Activity Intensity Breakdown",
        color_discrete_map={
            "SedentaryMinutes": "#264653",  # Dark blue
            "LightlyActiveMinutes": "#2A9D8F",  # Teal
            "FairlyActiveMinutes": "#E9C46A",  # Yellow
            "VeryActiveMinutes": "#E63946"  # Red
        }
    )

    # *Enhance labels with percentages*
    fig1.update_traces(
        textinfo="percent+label",
        pull=[0.1 if m == intensity_df['Minutes'].max() else 0 for m in intensity_df['Minutes']]
    )

    st.plotly_chart(fig1, use_container_width=True)

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
        title="Heart Rate Trends (Excluding 66 BPM)",
        labels={'HeartRate': 'Heart Rate (BPM)', 'ActivityDate': 'Date'},
        color_discrete_sequence=['#d62728']
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Heart Rate (BPM)",
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
        title=" Very Active vs. Sedentary Minutes",
        labels={"SedentaryMinutes": "Sedentary Minutes", "VeryActiveMinutes": "Very Active Minutes"},
        color_continuous_scale="blues"
    )

    fig.update_layout(
        xaxis_title="Sedentary Minutes",
        yaxis_title="Very Active Minutes",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_step_distribution_for_all_user(df):
    fig = go.Figure()
    fig = px.histogram(
        df, 
        x='TotalSteps', 
        title="Step Distribution for All Users", 
        nbins=20, 
        color_discrete_sequence=["#008000"]
    )

    fig.update_layout(
        xaxis=dict(title="Total Steps"),
        yaxis=dict(title="Frequency"),
        hovermode="x unified",
        template="seaborn"
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_steps_vs_calories(df):
    fig = px.scatter(
        df, 
        x='TotalSteps', 
        y='Calories',
        title="Steps vs. Calories Burned",
        labels={"TotalSteps": "Total Steps", "Calories": "Calories Burned"},
        color="Calories",
        color_continuous_scale="greens"
    )

    fig.update_layout(
        xaxis_title="Steps Taken",
        yaxis_title="Calories Burned",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_sleep_vs_activity(df):
    fig = px.scatter(
        df, 
        x='SleepMinutes', 
        y='VeryActiveMinutes',
        title="Sleep vs. Activity Level",
        labels={"SleepMinutes": "Minutes Asleep", "VeryActiveMinutes": "Very Active Minutes"},
        color="VeryActiveMinutes",
        color_continuous_scale="purples"
    )

    fig.update_layout(
        xaxis_title="Sleep Minutes",
        yaxis_title="Very Active Minutes",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_individual_metrics(user_df):
    # 1. Calories Burned each day - using orange color
    fig_calories = px.line(
        user_df, 
        x='ActivityDate', 
        y='Calories',
        title="Daily Calories Burned",
        markers=True,
        line_shape='linear',
        color_discrete_sequence=['orange']  # Set specific color
    )
    fig_calories.update_layout(
        xaxis_title="Date",
        yaxis_title="Calories",
        height=400
    )
    st.plotly_chart(fig_calories, use_container_width=True)
    
    # 2. Steps each day - using blue color - CHANGED TO BAR CHART
    fig_steps = px.bar(  # Changed from px.line to px.bar
        user_df, 
        x='ActivityDate', 
        y='TotalSteps',
        title="Daily Steps",
        color_discrete_sequence=['blue']  # Set specific color
    )
    fig_steps.update_layout(
        xaxis_title="Date",
        yaxis_title="Steps",
        height=400
    )
    st.plotly_chart(fig_steps, use_container_width=True)
    
    # 3. Distance each day - using green color
    fig_distance = px.line(
        user_df, 
        x='ActivityDate', 
        y='TotalDistance',
        title="Daily Distance Traveled",
        markers=True,
        line_shape='linear',
        color_discrete_sequence=['green']  # Set specific color
    )
    fig_distance.update_layout(
        xaxis_title="Date",
        yaxis_title="Distance (km)",
        height=400
    )
    st.plotly_chart(fig_distance, use_container_width=True)
    
    # 4. Sleep duration each day - using purple color - CHANGED TO BAR CHART
   
    sleep_column = 'TotalMinutesAsleep' if 'TotalMinutesAsleep' in user_df.columns else 'SleepMinutes'
    if sleep_column in user_df.columns:
        fig_sleep = px.bar(  # Changed from px.line to px.bar
            user_df, 
            x='ActivityDate', 
            y=sleep_column,
            title="Daily Sleep Duration",
            color_discrete_sequence=['purple']  # Set specific color
        )
        fig_sleep.update_layout(
            xaxis_title="Date",
            yaxis_title="Sleep Duration (minutes)",
            height=400
        )
        st.plotly_chart(fig_sleep, use_container_width=True)
    else:
        st.warning("Sleep data not available for this user")
