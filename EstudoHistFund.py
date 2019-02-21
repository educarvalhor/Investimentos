import sqlite3 as sql
import pandas as pd


c = sql.connect('HistFundamentus.db')
df = pd.read_sql('SELECT * FROM HistFundamentus', c)

colunas = list(df.columns)
colunas = colunas[2:20]

for column in colunas:
    df[column] = df[column].str.replace('.', "")
    df[column] = df[column].str.replace(',|%', '').astype(float)
    df[column] = df[column].divide(100)

datas = df['Data'].unique()

df_medianas = pd.DataFrame()
for data in datas:
    df_temp = df[df['Data'] == data]
    mediana = df_temp.median(axis=0)
    df_temp_med = mediana.to_frame().T
    df_medianas = df_medianas.append(df_temp_med)

df_medianas = df_medianas.set_index(datas)
print(df_medianas)