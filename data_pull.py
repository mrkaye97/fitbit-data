import sys
import fitbit
import gather_keys_oauth2 as Oauth2
import pandas as pd
import datetime
from sqlalchemy import create_engine
import time
import numpy as np
import argparse

yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).date()

parser = argparse.ArgumentParser()
parser.add_argument("--p", type=str, help="enter SQL password",
                    nargs='?', default=0, const=0)
parser.add_argument("--s", type=str, help='set start date',
                    nargs='?', default=None, const=None)
args = parser.parse_args()

database_username = 'root'
database_password = args.p  # db password as command line arg
database_ip = 'localhost:3306'
database_name = 'fitbit'

engine = create_engine('mysql+pymysql://{}:{}@{}/{}'.format(database_username,
                                                            database_password,
                                                            database_ip,
                                                            database_name),
                       echo=False)

CLIENT_ID = "22B8T7"
CLIENT_SECRET = "05645289a684308b40e5cef4a002223e"

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

    try:
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

    except:
        pass


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
                   'activityCalories': activity['activityCalories'],
                   'caloriesBMR': activity['caloriesBMR'],
                   'caloriesOut': activity['caloriesOut'],
                   'marginalCalories': activity['marginalCalories'],
                   'sedentaryMinutes': activity['sedentaryMinutes'],
                   'lightlyActiveMinutes': activity['lightlyActiveMinutes'],
                   'fairlyActiveMinutes': activity['fairlyActiveMinutes'],
                   'veryActiveMinutes': activity['veryActiveMinutes'],
                   'restingHeartRate': activity['restingHeartRate'],
                   'steps': activity['steps']
                   }, index=[0])
     .to_sql('basicactivity',
             con=engine,
             if_exists='append',
             index=False)
     )


def hrzones(date=yesterday):
    if date_check('hrzones', date) == -1:
        return None

    (pd
     .DataFrame(auth2_client.activities(date=date)['summary']['heartRateZones'])
     .assign(date=date)
     .filter(['date', 'name', 'min', 'max', 'minutes', 'caloriesOut'])
     .to_sql(name='hrzones',
             con=engine,
             if_exists='append',
             index=False)
     )


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + datetime.timedelta(n)


def date_check(tab, date):
    temp = pd.read_sql_table(tab, con=engine)
    temp.columns = map(str.lower, temp.columns)

    if date in np.unique(temp['date'].dt.date):
        print("Data from {} in database {} already exists".format(date, tab))
        return -1
    else:
        return 1


def fill_missing_dates(s):
    start = s
    end = yesterday

    all_dates = np.unique([date for date in daterange(start, end)])
    dates_exist = np.unique(pd.read_sql_table('sleep', con=engine)['date'].dt.date)

    diff = np.setdiff1d(all_dates, dates_exist)
    i = 0

    for date in diff:
        if i == 30:
            print(datetime.datetime.now().strftime("%H:%M:%S"))
            time.sleep(3600)

        print(date)
        sleep(date)
        hr(date)
        water(date)
        basicactivity(date)
        hrzones(date)

        i += 1


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


    if args.s is not None:
        fill_missing_dates(datetime.datetime.strptime(args.s, '%Y-%m-%d').date())

    else:
        fill_missing_dates(yesterday - datetime.timedelta(30))
