import re
import urllib.request
import urllib.parse
import http.cookiejar
from urllib.error import URLError

import pandas as pd
from lxml.html import fragment_fromstring
from collections import OrderedDict
import numpy as np
import sqlite3
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from datetime import date
from tkinter import messagebox
import datetime as dt
pd.core.common.is_list_like = pd.api.types.is_list_like
# import pandas_datareader.data as web
import Calc_pb_v2 as calc
import FundamentusREV1 as hist

#  BUSCA DADOS NO SITE DO FUNDAMENTUS
def busca_fundamentus(*args, **kwargs):

    try:
        url = 'http://www.fundamentus.com.br/resultado.php'
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201'),
                             ('Accept', 'text/html, text/plain, text/css, text/sgml, */*;q=0.01')]

        # Aqui estão os parâmetros de busca das ações
        # Estão em branco para que retorne todas as disponíveis
        data = {'pl_min': '',
                'pl_max': '',
                'pvp_min': '',
                'pvp_max': '',
                'psr_min': '',
                'psr_max': '',
                'divy_min': '',
                'divy_max': '',
                'pativos_min': '',
                'pativos_max': '',
                'pcapgiro_min': '',
                'pcapgiro_max': '',
                'pebit_min': '',
                'pebit_max': '',
                'fgrah_min': '',
                'fgrah_max': '',
                'firma_ebit_min': '',
                'firma_ebit_max': '',
                'margemebit_min': '',
                'margemebit_max': '',
                'margemliq_min': '',
                'margemliq_max': '',
                'liqcorr_min': '',
                'liqcorr_max': '',
                'roic_min': '',
                'roic_max': '',
                'roe_min': '',
                'roe_max': '',
                'liq_min': '',
                'liq_max': '',
                'patrim_min': '',
                'patrim_max': '',
                'divbruta_min': '',
                'divbruta_max': '',
                'tx_cresc_rec_min': '',
                'tx_cresc_rec_max': '',
                'setor': '',
                'negociada': 'ON',
                'ordem': '1',
                'x': '28',
                'y': '16'}

        with opener.open(url, urllib.parse.urlencode(data).encode('UTF-8')) as link:
            content = link.read().decode('ISO-8859-1')

        pattern = re.compile('<table id="resultado".*</table>', re.DOTALL)
        reg = re.findall(pattern, content)[0]
        page = fragment_fromstring(reg)
        lista = OrderedDict()

        for rows in page.xpath('tbody')[0].findall("tr"):
            lista.update({rows.getchildren()[0][0].getchildren()[0].text: {'cotacao': rows.getchildren()[1].text,
                                                                           'P/L': rows.getchildren()[2].text,
                                                                           'P/VP': rows.getchildren()[3].text,
                                                                           'PSR': rows.getchildren()[4].text,
                                                                           'DY': rows.getchildren()[5].text,
                                                                           'P/Ativo': rows.getchildren()[6].text,
                                                                           'P/Cap.Giro': rows.getchildren()[7].text,
                                                                           'P/EBIT': rows.getchildren()[8].text,
                                                                           'P/Ativ.Circ.Liq.': rows.getchildren()[9].text,
                                                                           'EV/EBIT': rows.getchildren()[10].text,
                                                                           'EBITDA': rows.getchildren()[11].text,
                                                                           'Mrg.Liq.': rows.getchildren()[12].text,
                                                                           'Liq.Corr.': rows.getchildren()[13].text,
                                                                           'ROIC': rows.getchildren()[14].text,
                                                                           'ROE': rows.getchildren()[15].text,
                                                                           'Liq.2m.': rows.getchildren()[16].text,
                                                                           # Linha filtrada na hora de buscar os dados
                                                                           'Pat.Liq': rows.getchildren()[17].text,
                                                                           # Linha suprimida por não conseguir converter os dados
                                                                           'Div.Brut/Pat.': rows.getchildren()[18].text,
                                                                           'Cresc.5a': rows.getchildren()[19].text}})

        # TRANSFORMA A LISTA DE DICIONÁRIO PARA DATAFRAME
        df = pd.DataFrame.from_dict(lista, orient='index')

        # CONVERTENDO DATAFRAME STRING EM FLOAT
        for ind, column in enumerate(df.columns):
            df[column] = df.iloc[:, ind]
            df[column] = df[column].str.replace('.', "")
            df[column] = df[column].str.replace(',|%', '').astype(float)
            df[column] = df[column].divide(100)

        # CRIAÇÃO DAS COLUNAS PARA INCLUIR EMPRESAS FINANCEIRAS
        df['P/L(fin)_EV/EBIT'] = np.where(df['PSR'] == 0, df['P/L'], df['EV/EBIT'])
        df['ROE(fin)_ROIC'] = np.where(df['PSR'] == 0, df['ROE'], df['ROIC'])

        # CRIAÇÃO DOS RANKINGS

        df = df.sort_values(by='P/L(fin)_EV/EBIT')
        df['Ranking_EV/EBIT'] = range(1, len(df) + 1)
        df = df.sort_values(by='ROE(fin)_ROIC', ascending=False)
        df['Ranking_ROIC'] = range(1, len(df) + 1)
        df = df.sort_values(by='DY', ascending=False)
        df['Ranking_DY'] = range(1, len(df) + 1)
        df = df.sort_values(by='P/VP')
        df['Ranking_P/VP'] = range(1, len(df) + 1)
        df = df.sort_values(by='Cresc.5a', ascending=False)
        df['Ranking_Cresc.5a'] = range(1, len(df) + 1)
        col_list = ['Ranking_EV/EBIT', 'Ranking_ROIC', 'Ranking_DY', 'Ranking_P/VP', 'Ranking_Cresc.5a']
        df['SOMA'] = df[col_list].sum(axis=1)
        df = df.sort_values(by='SOMA')

        Div = [calc_div_inint(acao) for acao in df.index]
        Div = pd.Series(Div)
        df['Ano Inicio Div.'] = Div.values

        # COLUNA DO DECIL
        lista1 = np.array(range(1, len(df) + 1))
        Int = int(len(df) / 10)
        df['Decil'] = (lista1 / Int) + 1

        # SALVA NO BANCO DE DADOS
        c = sqlite3.connect("dados_basicos_pb.db")
        df.to_sql("FUNDAMENTUS", c, if_exists="replace")

    except:
        messagebox.showerror('Erro Fundamentus','Não foi possível atualizar os dados do FUNDAMENTUS')

# CALCULA DIVIDENDOS ININTERRUPTOS POR AÇÃO PARA OS DADOS DO FUNDAMENTUS
def calc_div_inint(acao):

    try:
        global Corte, Ano_atual
        srt_inicio = 'http://www.fundamentus.com.br/proventos.php?papel='
        srt_meio = acao
        str_fim = '&tipo=2.php'
        site = srt_inicio + srt_meio + str_fim

        url = urlopen(site)
        bsOBJ = bs(url, 'lxml')
        Dados = (bsOBJ.findAll('td'))
        Valores = [link.string for link in Dados]  # Resultset no formato Lista

        linhas = int(len(Valores) / 4)
        Colunas = ['Data', 'Valor', 'Tipo', 'Fator']
        df = pd.DataFrame(np.array(Valores).reshape(linhas, 4), columns=Colunas)
        Datas = pd.to_datetime(df['Data'])
        Anos = list(Datas.dt.year)

        hj = date.today()
        Ano_atual = hj.year
        Rang = range(0, len(Anos) - 1, 1)

        if Anos == []:
            Corte = Ano_atual
        else:
            if (Ano_atual - Anos[0]) <= 1 and len(Anos) > 1:
                for k in Rang:
                    if (Anos[k] - Anos[k + 1]) <= 1:
                        Corte = Anos[k]
                    else:
                        Corte = Anos[k]
                        break
            else:
                Corte = Ano_atual
    except:
        Corte = Ano_atual

    return Corte

def atualiza_ipca_ibov(hj):
    # CONECTA AO BANCO DE DADOS
    c = sqlite3.connect("dados_basicos_pb.db")
    try:
        # COLETA IPCA
        IPCA = pd.read_csv('http://api.bcb.gov.br/dados/serie/bcdata.sgs.13522/dados/ultimos/18?formato=csv',
                           error_bad_lines=False, encoding="ISO-8859-1", sep=';')

        IPCA_db = pd.read_sql("SELECT * FROM IPCA", c)

        ultima_data_db = list(IPCA_db['data'])[-1]
        ultima_data_db = dt.datetime.strptime(ultima_data_db, '%d/%m/%Y')

        ultima_data_web = list(IPCA['data'])[-1]
        ultima_data_web = dt.datetime.strptime(ultima_data_web, '%d/%m/%Y')

        d_mes = calc.dif_mes(ultima_data_web, ultima_data_db)

        # SEPARA OS ÚLTIMOS VALORES NECESSÁRIOS PARA O DB
        append_ipca = IPCA.tail(d_mes)

        # SALVA IPCA
        append_ipca.to_sql("IPCA", c, if_exists="append")

    except:
        messagebox.showerror("Erro em obter o IPCA", "Problemas na conexão ao site do IPCA \n Tente novamente !")

    try:
        # COLETA IBOV do DB e do GOOGLE
        IBOV_db = pd.read_sql("SELECT * FROM IBOV", c)

        IBOV = web.DataReader('IBOV', 'google', hj - dt.timedelta(days=400), hj)['Close']
        IBOV = IBOV.resample('BM').apply(lambda x: x[-1])  # PEGA O IBOV DO ÚLTIMO DIA ÚTIL

        ultima_data_db = list(IBOV_db['Date'])[-1]
        ultima_data_db = dt.datetime.strptime(ultima_data_db, '%Y-%m-%d %H:%M:%S')

        ultima_data_web = list(IBOV.index)[-1]

        d_mes = calc.dif_mes(ultima_data_web, ultima_data_db)

        # SEPARA OS ÚLTIMOS VALORES NECESSÁRIOS PARA O DB
        append_ibov = IBOV.tail(d_mes)

        # SALVA IBOV
        append_ibov.to_sql("IBOV", c, if_exists="append")
    except:
        try:
            tent_yahoo = messagebox.askyesno("Erro em obter o IBOV", "Falha no Google. \n Tentar pelo Yahoo ?")
            if tent_yahoo == True:
                # COLETA IBOV do DB e do YAHOO
                IBOV_db = pd.read_sql("SELECT * FROM IBOV", c)

                IBOV = web.get_data_yahoo('^BVSP', hj - dt.timedelta(days=400), hj)['Adj Close']
                IBOV = IBOV.resample('BM').apply(lambda x: x[-1])  # PEGA O IBOV DO ÚLTIMO DIA ÚTIL
                IBOV.rename('Close', inplace=True)
                ultima_data_db = list(IBOV_db['Date'])[-1]
                ultima_data_db = dt.datetime.strptime(ultima_data_db, '%Y-%m-%d %H:%M:%S')

                ultima_data_web = list(IBOV.index)[-1]

                if calc.dif_mes(ultima_data_web,hj)== 0:
                    IBOV.drop(IBOV.index[len(IBOV)-1],inplace=True)
                    ultima_data_web = list(IBOV.index)[-1]

                d_mes = calc.dif_mes(ultima_data_web, ultima_data_db)

                # SEPARA OS ÚLTIMOS VALORES NECESSÁRIOS PARA O DB
                append_ibov = IBOV.tail(d_mes)

                # SALVA IBOV
                append_ibov.to_sql("IBOV", c, if_exists="append")
        except:
            messagebox.showerror("Erro em obter o IBOV", "Falha no Yahoo. \n Tente novamente !")

    # BUSCA O CDI
    c.close()

def salva_cdi_txt():
    str1 = 'ftp://ftp.cetip.com.br/MediaCDI/'
    str3 = '.txt'
    datas = [(dt.datetime.today() - dt.timedelta(days=dia)) for dia in range(1, 1400)]
    fora_da_lista = []
    with open('cdi.txt', 'w') as cdi:
        cdi.write('Data,Taxa CDI\n')
        for data in datas:
            str2 = dt.datetime.strftime(data, '%Y%m%d')
            str4 = dt.datetime.strftime(data, '%d/%m/%Y')
            link = str1 + str2 + str3
            try:
                f = urlopen(link)
                g = f.read().decode('utf-8').replace('\n', '').replace(' ', '')
                cdi.write(str4 + ',' + g[:-2] + '.' + g[-2:] + '\n')
            except URLError:
                fora_da_lista.append(data)
    print(fora_da_lista)

def salva_cdi_db():
    df = pd.read_csv('cdi.txt', sep=',').sort_index(ascending=False)
    df.set_index(keys='Data', inplace=True)
    c = sqlite3.connect("dados_basicos_pb.db")
    df.to_sql("CDI", c, if_exists="replace")
    c.close()

def atualiza_cdi():
    str1 = 'ftp://ftp.cetip.com.br/MediaCDI/'
    str3 = '.txt'

    # CRIA LISTA DE DATAS DOS ULTIMOS 60 DIAS
    datas = [(dt.datetime.today() - dt.timedelta(days=dia)) for dia in range(1, 60)]
    fora_da_lista = []
    data_cdi_web = 0

    # BUSCA NO SITA AS TAXAS CDI E SALVA EM TXT E INFORMA A ÚLTIMA DATA DE ATUALIZAÇÃO
    with open('cdi_atualiza.txt', 'w') as cdi_web:
        cdi_web.write('Data,Taxa CDI\n')
        for data in datas:
            str2 = dt.datetime.strftime(data, '%Y%m%d')
            str4 = dt.datetime.strftime(data, '%d/%m/%Y')
            link = str1 + str2 + str3
            try:
                f = urlopen(link)
                g = f.read().decode('utf-8').replace('\n', '').replace(' ', '')
                cdi_web.write(str4 + ',' + g[:-2] + '.' + g[-2:] + '\n')
                data_cdi_web = data
            except URLError:
                fora_da_lista.append(data)

    # BUSCA NO DB A LISTAGEM DO CDI E A ÚLTIMA DATA ATUALIZADA
    c = sqlite3.connect('dados_basicos_pb.db')
    cdi_db = pd.read_sql('SELECT * FROM CDI', c)
    data_cdi_db = list(cdi_db['Data'])[-1]
    data_cdi_db = dt.datetime.strptime(data_cdi_db, '%d/%m/%Y')

    data_cdi_web = datas[0]

    # CALCULA A DIFERENCA DE MESES ENTRE AS DATAS DO SITE E DO DB
    if data_cdi_db.date() != data_cdi_web.date():
        data_cdi_db1 = list(cdi_db['Data'])[-1]
        data_cdi_db1 = dt.datetime.strptime(data_cdi_db1, '%d/%m/%Y')

        # SALVA NO DB AS LINHAS NECESSÁRIAS PARA ATUALIZAÇÃO DO DB DO CDI
        df = pd.read_csv('cdi_atualiza.txt', sep=',').sort_index(ascending=False)
        df['Data'] = pd.to_datetime(df['Data'].astype(str))
        append_cdi = df[(df['Data'] > data_cdi_db1)]
        append_cdi['Data'] = df['Data'].apply(lambda x: x.strftime('%d/%m/%Y'))
        append_cdi.set_index(keys='Data', inplace=True)
        append_cdi.to_sql("CDI", c, if_exists="append")

        # CRIA COLUNA DO FATOR DIARIO DO CDI
        fator_db = pd.read_sql('SELECT * FROM CDI', c)
        fator_db['Fator'] = ((fator_db['Taxa CDI'] / 100) + 1) ** (1 / 252)
        fator_db.set_index(keys='Data', inplace=True)
        fator_db.to_sql("CDI", c, if_exists="replace")
        c.close()

def setor_subsetor(acao):

    srt_inicio = 'http://www.fundamentus.com.br/detalhes.php?papel='
    srt_meio = str(acao)
    str_fim = '&tipo=2.php'
    site = srt_inicio + srt_meio + str_fim

    req = Request(site, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) Version/7.0.3 Safari/7046A194A'})
    url = urlopen(req).read()
    bsOBJ = bs(url, 'lxml')
    dados = (bsOBJ.findAll('a'))

    setor = dados[14].string
    subsetor = dados[15].string

    return setor, subsetor

def atualiza_hist_fund():
    c = sqlite3.connect('dados_basicos_pb.db')
    df = pd.read_sql_query("SELECT * FROM FUNDAMENTUS", c)

    d = sqlite3.connect('SetoresAcoes.db')
    dff = pd.read_sql("SELECT * FROM SetoresAcoes", d, index_col='Acao')

    hj = dt.datetime.today()
    df['Dia'] = str(hj)[:10]

    for i in range(len(df)):
        papel = df.loc[i, 'index']
        try:
            setor = dff.loc[papel, 'Setor']
            subsetor = dff.loc[papel, 'Subsetor']

            df.loc[i, 'Setor'] = setor
            df.loc[i, 'Subsetor'] = subsetor
        except:
            try:
                setor_i, sub_setor_i = setor_subsetor(i)
                df.loc[i, 'Setor'] = setor_i
                df.loc[i, 'Subsetor'] = sub_setor_i
            except:
                df.loc[i, 'Setor'] = 'ERRO'
                df.loc[i, 'Subsetor'] = 'ERRO'

    c.close()
    
    c = sqlite3.connect('hist_fundamentus.db')
    df.to_sql('HISTFUNDAMENTUS', c, if_exists="append", index=False)
    c.close()
    
    # hist.HistFundamentus()

if __name__ == '__main__':

    #hj = dt.datetime.now()
    #atualiza_ipca_ibov(hj)
    busca_fundamentus()
