import pandas as pd
from sqlalchemy import create_engine
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import sys

database_username = 'root'
database_password = sys.argv[1]
database_ip = 'localhost:3306'
database_name = 'fitbit'

engine = create_engine('mysql+pymysql://{}:{}@{}/{}'.format(database_username,
                                                            database_password,
                                                            database_ip,
                                                            database_name),
                       echo=False)

df = (pd
      .read_sql_table('heartrate', con=engine)
      .assign(datetime=lambda x: pd.to_datetime(x.date.apply(str) + ' ' + x.time.apply(str)))
      .sort_values(by='datetime')
      .assign(day=lambda x: x.datetime.dt.date,
              daymean=lambda x: x.hr.rolling(1440).mean())
      .filter(['datetime', 'hr', 'daymean'])
      )

plt.style.use('ggplot')
fig, ax = plt.subplots()
ax.plot(df.datetime, df.hr, alpha = .2)
ax.plot(df.datetime, df.daymean)
#ax.set_xticks(df.datetime)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax.xaxis.set_minor_formatter(mdates.DateFormatter("%Y-%m"))
_=plt.xticks(rotation=90)
plt.show()

df = (pd
      .read_sql_table('sleep', con=engine)
      .filter(items=['date', 'minutesAsleep', 'minutesAwake', 'restlessCount', 'awakenings', 'restlessDuration', 'timeInBed'])
      .groupby('date')
      .sum()
      .assign(rollmean=lambda x: x.minutesAsleep.rolling(2).mean())
      )

fig, ax = plt.subplots()
ax.plot(df.index, df.minutesAsleep)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax.xaxis.set_minor_formatter(mdates.DateFormatter("%Y-%m"))
_=plt.xticks(rotation=90)
plt.show()
