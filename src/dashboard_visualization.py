import pandas as pd
import numpy as np
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
    merged_df["ActivityDate"] = pd.to_datetime(merged_df["ActivityDate"])
    merged_df["SleepMinutes"] = merged_df["SleepMinutes"].fillna(0)
    daily_sleep = merged_df.groupby("ActivityDate")["SleepMinutes"].mean().reset_index()
    missing_dates = pd.date_range(start=daily_sleep["ActivityDate"].min(), end=daily_sleep["ActivityDate"].max())
    missing = set(missing_dates) - set(daily_sleep["ActivityDate"])
    if missing:
        print("Missing dates in sleep data:", missing)
    fig = px.line(daily_sleep, x="ActivityDate", y="SleepMinutes",
                  title="Average Sleep Duration Over Time",
                  labels={"SleepMinutes": "Avg Sleep (mins)", "ActivityDate": "Date"},
                  template="plotly_dark")
    return fig

def plot_step_distance_relationship(champ_daily_df):
    if champ_daily_df.empty:
        st.warning("No daily data available for this user.")
        return
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["TotalDistance"],
        name="Distance (km)",
        line=dict(color="orange"),
        yaxis="y2",
        mode="lines+markers"
    ))
    fig.add_trace(go.Bar(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["TotalSteps"],
        name="Steps",
        marker_color="purple"
    ))
    fig.update_layout(
        title=f"Steps vs. Distance",
        xaxis=dict(
            title="Dates",
            showticklabels=False,
            type='category'
        ),
        yaxis=dict(
            title="Steps",
            side="left",
            rangemode='tozero'
        ),
        yaxis2=dict(
            title="Distance (km)",
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

def plot_calories_vs_activity(champ_daily_df):
    if champ_daily_df.empty:
        st.warning("No daily data available for this user.")
        return
    champ_daily_df = champ_daily_df.sort_values(by="ActivityDate")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["Calories"],
        name="Calories (kcal)",
        line=dict(color="red"),
        yaxis="y2",
        mode="lines+markers"
    ))
    fig.add_trace(go.Bar(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["VeryActiveMinutes"],
        name="Very Active Minutes",
        marker_color="yellow"
    ))
    fig.update_layout(
        title=f"Calories vs. Very Active Minutes",
        xaxis=dict(
            title="Dates",
            showticklabels=False,
            type='category'
        ),
        yaxis=dict(
            title="Very Active Minutes",
            side="left",
            rangemode='tozero'
        ),
        yaxis2=dict(
            title="Calories (kcal)",
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

def plot_sleep_distribution(champ_daily_df):
    required_cols = ['AsleepMinutes', 'RestlessMinutes', 'AwakeMinutes', 'SedentaryMinutes']
    if champ_daily_df.empty or not all(col in champ_daily_df for col in required_cols):
        st.warning("No sleep data available for this user.")
        return
    champ_daily_df = champ_daily_df.sort_values(by="ActivityDate")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["AsleepMinutes"],
        name='Deep Sleep',
        marker_color='#2ca02c',
        hoverinfo='y+name'
    ))
    fig.add_trace(go.Bar(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["RestlessMinutes"],
        name='Restless Sleep',
        marker_color='#ff7f0e',
        hoverinfo='y+name'
    ))
    fig.add_trace(go.Bar(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["AwakeMinutes"],
        name='Awake Time',
        marker_color='#d62728',
        hoverinfo='y+name'
    ))
    fig.add_trace(go.Scatter(
        x=champ_daily_df["ActivityDate"],
        y=champ_daily_df["SedentaryMinutes"],
        name='Sedentary Time',
        line=dict(color="blue", width=2),
        yaxis='y2',
        mode='lines+markers',
        hoverinfo='y+name'
    ))
    fig.update_layout(
        barmode='stack',
        title=f"Sleep Quality vs. Sedentary Time",
        xaxis=dict(
            title="Dates",
            showticklabels=False,
            type='category'
        ),
        yaxis=dict(
            title="Sleep (mins)",
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
    corr_df = champ_daily_df[['TotalSteps', 'TotalDistance', 'VeryActiveMinutes', 
                            'SedentaryMinutes', 'Calories', 'AsleepMinutes']]
    corr_matrix = corr_df.corr()
    fig = px.imshow(
        corr_matrix,
        labels=dict(color="Correlation"),
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        color_continuous_scale='RdBu',
        zmin=-1,
        zmax=1)
    fig.update_layout(
        title="Sleep-Activity Correlation Matrix",
        xaxis=dict(
            side='bottom',
            tickangle=-15
        ),
        yaxis=dict(
            side='left',
            tickangle=-15
        ),
        margin=dict(l=10, r=10, t=50, b=20))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    st.plotly_chart(fig)

def plot_sleep_efficiency(champ_daily_df):
    df = champ_daily_df.copy()
    
    denominator = df['AsleepMinutes'] + df['RestlessMinutes'] + df['AwakeMinutes']
    df['SleepEfficiency'] = np.where(denominator > 0, 
                                     df['AsleepMinutes'] / denominator,
                                     np.nan)
    
    df_clean = df.dropna(subset=['SleepEfficiency'])
    
    if len(df_clean) < len(df) * 0.5:  # If more than half the data is missing
        st.warning(f"Only {len(df_clean)} of {len(df)} days have sleep data.")
    
    if len(df_clean) == 0:
        st.error("No sleep data available for this user.")
        return
    
    fig = px.scatter(
        df_clean,
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
        color_continuous_scale=["white", "lightblue", "blue"]
    )
    
    fig.update_layout(
        title='Sleep Efficiency vs Physical Activity',
        coloraxis_colorbar=dict(
            title='Daily Steps',
            tickvals=[5000, 10000, 15000],
            ticktext=['5k', '10k', '15k']),
        margin=dict(l=10, r=10, t=50, b=20))
    
    st.plotly_chart(fig)

def plot_steps_vs_sleep(champ_daily_df):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=champ_daily_df['ActivityDate'],
        y=champ_daily_df['TotalSteps'],
        name='Steps',
        line=dict(color='blue'),
        yaxis='y1', mode="lines+markers"
    ))
    
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
        yaxis2=dict(title='Sleep (mins)', side='right', overlaying='y', rangemode='tozero'),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02, 
            xanchor="right",
            x=1 
        )
    )
    st.plotly_chart(fig)
    
# Champion visualization functions for the leaderboard page
def plot_steps_champion_chart(conn, user_id):
    """
    Plot bar chart for the Step Master showing total steps over time with average comparison
    """
    # Query for the selected user's data
    user_query = f"""
        SELECT 
            ActivityDate, 
            TotalSteps
        FROM daily_activity
        WHERE Id = {user_id}
        ORDER BY ActivityDate
    """
    user_df = pd.read_sql(user_query, conn)
    
    # Query for all users' average data
    avg_query = """
        SELECT 
            ActivityDate, 
            AVG(TotalSteps) as AvgSteps
        FROM daily_activity
        GROUP BY ActivityDate
        ORDER BY ActivityDate
    """
    avg_df = pd.read_sql(avg_query, conn)
    
    user_df['ActivityDate'] = pd.to_datetime(user_df['ActivityDate'])
    avg_df['ActivityDate'] = pd.to_datetime(avg_df['ActivityDate'])
    
    user_df = user_df.sort_values('ActivityDate')
    avg_df = avg_df.sort_values('ActivityDate')
    
    merged_df = pd.merge(user_df[['ActivityDate']], avg_df, on='ActivityDate', how='left')
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=merged_df['ActivityDate'],
            y=merged_df['AvgSteps'],
            name="Community",
            line=dict(color='orange', width=2, dash='dash')
        )
    )

    fig.add_trace(
        go.Bar(
            x=user_df['ActivityDate'],
            y=user_df['TotalSteps'],
            name=f"Champion",
            marker_color='blue'
        )
    )

    fig.update_layout(
        title=f"Daily Steps Over Time",
        xaxis=dict(
            title="Date",
            showticklabels=False,
            type='category'
        ),
        yaxis=dict(
            title="Steps",
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
    
    return fig

def plot_distance_champion_chart(conn, user_id):
    """
    Plot bar chart for the Distance Champion showing total distance over time with average comparison
    """
    # Query for the selected user's data
    user_query = f"""
        SELECT 
            ActivityDate, 
            TotalDistance
        FROM daily_activity
        WHERE Id = {user_id}
        ORDER BY ActivityDate
    """
    user_df = pd.read_sql(user_query, conn)
    
    # Query for all users' average data
    avg_query = """
        SELECT 
            ActivityDate, 
            AVG(TotalDistance) as AvgDistance
        FROM daily_activity
        GROUP BY ActivityDate
        ORDER BY ActivityDate
    """
    avg_df = pd.read_sql(avg_query, conn)
    
    # Convert dates to datetime
    user_df['ActivityDate'] = pd.to_datetime(user_df['ActivityDate'])
    avg_df['ActivityDate'] = pd.to_datetime(avg_df['ActivityDate'])
    
    # Sort both dataframes by date to ensure proper order
    user_df = user_df.sort_values('ActivityDate')
    avg_df = avg_df.sort_values('ActivityDate')
    
    # Align the average dataframe with user dataframe dates
    merged_df = pd.merge(user_df[['ActivityDate']], avg_df, on='ActivityDate', how='left')
    
    # Create plot
    fig = go.Figure()
     
    # Add line for average distance using the merged dataframe
    fig.add_trace(
        go.Scatter(
            x=merged_df['ActivityDate'],
            y=merged_df['AvgDistance'],
            name="Community",
            line=dict(color='orange', width=2, dash='dash')
        )
    )

    # Add bar chart for user's distance
    fig.add_trace(
        go.Bar(
            x=user_df['ActivityDate'],
            y=user_df['TotalDistance'],
            name=f"Champion",
            marker_color='green'
        )
    )

    # Update layout
    fig.update_layout(
        title=f"Daily Distance Over Time",
        xaxis=dict(
            title="Date",
            showticklabels=False,
            type='category'
        ),
        yaxis=dict(
            title="Distance (km)",
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
    
    return fig

def plot_intensity_champion_chart(conn, user_id): 
    """Plot bar chart for the Activity King/Queen showing average intensity over time with average comparison"""
    
    # Query for all hourly intensity data without filters
    query = f"""
    SELECT Id, ActivityHour, AverageIntensity 
    FROM hourly_intensity 
    ORDER BY ActivityHour
    """
    
    all_data = pd.read_sql(query, conn)
    
    all_data['ActivityHour'] = pd.to_datetime(all_data['ActivityHour'])
    all_data['ActivityDate'] = all_data['ActivityHour'].dt.date
    
    user_data = all_data[all_data['Id'] == user_id].copy()
    
    user_daily_df = user_data.groupby('ActivityDate')['AverageIntensity'].mean().reset_index()
    
    avg_df = all_data.groupby('ActivityDate')['AverageIntensity'].mean().reset_index()
    avg_df.rename(columns={'AverageIntensity': 'AvgIntensity'}, inplace=True)
    
    user_daily_df['ActivityDate'] = pd.to_datetime(user_daily_df['ActivityDate'])
    avg_df['ActivityDate'] = pd.to_datetime(avg_df['ActivityDate'])
    
    user_daily_df = user_daily_df.sort_values('ActivityDate')
    avg_df = avg_df.sort_values('ActivityDate')
    
    merged_df = pd.merge(user_daily_df[['ActivityDate']], avg_df, on='ActivityDate', how='left')
    
    fig = go.Figure()
        
    fig.add_trace(
        go.Scatter(
            x=merged_df['ActivityDate'],
            y=merged_df['AvgIntensity'],
            name="Community",
            line=dict(color='orange', width=2, dash='dash')
        )
    )

    fig.add_trace(
        go.Bar(
            x=user_daily_df['ActivityDate'],
            y=user_daily_df['AverageIntensity'],
            name=f"Champion",
            marker_color='green'
        )
    )
 
    fig.update_layout(
        title=f"Daily Average Intensity Over Time",
        xaxis=dict(
            title="Date",
            showticklabels=False,
            type='category'
        ),
        yaxis=dict(
            title="Average Intensity",
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
    
    return fig

def plot_calories_champion_chart(conn, user_id):
    """
    Plot bar chart for the Calorie Burner showing total calories over time with average comparison
    """
    
    # Query for the selected user's data
    user_query = f"""
        SELECT 
            ActivityDate, 
            Calories
        FROM daily_activity
        WHERE Id = {user_id}
        ORDER BY ActivityDate
    """
    user_df = pd.read_sql(user_query, conn)
    
    # Query for all users' average data
    avg_query = """
        SELECT 
            ActivityDate, 
            AVG(Calories) as AvgCalories
        FROM daily_activity
        GROUP BY ActivityDate
        ORDER BY ActivityDate
    """
    avg_df = pd.read_sql(avg_query, conn)
    
    user_df['ActivityDate'] = pd.to_datetime(user_df['ActivityDate'])
    avg_df['ActivityDate'] = pd.to_datetime(avg_df['ActivityDate'])
    
    user_df = user_df.sort_values('ActivityDate')
    avg_df = avg_df.sort_values('ActivityDate')
    
    merged_df = pd.merge(user_df[['ActivityDate']], avg_df, on='ActivityDate', how='left')
    
    
    fig = go.Figure()
     
    
    fig.add_trace(
        go.Scatter(
            x=merged_df['ActivityDate'],
            y=merged_df['AvgCalories'],
            name="Community",
            line=dict(color='orange', width=2, dash='dash')
        )
    )

    
    fig.add_trace(
        go.Bar(
            x=user_df['ActivityDate'],
            y=user_df['Calories'],
            name=f"Champion",
            marker_color="#E63946"
        )
    )
    
    
    fig.update_layout(
        title=f"Daily Calories Over Time",
        xaxis=dict(
            title="Date",
            showticklabels=False,
            type='category'
        ),
        yaxis=dict(
            title="Calories (kcal)",
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
    
    return fig

#----------------------------------------------------------------   
def plot_steps_trends(data):
    if data.empty:
        st.warning(" No step data available.")
        return
    data = data.sort_values("ActivityDate")  
    data["RollingAvgSteps"] = data["TotalSteps"].rolling(window=7).mean()  

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["ActivityDate"], 
        y=data["TotalSteps"], 
        mode='lines+markers',
        name='Daily Steps',
        line=dict(color='#1F77B4', width=2),
        marker=dict(size=5)
    ))

    fig.add_trace(go.Scatter(
        x=data["ActivityDate"], 
        y=data["RollingAvgSteps"], 
        mode='lines',
        name='7-Day Moving Average',
        line=dict(color='orange', width=3, dash="dash")
    ))

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Steps",
        hovermode="x unified",
        template="plotly_dark",
        font=dict(size=14),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02, 
            xanchor="right",
            x=1  
        )
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_calories_trends(data):
    fig = px.histogram(
        data, 
        x="Calories",
        labels={"Calories": "Calories Burned"},
        color_discrete_sequence=["#E63946"], 
        nbins=25,
        opacity=0.8,
    )
    
    mean_calories = data["Calories"].mean()
    fig.add_vline(x=mean_calories, line_dash="dash", line_color="yellow", annotation_text=f"Avg: {mean_calories:.0f}")

    fig.update_layout(
        xaxis_title="Calories",
        yaxis_title="Frequency",
        template="plotly_dark",
        font=dict(size=14),
        bargap=0.2,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02, 
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_sleep_trends(data):
    if data.empty:
        st.warning("No sleep data available.")
        return

    data = data.sort_values("ActivityDate")  
    data["RollingAvgSleep"] = data["SleepMinutes"].rolling(window=7).mean() 

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data["ActivityDate"], 
        y=data["SleepMinutes"], 
        mode='lines+markers',
        name='Daily Sleep (mins)',
        line=dict(color='#6A0DAD', width=2),
        marker=dict(size=5)
    ))

    fig.add_trace(go.Scatter(
        x=data["ActivityDate"], 
        y=data["RollingAvgSleep"], 
        mode='lines',
        name='7-Day Moving Average',
        line=dict(color='cyan', width=3, dash="dash")
    ))

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Sleep (mins)",
        hovermode="x unified",
        template="plotly_dark",
        font=dict(size=14),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02, 
            xanchor="right",
            x=1  
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_activity_intensity(df):
    intensity_df = df[['VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes', 'SedentaryMinutes']].sum().reset_index()
    intensity_df.columns = ['Activity Level', 'Minutes']

    intensity_df = intensity_df.sort_values(by="Minutes", ascending=False)

    fig1 = px.pie(
        intensity_df, 
        names='Activity Level', 
        values='Minutes', 
        hole=0.4, 
        color='Activity Level',
        color_discrete_map={
            "SedentaryMinutes": "#264653",  # Dark blue
            "LightlyActiveMinutes": "#2A9D8F",  # Teal
            "FairlyActiveMinutes": "#E9C46A",  # Yellow
            "VeryActiveMinutes": "#E63946"  # Red
        }
    )

    fig1.update_traces(
        textinfo="percent+label",
        pull=[0.1 if m == intensity_df['Minutes'].max() else 0 for m in intensity_df['Minutes']]
    )
    fig1.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02, 
            xanchor="right",
            x=1 
        ))

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
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,  
            xanchor="right",
            x=1 
        )
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_active_vs_sedentary(df):
    fig = px.scatter(
        df, 
        x='SedentaryMinutes', 
        y='VeryActiveMinutes', 
        color='Calories',
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
    fig = px.histogram(
        df, 
        x='TotalSteps', 
        nbins=25, 
        color_discrete_sequence=["#2D6A4F"],
        opacity=0.85
    )
    
    mean_steps = df["TotalSteps"].mean()
    fig.add_vline(x=mean_steps, line_dash="dash", line_color="orange", annotation_text=f"Avg: {mean_steps:.0f}")


    fig.update_layout(
        xaxis=dict(title="Total Steps", tickangle=-30),
        yaxis=dict(title="Frequency"),
        template="plotly_dark",
        font=dict(size=14),
        bargap=0.2
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_steps_vs_calories(df):
    fig = px.scatter(
        df, 
        x='TotalSteps', 
        y='Calories',
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
    # 1. Calories Burned each day
    fig_calories = px.line(
        user_df, 
        x='ActivityDate', 
        y='Calories',
        markers=True,
        line_shape='linear',
        color_discrete_sequence=['green']
    )
    fig_calories.update_layout(
        title='Calories Over Time',
        xaxis_title="Date",
        yaxis_title="Calories (kcal)",
        height=350
    )
    st.plotly_chart(fig_calories, use_container_width=True)
    
    # 2. Steps each day
    avg_steps = user_df['TotalSteps'].mean()

    fig_steps = px.bar(
        user_df, 
        x='ActivityDate', 
        y='TotalSteps',
        color_discrete_sequence=['blue']
    )

    fig_steps.add_hline(
        y=avg_steps,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Avg: {avg_steps:.0f}",
        annotation_position="top right"
    )

    fig_steps.update_layout(
        xaxis_title="Date",
        yaxis_title="Steps",
        height=350
    )

    st.plotly_chart(fig_steps, use_container_width=True)
    
    
    # 3. Distance each day
    fig_distance = px.line(
        user_df, 
        x='ActivityDate', 
        y='TotalDistance',
        markers=True,
        line_shape='linear',
        color_discrete_sequence=['orange']
    )
    fig_distance.update_layout(
        title='Distance Over Time',
        xaxis_title="Date",
        yaxis_title="Distance (km)",
        height=350
    )
    st.plotly_chart(fig_distance, use_container_width=True)
    
    # 4. Sleep duration each day
    sleep_column = 'TotalMinutesAsleep' if 'TotalMinutesAsleep' in user_df.columns else 'SleepMinutes'
    if sleep_column in user_df.columns:
        fig_sleep = px.bar(
            user_df, 
            x='ActivityDate', 
            y=sleep_column,
            color_discrete_sequence=['purple']
        )
        fig_sleep.update_layout(
            title='Sleep Over Time',
            xaxis_title="Date",
            yaxis_title="Sleep (mins)",
            height=350,
            yaxis=dict(rangemode="tozero")
        )
        st.plotly_chart(fig_sleep, use_container_width=True)
    else:
        st.warning("Sleep data not available for this user")
