# fitbit

https://python-fitbit.readthedocs.io/en/latest/


## Description:

This repository contains two python files, data_pull.py and make_plots.py. data_pull.py hooks into the Fitbit API (with a given client ID and secret) and pulls Fitbit statistics. 

## Plot Example:

![](users/matt/documents/github/fitbit/viz/sleepplot.svg)

## Methods:

**hr()** for minute-by-minute heart rate data, given a date

**sleep()** for all sleep logs, including time slept, start and end times, nap / main sleep, restless count, etc., given a date

**water()** for how much water was logged, given a date

**basicactivity()** for data on steps, active minutes, sedentary minutes, etc., given a date

**hrzones()** for data on how long was spent in each heart rate zone (peak, cardio, fat burn, other), given a date

**fill_missing_data()** will call all five above methods for a specified date range, and is meant to be run if the program doesn't execute on some day or set of days

**date_check()** ensures no duplicates in the database

**daterange()** is a helper method to yield a range of dates (analogous to the range() function, but for dates)


All date parameters for each method defaults to the previous day. All methods (except for daterange() and date_check()) do not return. If date_check() returns -1, then the method that called it returns None and nothing is uploaded to the SQL database. Otherwise, new rows are appended to a SQL table in database fitbit with the specified name.

## Setup and Use:

This project **not** runnable or useful (unless you want my Fitbit data) without registering an application with the Fitbit API and getting your own client ID and secret. Steps to get set up:

1. First, [**go here**](https://towardsdatascience.com/collect-your-own-fitbit-data-with-python-ff145fa10873) and follow the instructions to authorize yourself to use the API.
2. **SAVE YOUR CLIENT ID AND CLIENT SECRET!** You'll need them in the next step.
3. Then, in data_pull.py, change the database parameters (username, ip, name) to whatever mySQL database you want to use for storing the data. Keep in mind that the tables in the database **MUST** have the same names as mine.
4. Change the CLIENT_ID and CLIENT_SECRET to your newly saved ones (from when you authorized yourself with the API)
5. Run data_pull.py and give it a test run!

## Command Line Arguments:

--p YOUR_MYSQL_PASSWORD (mandatory)

--m (defaults to yesterday, specifying "fill" will allow you to fill a range of dates from a set start date to yesterday)

--s (start date for fill in format %Y-%m-%d without quotation marks. Does not do anything if --m fill is not set.)


