import pandas as pd
import numpy as np
import os

#Dicionário que irá armazenar os dados. As keys serão o ano
lista_df = {}

for filename in os.listdir(os.getcwd()):
    if filename.endswith(".TXT"):
        print(filename)
        ind = filename[10:14]
        df_temp = pd.read_csv(str(filename), encoding='cp860')
        df_temp.drop(df_temp.tail(1).index,inplace=True)
        df_temp.columns = ['tudo']
        lista_df[ind] = df_temp

#Faz os slices para gerar as colunas
for chave in lista_df.keys():
    lista_df[chave]['DATA'] = lista_df[chave]['tudo'].str.slice(2,10)
    lista_df[chave]['CODNEG'] = lista_df[chave]['tudo'].str.slice(12,24)
    lista_df[chave]['TPMERC'] = lista_df[chave]['tudo'].str.slice(25,27)
    lista_df[chave]['NOMRES'] = lista_df[chave]['tudo'].str.slice(28,39)
    lista_df[chave]['PRAZOT'] = lista_df[chave]['tudo'].str.slice(50,52)
    lista_df[chave]['MODREF'] = lista_df[chave]['tudo'].str.slice(52,55)
    lista_df[chave]['PREABE'] = lista_df[chave]['tudo'].str.slice(57,69)
    lista_df[chave]['PREMAX'] = lista_df[chave]['tudo'].str.slice(70,82)
    lista_df[chave]['PREMIN'] = lista_df[chave]['tudo'].str.slice(83,95)
    lista_df[chave]['PREMED'] = lista_df[chave]['tudo'].str.slice(96,108)
    lista_df[chave]['PREULT'] = lista_df[chave]['tudo'].str.slice(109,121)
    lista_df[chave]['PREOFC'] = lista_df[chave]['tudo'].str.slice(122,134)
    lista_df[chave]['PREOFV'] = lista_df[chave]['tudo'].str.slice(135,147)
    lista_df[chave]['TOTNEG'] = lista_df[chave]['tudo'].str.slice(148,152)
    lista_df[chave]['QUATOT'] = lista_df[chave]['tudo'].str.slice(153,170)
    lista_df[chave]['VOLTOT'] = lista_df[chave]['tudo'].str.slice(171,188)
    lista_df[chave]['PREEXE'] = lista_df[chave]['tudo'].str.slice(189,201)
    lista_df[chave]['FATCOT'] = lista_df[chave]['tudo'].str.slice(211,217)
    lista_df[chave]['DISMES'] = lista_df[chave]['tudo'].str.slice(243,245)

#Exclui algumas colunas
for chave in lista_df.keys():
    lista_df[chave] = lista_df[chave].iloc[:,[1,2,5,6,7,8,9,10,11,12,13,14,15,16,17,19]]

#Ajusta os tipos
for chave in lista_df.keys():
    lista_df[chave]['DATA'] = pd.to_datetime(lista_df[chave]['DATA'].astype(str), format='%Y%m%d')
    lista_df[chave]['PREABE'] = lista_df[chave]['PREABE'].astype(float)/100
    lista_df[chave]['PREMAX'] = lista_df[chave]['PREMAX'].astype(float)/100
    lista_df[chave]['PREMIN'] = lista_df[chave]['PREMIN'].astype(float)/100
    lista_df[chave]['PREMED'] = lista_df[chave]['PREMED'].astype(float)/100
    lista_df[chave]['PREULT'] = lista_df[chave]['PREULT'].astype(float)/100
    lista_df[chave]['PREOFC'] = lista_df[chave]['PREOFC'].astype(float)/100
    lista_df[chave]['PREOFV'] = lista_df[chave]['PREOFV'].astype(float)/100
    lista_df[chave]['TOTNEG'] = lista_df[chave]['TOTNEG'].astype(float)/100
    lista_df[chave]['QUATOT'] = lista_df[chave]['QUATOT'].astype(np.int64)
    lista_df[chave]['VOLTOT'] = lista_df[chave]['VOLTOT'].astype(float)/100
    lista_df[chave]['PREEXE'] = lista_df[chave]['PREEXE'].astype(float)/100
    lista_df[chave]['DISMES'] = lista_df[chave]['DISMES'].astype(int)
lista_df['2018'].head()

#Salva um db por cada ano
import sqlite3 as sql
for chave in lista_df.keys():
    c = sql.connect('db_hist_'+chave+'.db')
    lista_df[chave].to_sql(name='hist_bovespa', con=c, if_exists="replace")
    c.commit()
    c.close()