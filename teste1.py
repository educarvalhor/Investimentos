import sqlite3
import pandas as pd
import datetime as dt


c = sqlite3.connect('dados_basicos_pb.db')
df = pd.read_sql_query("SELECT * FROM FUNDAMENTUS", c)
hj = dt.datetime.today()
df['Dia'] = str(hj)[:10]
c.close()
c = sqlite3.connect('hist_fundamentus.db')
df.to_sql('HISTFUNDAMENTUS', c, if_exists="append")
c.close()
