import statsmodels.formula.api as smf
import pandas as pd

def classify_user(df):
    user_counts = df.groupby('Id').size()
    categories = pd.cut(user_counts, bins=[0, 10, 15, float('inf')], labels=['Light', 'Moderate', 'Heavy'])
    # fourth-change: DELETE " 'Id': user_counts.index, " for cutting the redundancy
    return pd.DataFrame({'Class': categories})

def linear_regression(df):
    df['Id'] = df['Id'].astype(str)  
    model = smf.ols('Calories ~ TotalSteps + C(Id)', data=df).fit()
    return model