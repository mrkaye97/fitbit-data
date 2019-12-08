import pandas as pd
from sqlalchemy import create_engine
from matplotlib import pyplot
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
      .filter(['datetime', 'hr'])
      )

ts = (df
      .set_index('datetime')
      )

ts = (ts
      .groupby([ts.index.date, ts.index.hour])
      .mean()
      )

pyplot.style.use('ggplot')
ts.plot(linewidth = .9, alpha = .5)
pyplot.show()
