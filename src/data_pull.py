import fitbit
import gather_keys_oauth2 as Oauth2
import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import argparse
import time
import datetime

yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).date()

parser = argparse.ArgumentParser()
parser.add_argument("--p", type=str, help="enter SQL password",
                    nargs='?', default=0, const=0)
parser.add_argument("--s", type=str, help='set start date',
                    nargs='?', default=None, const=None)
parser.add_argument("--id", type=str, help='set client id',
                    nargs='?', default=None, const=None)
parser.add_argument("--sec", type=str, help='set client secret',
                    nargs='?', default=None, const=None)
args = parser.parse_args()

database_username = 'matt'
database_password = args.p  # db password as command line arg
database_ip = 'localhost'
database_name = 'fitbit'

engine = create_engine('postgresql+pg8000://{}:{}@{}/{}'.format(database_username,
                                                                database_password,
                                                                database_ip,
                                                                database_name),
                       echo=False)

CLIENT_ID = args.id
CLIENT_SECRET = args.sec

def hr(date = yesterday):
    if date_check('heartrate', date) == -1:
        return None

    fit_statsHR = auth2_client.intraday_time_series('activities/heart', base_date=date, detail_level='1min')

    (pd
     .DataFrame.from_dict(fit_statsHR['activities-heart-intraday']['dataset'])
     .rename(columns={'value': 'hr'})
     .assign(date=date)
     .filter(['date', 'time', 'hr'])
     .to_sql('heartrate',
             con=engine,
             if_exists='append',
             index=False)
     )


def sleep(date=yesterday):
    if date_check('sleep', date) == -1:
        return None

    for x in auth2_client.sleep(date=date)['sleep']:

        (pd
         .DataFrame({'date': pd.to_datetime(x['dateOfSleep']).date(),
                     'mainSleep': x['isMainSleep'],
                     'startTime': x['startTime'],
                     'endTime': x['endTime'],
                     'minutesAsleep': x['minutesAsleep'],
                     'minutesAwake': x['minutesAwake'],
                     'awakenings': x['awakeCount'],
                     'restlessCount': x['restlessCount'],
                     'restlessDuration': x['restlessDuration'],
                     'timeInBed': x['timeInBed'],
                     'efficiency': x['efficiency']
                     }, index=[0])
         .to_sql('sleep',
                 con=engine,
                 if_exists='append',
                 index=False)
         )



def water(date=yesterday):
    if date_check('water', date) == -1:
        return None

    x = auth2_client.foods_log_water(date=date)

    (pd
     .DataFrame.from_dict({'date': [date], 'water': [x['summary']['water']]})
     .to_sql('water',
             con=engine,
             if_exists='append',
             index=False)
     )


def basicactivity(date=yesterday):
    if date_check('basicactivity', date) == -1:
        return None

    # change to one line
    activity = auth2_client.activities(date=date)['summary']

    (pd.DataFrame({'date': date,
                   'activityCalories': activity['activityCalories'] if 'activityCalories' in activity.keys() else None,
                   'caloriesBMR': activity['caloriesBMR'] if 'caloriesBMR' in activity.keys() else None,
                   'caloriesOut': activity['caloriesOut'] if 'caloriesOut' in activity.keys() else None,
                   'marginalCalories': activity['marginalCalories'] if 'marginalCalories' in activity.keys() else None,
                   'sedentaryMinutes': activity['sedentaryMinutes'] if 'sedentaryMinutes' in activity.keys() else None,
                   'lightlyActiveMinutes': activity['lightlyActiveMinutes'] if 'lightlyActiveMinutes' in activity.keys() else None,
                   'fairlyActiveMinutes': activity['fairlyActiveMinutes'] if 'fairlyActiveMinutes' in activity.keys() else None,
                   'veryActiveMinutes': activity['veryActiveMinutes'] if 'veryActiveMinutes' in activity.keys() else None,
                   'restingHeartRate': activity['restingHeartRate'] if 'restingHeartRate' in activity.keys() else None,
                   'steps': activity['steps'] if 'steps' in activity.keys() else None
                   }, index=[0])
     .to_sql('basicactivity',
             con=engine,
             if_exists='append',
             index=False)
     )


def hrzones(date=yesterday):
    if date_check('hrzones', date) == -1:
        return None

    activity = auth2_client.activities(date=date)['summary']
    if 'heartRateZones' in activity.keys():
        (pd
         .DataFrame(activity['heartRateZones'])
         .assign(date=date)
         .filter(['date', 'name', 'min', 'max', 'minutes', 'caloriesOut'])
         .to_sql(name='hrzones',
                 con=engine,
                 if_exists='append',
                 index=False)
         )
    else:
        pass

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + datetime.timedelta(n)


def date_check(tab, date):

    if not engine.dialect.has_table(engine, tab):
        return 1
    else:
        temp = set(pd.read_sql_query(" ".join(["select distinct date from", str(tab)]), engine)['date'])

    if date in temp:
        print("Data from {} in database {} already exists".format(date, tab))
        return -1
    else:
        return 1


def tryfunc(fn, date):
    try:
        fn(date)
    except fitbit.exceptions.HTTPTooManyRequests:
        print("Too many requests from Fitbit API. Waiting for 1 minute starting at " + str(datetime.datetime.now()))
        time.sleep(60)
        print("Trying again")
        tryfunc(fn, date)


def fill_missing_dates(s):
    start = s
    end = yesterday

    all_dates = np.unique([date for date in daterange(start, end)])

    for date in all_dates:

        funcs = [
            sleep,
            hr,
            water,
            basicactivity,
            hrzones
        ]

        print(date)
        [tryfunc(f, date) for f in funcs]



def check_for_db():
    try:
        engine.connect()
    except:
        engine.execution_options(isolation_level="AUTOCOMMIT").execute("CREATE DATABASE fitbit")


if __name__ == '__main__':
    server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
    server.browser_authorize()
    ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
    REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])
    auth2_client = fitbit.Fitbit(CLIENT_ID,
                                 CLIENT_SECRET,
                                 oauth2=True,
                                 access_token=ACCESS_TOKEN,
                                 refresh_token=REFRESH_TOKEN)

    check_for_db()

    if args.s is not None:
        fill_missing_dates(datetime.datetime.strptime(args.s, '%Y-%m-%d').date())

    else:
        fill_missing_dates(yesterday - datetime.timedelta(7))
