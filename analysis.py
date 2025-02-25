import statsmodels.formula.api as smf
import statsmodels.api as sm
import pandas as pd
from database import SQL_acquisition

def classify_user(df):
    user_counts = df.groupby('Id').size()
    categories = pd.cut(user_counts, bins=[0, 10, 15, float('inf')], labels=['Light', 'Moderate', 'Heavy'])
    # fourth-change: DELETE " 'Id': user_counts.index, " for cutting the redundancy
    return pd.DataFrame({'Class': categories})

def linear_regression(df):
    df['Id'] = df['Id'].astype(str)  
    model = smf.ols('Calories ~ TotalSteps + C(Id)', data=df).fit()
    return model

def active_minutes_vs_sleep(connection):
    query = '''
    SELECT d.Id, d.VeryActiveMinutes + d.FairlyActiveMinutes + d.LightlyActiveMinutes AS ActiveMinutes, s.sleep_minutes
    FROM daily_activity d
    JOIN (
        SELECT Id, logId, COUNT(*) AS sleep_minutes
        FROM minute_sleep
        GROUP BY Id, logId
    ) s ON d.Id = s.Id
    '''
    df = SQL_acquisition(connection, query)
    model = sm.OLS(df['sleep_minutes'], sm.add_constant(df['ActiveMinutes'])).fit()
    print(model.summary())

def sedentary_vs_sleep(connection):
    query = '''
    SELECT d.Id, d.SedentaryMinutes, s.sleep_minutes
    FROM daily_activity d
    JOIN (
        SELECT Id, logId, COUNT(*) AS sleep_minutes
        FROM minute_sleep
        GROUP BY Id, logId
    ) s ON d.Id = s.Id
    '''
    df = SQL_acquisition(connection, query)
    model = sm.OLS(df['sleep_minutes'], sm.add_constant(df['SedentaryMinutes'])).fit()
    print(model.summary())
    