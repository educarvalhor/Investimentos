import datetime as dt
import sqlite3 as sql
import pandas as pd
import os

papel = 'GGBR3'.ljust(12)

ano_atual_cot = str(dt.datetime.today().year)
con = sql.connect(os.getcwd()+'\\base\\'+'db_hist_' + ano_atual_cot + '.db')
fech_ano = pd.read_sql_query("SELECT PREULT FROM hist_bovespa WHERE CODNEG = '"+papel+"'", con)
ultima_cot = list(fech_ano['PREULT'])[-1]
con.commit()
con.close()

print(ultima_cot)
