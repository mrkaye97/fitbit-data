import fitbit
import gather_keys_oauth2 as Oauth2
import pandas as pd
import datetime
from sqlalchemy import create_engine
import sys

database_username = 'root'
database_password = sys.argv[1]    # db password as command line arg
database_ip = 'localhost:3306'
database_name = 'fitbit'

engine = create_engine('mysql+pymysql://{}:{}@{}/{}'.format(database_username,
                                                            database_password,
                                                            database_ip,
                                                            database_name),
                       echo=False)

CLIENT_ID = "22B8T7"
CLIENT_SECRET = "05645289a684308b40e5cef4a002223e"


def hr():
    if date_check('heartrate', yesterday2) == -1:
        return None

    fit_statsHR = auth2_client.intraday_time_series('activities/heart', base_date=yesterday2, detail_level='1sec')

    heartdf = (pd
               .DataFrame.from_dict(fit_statsHR['activities-heart-intraday']['dataset'])
               .rename(columns={'value': 'hr'})
               .assign(date=datetime.datetime.strptime(yesterday2, "%Y-%m-%d").date())
               .filter(['date', 'time', 'hr']))

    heartdf.to_sql('heartrate', con=engine, if_exists='append', index=False)


def sleep():
    if date_check('sleep', today2) == -1:
        return None

    fit_statsSum = auth2_client.sleep(date='today')['sleep'][0]
    ssummarydf = pd.DataFrame({'date': pd.to_datetime(fit_statsSum['dateOfSleep']).date(),
                               'mainSleep': fit_statsSum['isMainSleep'],
                               'minutesAsleep': fit_statsSum['minutesAsleep'],
                               'minutesAwake': fit_statsSum['minutesAwake'],
                               'awakenings': fit_statsSum['awakeCount'],
                               'restlessCount': fit_statsSum['restlessCount'],
                               'restlessDuration': fit_statsSum['restlessDuration'],
                               'timeInBed': fit_statsSum['timeInBed']
                               }, index=[0])

    ssummarydf.to_sql('sleep',
                      con=engine,
                      if_exists='append',
                      index=False)

def water():
    if date_check('water', yesterday2) == -1:
        return None

    fit_statsWater = auth2_client.foods_log_water(date=yesterday2)
    df = pd.DataFrame.from_dict({'date': [datetime.datetime.today().date()],'water': [fit_statsWater['summary']['water']]})

    df.to_sql('water',
              con=engine,
              if_exists='append',
              index=False)

def date_check(tab, date):
    temp = (pd
          .read_sql_table(tab, con=engine)
          )

    temp.columns = map(str.lower, temp.columns)

    if datetime.datetime.strptime(date, "%Y-%m-%d").date() in set(temp['date'].dt.date):
        print("Data from yesterday in database {} already exists".format(tab))
        return -1

    else:
        return 1


if __name__ == '__main__':
    server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
    server.browser_authorize()
    ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
    REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])
    auth2_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN,
                                 refresh_token=REFRESH_TOKEN)

    yesterday = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d"))
    yesterday2 = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
    today = str(datetime.datetime.now().strftime("%Y%m%d"))
    today2 = str(datetime.datetime.now().strftime("%Y-%m-%d"))

    sleep()
    hr()
    water()
