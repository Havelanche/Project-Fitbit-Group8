import os
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from data_processing import load_data, get_unique_users
from analysis import classify_user
from database import connect_db, SQL_acquisition

# Load data
DB_NAME = 'fitbit_database.db'
DATA_FILE = 'daily_activity.csv'

df = load_data(DATA_FILE)
df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], errors='coerce')
user_classes = classify_user(df)

# Connect to the database
connection = connect_db(DB_NAME)

app = dash.Dash(__name__)
app.title = 'Fitbit Data Dashboard'

def user_profile_image():
    return 'https://www.w3schools.com/w3images/avatar2.png'

def create_summary_card(title, value, icon):
    return html.Div(style={
        'border': '1px solid #ddd',
        'borderRadius': '10px',
        'padding': '20px',
        'textAlign': 'center',
        'width': '250px',
        'backgroundColor': '#f9f9f9',
        'boxShadow': '0px 4px 8px rgba(0,0,0,0.1)'
    }, children=[
        html.Img(src=icon, style={'width': '50px', 'marginBottom': '10px'}),
        html.H4(title, style={'margin': '5px 0'}),
        html.H2(value, style={'margin': '5px 0', 'color': '#007BFF'})
    ])
    
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px'}, children=[
    html.H1('📊 Fitbit Data Dashboard', style={'textAlign': 'center', 'marginBottom': '40px'}),

    html.Div(style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'gap': '20px', 'marginBottom': '40px'}, children=[
        html.Img(src=user_profile_image(), style={'width': '100px', 'borderRadius': '50%'}),
        html.Div([
            html.Label('Select a User:', style={'fontSize': '18px', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='user-dropdown',
                options=[{'label': user_id, 'value': user_id} for user_id in df['Id'].unique()],
                value=df['Id'].iloc[0],
                clearable=True,
                placeholder='Search for a user...'
            )
        ])
    ]),

    html.Div(id='summary-cards', style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '40px'}),

    html.Div([
        dcc.Graph(id='distance-distribution'),
        dcc.Graph(id='calories-burned'),
        dcc.Graph(id='workout-count'),
        dcc.Graph(id='steps-vs-calories'),
    ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '30px'}),
])

# Callback for updating graphs and summary cards
@app.callback(
    [
        Output('distance-distribution', 'figure'),
        Output('calories-burned', 'figure'),
        Output('workout-count', 'figure'),
        Output('steps-vs-calories', 'figure'),
        Output('summary-cards', 'children')
    ],
    Input('user-dropdown', 'value')
)
def update_graphs(selected_user):
    user_data = df[df['Id'] == selected_user]

    fig_distance = px.histogram(
        user_data, x=user_data['TotalDistance'].round(3), nbins=10, title='Total Distance Distribution',
        color_discrete_sequence=['#007BFF'], template='simple_white'
    )
    fig_distance.update_layout(
        xaxis_title='Total Distance (km)',
        yaxis_title='Frequency',
        bargap=0.2
    )

    fig_calories = px.line(user_data, x='ActivityDate', y='Calories', title=f'Calories Burned by User {selected_user}')
    fig_workout = px.histogram(user_data, x=user_data['ActivityDate'].dt.day_name(), title='Workout Count by Day')
    fig_steps_vs_calories = px.scatter(user_data, x='TotalSteps', y='Calories', trendline='ols', title='Steps vs. Calories')

    total_steps = user_data['TotalSteps'].sum()
    total_calories = user_data['Calories'].sum()
    active_minutes = user_data['VeryActiveMinutes'].sum() + user_data['FairlyActiveMinutes'].sum()

    summary_cards = [
        create_summary_card('Total Steps', f'{total_steps:,}', 'https://cdn-icons-png.flaticon.com/512/747/747376.png'),
        create_summary_card('Calories Burned', f'{total_calories:,}', 'https://cdn-icons-png.flaticon.com/512/3176/3176364.png'),
        create_summary_card('Active Minutes', f'{active_minutes:,}', 'https://cdn-icons-png.flaticon.com/512/865/865836.png')
    ]

    return fig_distance, fig_calories, fig_workout, fig_steps_vs_calories, summary_cards

if __name__ == '__main__':
    app.run_server(debug=True)
    connection.close()
