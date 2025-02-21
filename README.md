##Project-Fitbit-group8

##Project Description
```
```

## Function Explaination & Usage

``` load_data(filename):
This function can convert the csv file into a dataframe for future using.
```

``` get_unique_users(df, str):
This function can find the distinct user IDs in the dataframe and count each user's specific data, such as Total Distance or total Steps.
It needs 2 parameters. 'df': The dataframe to be analyzed. 'str': The column name of the dataframe, to sum up the column's total counts of each user.
```

``` plot_distance_distribution(unique_users):
This function plots 35 distinct users' total distance of running in a histogram, illustrating the distribution.
It needs 1 parameter. obtained from the second function's return.
```

``` calories_burned_per_day(df, user_id, start_date=None, end_date=None):
This function plots a user's daily burned calories in a certain period in a line graph.
It needs 4 parameters. 'df': The dataframe to be analyzed. 'user_id': The user you want to investigate. 'start_date' & 'end_date': The interval of a certain period. 
```

``` plot_workout(df):
This function plots
```

``` plot_LRM(df, user_id):
```

``` classify_user(df):
```

``` SQL_acquisition(str):
This function allows you to use SQL query commands in Python, by converting the data from database into dataframe.
It needs 1 parameter. 'str': The SQL query you want to use to acquire the data from database, such that, "SELECT * FROM daily_activities"
```

``` verify_total_steps(df):
This function can verify if the total steps recorded in csv file are the same as those recorded in the database by comparing them.
It needs 1 parameter. 'df': The dataframe to be analyzed.
```
```
