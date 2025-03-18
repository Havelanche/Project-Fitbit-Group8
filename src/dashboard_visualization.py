import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import streamlit as st


def plot_step_distance_relationship(champ_daily_df):
    if champ_daily_df.empty:
        st.warning("No daily data available for this user.")
        return

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
        title=f"Steps vs. Distance",
        xaxis=dict(title="Dates", showticklabels=False),  # Hides individual dates
        yaxis=dict(title="Steps", side="left"),
        yaxis2=dict(title="Distance (km)", side="right", overlaying="y"),
        hovermode="x unified"
    )

    st.plotly_chart(fig)

def plot_calories_vs_activity(champ_daily_df):
    if champ_daily_df.empty:
        st.warning("No daily data available for this user.")
        return

    champ_daily_df = champ_daily_df.sort_values(by="ActivityDate")

    fig = go.Figure()
    # Active Minutes (Bar)
    fig.add_trace(go.Bar(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["VeryActiveMinutes"],
        name="Very Active Minutes",
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
        title=f"Calories vs. Very Active Minute",
        xaxis=dict(title="Dates", showticklabels=False),
        yaxis=dict(title="Very Active Minutes", side="left"),
        yaxis2=dict(title="Calories (kcal)", side="right", overlaying="y"),
        hovermode="x unified"
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
        line=dict(color='#7f7f7f', width=2),  # Gray
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
        zmax=1
    )
    
    # Update layout for better label placement
    fig.update_layout(
        title="Sleep-Activity Correlation Matrix",
        xaxis=dict(
            side='bottom',  # Move x-axis labels to top
            tickangle=-15  # Angle labels for better readability
        ),
        yaxis=dict(
            side='left'  # Keep y-axis on left
        ),
        margin=dict(l=100, r=20, t=100, b=20)  # Adjust margins
    )
    
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
        'VeryActiveMinutes': 'Active Minutes',
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
            ticktext=['5k', '10k', '15k']
        )
    )
    
    st.plotly_chart(fig)

def plot_steps_vs_sleep(champ_daily_df):
    fig = go.Figure()
    
    # Add steps trace
    fig.add_trace(go.Scatter(
        x=champ_daily_df['ActivityDate'],
        y=champ_daily_df['TotalSteps'],
        name='Steps',
        line=dict(color='blue'),
        yaxis='y1'
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
        yaxis=dict(title='Steps', side='left'),
        yaxis2=dict(title='Sleep Minutes', side='right', overlaying='y'),
        hovermode='x unified'
    )
    st.plotly_chart(fig)
