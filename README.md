# fitbit

https://python-fitbit.readthedocs.io/en/latest/


## Description:

This repository contains two python files, data_pull.py and make_plots.py. data_pull.py hooks into the Fitbit API (with a given client ID and secret) and pulls Fitbit statistics. Methods outlined below:


**hr()** for minute-by-minute heart rate data, given a date

**sleep()** for all sleep logs, including time slept, start and end times, nap / main sleep, restless count, etc., given a date

**water()** for how much water was logged, given a date

**basicactivity()** for data on steps, active minutes, sedentary minutes, etc., given a date

**hrzones()** for data on how long was spent in each heart rate zone (peak, cardio, fat burn, other), given a date

**fill_missing_data()** will call all five above methods for a specified date range, and is meant to be run if the program doesn't execute on some day or set of days

**date_check()** ensures no duplicates in the database

**daterange()** is a helper method to yield a range of dates (analogous to the range() function, but for dates)



All date parameters for each method defaults to the previous day. All methods (except for daterange() and date_check()) do not return. If date_check() returns -1, then the method that called it returns None and nothing is uploaded to the SQL database. Otherwise, new rows are appended to a SQL table in database fitbit with the specified name.

