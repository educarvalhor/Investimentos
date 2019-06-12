#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
__author__ = "Eduardo Rosa"
__version__ = "1.0.1"
__email__ = "educarvalhor@gmail.com"
"""

import sqlite3 as sql
import datetime as dt
from sqlite3 import OperationalError

import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
# from pandas_datareader import data
# import fix_yahoo_finance as yf
# yf.pdr_override()

import numpy as np
# from yahoo_fin import stock_info as si
import time
from functools import wraps
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from os import chdir, getcwd
from functools import reduce
import pandas as pd
from itertools import zip_longest
import os
import sqlite3 as sql
import datetime as dt


path = getcwd()


def dif_mes(d1, d2):
    return d1.date().month - d2.date().month + (d1.date().year - d2.date().year) * 12


def atualiza_ipca_mensal():
    # CONECTA AO BANCO DE DADOS
    c = sql.connect("dados_basicos_pb.db")
    try:
    # COLETA IPCA
        IPCA = pd.read_csv('http://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados/ultimos/48?formato=csv',
                           error_bad_lines=False, encoding="ISO-8859-1", sep=';')

        IPCA_db = pd.read_sql("SELECT * FROM IPCA_MENSAL", c)

        ultima_data_db = list(IPCA_db['data'])[-1]
        ultima_data_db = dt.datetime.strptime(ultima_data_db, '%d/%m/%Y')

        ultima_data_web = list(IPCA['data'])[-1]
        ultima_data_web = dt.datetime.strptime(ultima_data_web, '%d/%m/%Y')

        d_mes = dif_mes(ultima_data_web, ultima_data_db)

        # SEPARA OS ÚLTIMOS VALORES NECESSÁRIOS PARA O DB
        append_ipca = IPCA.tail(d_mes)

        # SALVA IPCA
        append_ipca.to_sql("IPCA_MENSAL", c, if_exists="append")

    except HTTPError as e:
        print("Não foi possível atualizar o IPCA - " + str(e))
    except KeyError as f:
        print("Não foi possível atualizar o IPCA - " + str(f))
    except TimeoutError as t:
        print("Não foi possível atualizar o IPCA - " + str(t))
    except URLError as u:
        print("Não foi possível atualizar o IPCA - " + str(u))

    c.close()

    print("O IPCA está atualizado.")
    return


def atualiza_SELIC():

    # CONECTA AO BANCO DE DADOS
    c = sql.connect("dados_basicos_pb.db")
    try:
    # COLETA SELIC

        SELIC = pd.read_csv('http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/48?formato=csv',
                            error_bad_lines=False, encoding="ISO-8859-1", sep=';')

        SELIC.data = pd.to_datetime(SELIC.data)
        SELIC.valor = SELIC.valor.str.replace(",",".")

        SELIC_DB = pd.read_sql("SELECT * FROM SELIC", c)

        ultima_data_db = list(SELIC_DB['data'])[-1]
        ultima_data_db = dt.datetime.strptime(ultima_data_db, '%Y-%m-%d')

        ultima_data_web = list(SELIC['data'])[-1]

        d_mes = dif_mes(ultima_data_web, ultima_data_db)

        SELIC.data = SELIC.data.dt.date
        # SEPARA OS ÚLTIMOS VALORES NECESSÁRIOS PARA O DB
        append_selic = SELIC.tail(d_mes)

        # SALVA SELIC
        append_selic.to_sql("SELIC", c, if_exists="append")

    except HTTPError as e:
        print("Não foi possível atualizar a SELIC - " + str(e))
    except KeyError as f:
        print("Não foi possível atualizar a SELIC - " + str(f))
    except TimeoutError as t:
        print("Não foi possível atualizar a SELIC - " + str(t))
    except URLError as u:
        print("Não foi possível atualizar a SELIC - " + str(u))
    c.close()

    print("A SELIC foi atualizada.")

    return


def timethis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        r = func(*args, **kwargs)
        end = time.perf_counter()
        print('{}.{} : {}'.format(func.__module__,func.__name__, end - start))
        return r
    return wrapper


def busca_IPCA_m():

    c = sql.connect("dados_basicos_pb.db")
    df = pd.read_sql("SELECT * FROM IPCA_MENSAL", c)
    c.close()
    
    return df


def buscaRendaVar(usuario):

    con = sql.connect(usuario + ".db")
    cursor = con.cursor()

    try:
        lista_acoes = cursor.execute(''' SELECT DISTINCT acao FROM ACOES ''').fetchall()
        lista_acoes = [item[0] for item in lista_acoes]
    except OperationalError as o:
        print("Banco de dados do usuário " + usuario + " não possui Ações.")
        lista_acoes = []

    try:
        lista_fii = cursor.execute(''' SELECT DISTINCT FII FROM FII ''').fetchall()
        lista_fii = [item[0] for item in lista_fii]
    except OperationalError as e:
        print("Banco de dados do usuário " + usuario + " não possui FIIs.")
        lista_fii = []

    con.close()

    return lista_acoes , lista_fii


def buscaRendaFixa(usuario):

    con = sql.connect(usuario + ".db")
    cursor = con.cursor()
    try:
        lista = cursor.execute(''' SELECT DISTINCT titulo FROM RENDA_FIXA ''').fetchall()
        lista = [item[0] for item in lista]
    except sql.OperationalError as e:
        lista = [""]
    con.close()

    return lista


def salvaDB(usuario, tipo_inv, codigo_investimento, tipo, valor, data, qtd, corretagem, ir_prev, prej_lucro,
            tipo_aplicacao ="", data_carencia="", data_vencimento="", tipo_taxa="", valor_taxa=0 ):

    con = sql.connect(usuario+".db")
    cursor = con.cursor()

    if tipo_inv == "ACOES":

        query = '''CREATE TABLE IF NOT EXISTS ACOES (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    acao TEXT NOT NULL,
                    tipo_de_evento TEXT NOT NULL,
                    valor NUMERIC NOT NULL,
                    data TEXT NOT NULL,
                    qtd INTEGER,
                    corretagem NUMERIC,
                    IR_previa NUMERIC,
                    Prejuizo_lucro NUMERIC);'''
        cursor.execute(query)
        con.commit()

        query2 = ''' INSERT INTO ACOES (acao, tipo_de_evento, valor, data, qtd, corretagem,
                                          IR_previa, Prejuizo_lucro)
                           VALUES(?,?,?,?,?,?,?,?);        '''
        cursor.execute(query2, (codigo_investimento, tipo, valor, data, qtd, corretagem, ir_prev, prej_lucro))
        con.commit()

    elif tipo_inv == "FII":

        query = '''CREATE TABLE IF NOT EXISTS FII (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    FII TEXT NOT NULL,
                    tipo_de_evento TEXT NOT NULL,
                    valor NUMERIC NOT NULL,
                    data TEXT NOT NULL,
                    qtd INTEGER,
                    corretagem NUMERIC,
                    IR_previa NUMERIC,
                    Prejuizo_lucro NUMERIC);'''
        cursor.execute(query)
        con.commit()

        query2 = ''' INSERT INTO FII (FII, tipo_de_evento, valor, data, qtd, corretagem,
                                          IR_previa, Prejuizo_lucro)
                           VALUES(?,?,?,?,?,?,?,?);        '''
        cursor.execute(query2, (codigo_investimento, tipo, valor, data, qtd, corretagem, ir_prev, prej_lucro))
        con.commit()

    elif tipo_inv == "RENDA_FIXA":

        query = '''CREATE TABLE IF NOT EXISTS RENDA_FIXA (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    tipo_de_evento TEXT NOT NULL,
                    tipo_de_renda_fixa TEXT NOT NULL,
                    tipo_de_taxa TEXT NOT NULL,
                    valor_taxa NUMERIC,
                    valor_compra NUMERIC NOT NULL,
                    data_compra TEXT NOT NULL,
                    data_carencia TEXT NOT NULL,
                    data_vencimento TEXT NOT NULL,
                    qtd NUMERIC,
                    isento_IR TEXT,
                    IR_previa NUMERIC,
                    Prejuizo_lucro NUMERIC);'''
        cursor.execute(query)
        con.commit()

        query2 = ''' INSERT INTO RENDA_FIXA (titulo, tipo_de_evento, tipo_de_renda_fixa, tipo_de_taxa, valor_taxa,
                                             valor_compra, data_compra, data_carencia, data_vencimento, qtd, isento_IR,
                                            IR_previa, Prejuizo_lucro)
                           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?);        '''

        cursor.execute(query2, (codigo_investimento, tipo, tipo_aplicacao, tipo_taxa, valor_taxa, valor, data,
                                data_carencia, data_vencimento, qtd, corretagem, ir_prev, prej_lucro))
        con.commit()
    elif tipo_inv == "DINHEIRO":

        query = '''CREATE TABLE IF NOT EXISTS DINHEIRO (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    data TEXT NOT NULL,
                    valor NUMERIC NOT NULL);'''
        cursor.execute(query)
        con.commit()

        query2 = ''' INSERT INTO DINHEIRO (tipo, data, valor)
                           VALUES(?,?,?);        '''
        cursor.execute(query2, (tipo, data, valor))
        con.commit()

    else:
        print("Erro na função " + function.__name__)

    con.close()
    return


def salva_cdi_txt():
    chdir(path)
    str1 = 'ftp://ftp.cetip.com.br/MediaCDI/'
    str3 = '.txt'
    datas = [(dt.datetime.today() - dt.timedelta(days=dia)) for dia in range(1, 2000)]
    fora_da_lista = []
    with open('cdi.txt', 'w') as cdi:
        cdi.write('Data,Taxa CDI\n')
        for data in datas:
            str2 = dt.datetime.strftime(data, '%Y%m%d')
            str4 = dt.datetime.strftime(data, '%Y-%m-%d')
            link = str1 + str2 + str3
            try:
                f = urlopen(link)
                g = f.read().decode('utf-8').replace('\n', '').replace(' ', '')
                cdi.write(str4 + ',' + g[:-2] + '.' + g[-2:] + '\n')
            except URLError:
                fora_da_lista.append(data)
                cdi.write(str4 + ',0\n')

    return


def salva_cdi_db():
    df = pd.read_csv('cdi.txt', sep=',').sort_index(ascending=False)
    df.set_index(keys='Data', inplace=True)
    c = sql.connect("dados_basicos_pb.db")
    df.to_sql("CDI", c, if_exists="replace")
    c.close()


def atualiza_cdi():

    hoje = dt.datetime.today()

    # BUSCA NO DB A LISTAGEM DO CDI E A ÚLTIMA DATA ATUALIZADA
    c = sql.connect('dados_basicos_pb.db')
    cdi_db = pd.read_sql('SELECT * FROM CDI', c)
    data_cdi_db = list(cdi_db['Data'])[-1]
    data_cdi_db = dt.datetime.strptime(data_cdi_db, '%Y-%m-%d')

    # CALCULA DIFERENÇA EM DIAS ENTRE ÚLTIMA DATA DO DB E HOJE

    diff = hoje - data_cdi_db

    str1 = 'ftp://ftp.cetip.com.br/MediaCDI/'
    str3 = '.txt'

    # CRIA LISTA DE DATAS DOS DIAS ENTRE A ÚLTIMA DATA DO DB E HOJE
    datas = [(dt.datetime.today() - dt.timedelta(days=dia)) for dia in range(1, diff.days)]
    fora_da_lista = []
    data_cdi_web = 0

    # BUSCA NO SITE AS TAXAS CDI E SALVA EM TXT E INFORMA A ÚLTIMA DATA DE ATUALIZAÇÃO
    with open('cdi_atualiza.txt', 'w') as cdi_web:
        cdi_web.write('Data,Taxa CDI\n')
        for data in datas:
            str2 = dt.datetime.strftime(data, '%Y%m%d')
            str4 = dt.datetime.strftime(data, '%Y-%m-%d')
            link = str1 + str2 + str3
            try:
                f = urlopen(link)
                g = f.read().decode('utf-8').replace('\n', '').replace(' ', '')
                cdi_web.write(str4 + ',' + g[:-2] + '.' + g[-2:] + '\n')
                data_cdi_web = data
            except URLError:
                cdi_web.write(str4 + ',0\n')
                fora_da_lista.append(data)

    data_cdi_web = datas[0]

    # CALCULA A DIFERENCA DE MESES ENTRE AS DATAS DO SITE E DO DB
    if data_cdi_db.date() != data_cdi_web.date():
        data_cdi_db1 = list(cdi_db['Data'])[-1]
        data_cdi_db1 = dt.datetime.strptime(data_cdi_db1, '%Y-%m-%d')

        # SALVA NO DB AS LINHAS NECESSÁRIAS PARA ATUALIZAÇÃO DO DB DO CDI
        df = pd.read_csv('cdi_atualiza.txt', sep=',').sort_index(ascending=False)
        df['Data'] = pd.to_datetime(df['Data'].astype(str))
        append_cdi = df[(df['Data'] > data_cdi_db1)]
        append_cdi['Data'] = df['Data'].apply(lambda x: x.strftime('%Y-%m-%d'))
        append_cdi.set_index(keys='Data', inplace=True)
        append_cdi.to_sql("CDI", c, if_exists="append")

        # CRIA COLUNA DO FATOR DIARIO DO CDI
        fator_db = pd.read_sql('SELECT * FROM CDI', c)
        fator_db['Fator'] = ((fator_db['Taxa CDI'] / 100) + 1) ** (1 / 252)
        fator_db.set_index(keys='Data', inplace=True)
        fator_db.to_sql("CDI", c, if_exists="replace")
        c.close()


def BuscaCDI(data):

    c = sql.connect('dados_basicos_pb.db')
    cursor = c.cursor()
    cdi_db = cursor.execute('''SELECT Fator FROM CDI WHERE Data > ?;''',(data,))
    lista = cdi_db.fetchall()
    c.close()
    lista2 = [item[0] for item in lista]

    return lista2


def DiasUteis(data1):

    c = sql.connect('dados_basicos_pb.db')
    cursor = c.cursor()
    dias_nao_uteis = cursor.execute('''select count(*) from CDI where Fator > 1 AND Data > ?;''',(data1,))
    dias_n = dias_nao_uteis.fetchall()
    dias = dias_n[0]
    c.close()

    return dias[0]


def busca_salva_cotacoes(ticker, data_fim):

    if ticker == "":
        pass
    else:
        # CONECTA AO DB DE RENDA VARIAVEL
        c = sql.connect("renda_variavel.db")
        cursor = c.cursor()

        # CRIA TABELA PARA AQUELA ACAO CASO NÃO EXISTA
        query = ''' CREATE TABLE IF NOT EXISTS {} 
                        (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                        date TEXT NOT NULL, close NUMERIC NOT NULL);
                        '''.format(ticker)
        cursor.execute(query)

        # BUSCA A ULTIMA DATA COM INFORACOES PARA AQUELA ACAO
        query2 = ''' SELECT date FROM {} ORDER BY id DESC LIMIT 1'''.format(ticker)

        try:
            data_1 = cursor.execute(query2).fetchone()[0]
            data_1 = str(data_1)[:10]

            data_inicio = dt.datetime.strptime(data_1,"%Y-%m-%d")

        except TypeError as t:
            print("Não foi encontrado registro de " + ticker + " no Banco de Dados. " + str(t))
            data_inicio = dt.datetime(2000,1,1)

        if data_inicio.date() == data_fim.date():
            print(ticker + " já está atualizado no DB.")

        else:
            # BUSCA NO YAHOO FIN AS ULTIMAS INFORMACOES PARA AQUELA ACAO
            df = si.get_data(ticker + ".SA", data_inicio.date(), data_fim.date())

            data_web = df.first_valid_index()

            if data_web == data_inicio.date():
                print(ticker + " não possui cotações após a data " + str(data_web) + " no yahoo_fin.")

                print("Tentando pelo Pandas datareader")

                df = data.get_data_yahoo(ticker + ".SA", start=data_inicio, end=data_fim)

                # FILTRA PARA AS ULTIMAS COTACOES
                df2 = pd.DataFrame(df, columns=["Close"])

                # SALVA NO DB
                df2.to_sql(ticker, c, if_exists="append")

                print(ticker + " foi atualizado no DB.")

            else:
                # FILTRA PARA AS ULTIMAS COTACOES
                df2 = pd.DataFrame(df, columns=["close"])

                # SALVA NO DB
                df2.to_sql(ticker, c, if_exists="append")

                print(ticker + " foi atualizado no DB.")

        c.close()

    return


class Evento:

    def __init__(self,  investimento, tipo, valor, data, qtd=0, corretagem=0, usuario="acao", id=0, tipo_aplicacao="",
                  data_carencia="", data_vencimento="", tipo_taxa="", valor_taxa="" ):

        self.id = id
        self.usuario = usuario
        self.codigo = investimento
        self.tipo_operacao = tipo
        self.valor_aplicado = valor
        self.tipo_aplicacao = tipo_aplicacao
        self.tipo_taxa = tipo_taxa
        self.valor_taxa = valor_taxa

        data  = data.replace("-","/")                                       # Corrige a data se inserida com -
        data = data[0:10]                                                   # Busca somente a data e deixa as horas
        if data[2] == "/":                                                  # Verifica se é dd/mm/aaaa
            data = data[-4:]+data[2:6]+data[0:2]                            # Inverte para aaaa/mm/dd
        self.data_aplicacao = dt.datetime.strptime(data, "%Y/%m/%d")

        if data_carencia == "":
            self.data_carencia = ""
        else:
            data2 = data_carencia.replace("-","/")                                       # Corrige a data se inserida com -
            data2 = data2[0:10]                                                   # Busca somente a data e deixa as horas
            if data2[2] == "/":                                                  # Verifica se é dd/mm/aaaa
                data2 = data2[-4:]+data2[2:6]+data2[0:2]                            # Inverte para aaaa/mm/dd
            self.data_carencia = dt.datetime.strptime(data2, "%Y/%m/%d")

        if data_vencimento == "":
            self.data_vencimento = ""
        else:
            data3 = data_vencimento.replace("-","/")                                       # Corrige a data se inserida com -
            data3 = data3[0:10]                                                   # Busca somente a data e deixa as horas
            if data3[2] == "/":                                                  # Verifica se é dd/mm/aaaa
                data3 = data3[-4:]+data3[2:6]+data3[0:2]                            # Inverte para aaaa/mm/dd
            self.data_vencimento = dt.datetime.strptime(data3, "%Y/%m/%d")

        self.qtd = qtd
        self.corretagem = corretagem
        self.imposto_renda_prev = 0
        self.preju_lucro = 0


class Acao:

    def __init__(self, cod_acao, usuario="acao"):

        # Cria os campos de cada Ação

        self.usuario = usuario
        self.codigo = cod_acao

        self.busca_eventos_DB()                                              # Busca os eventos já registrados no banco de dados
        self.criaEventos()                                          # Gera a lista com os objetos Eventos

        self.preco_medio_sem_div = 0                                # Atribui valores iniciais
        self.qtd_atual = 0
        self.data_media_aquisicao = dt.datetime(1, 1, 1)
        self.valor_investido = 0
        self.rendimento_vendas = 0
        self.soma_dividendo = 0
        self.preco_medio_com_div = 0
        self.valor_compra_total = 0
        self.valor_venda_total = 0
        self.valor_dividendo_total = 0
        self.retorno_total = 0
        self.corretagem_total = 0

        # Loop de cálculo para cada evento da lista de eventos do Banco de Dados

        for evento in self.eventos:

            if evento.tipo_operacao == "Compra":

                if self.preco_medio_sem_div == 0:                       # A cada iteração do loop ele calcula a média
                    self.preco_medio_sem_div = ((evento.valor_aplicado * evento.qtd) + evento.corretagem) / evento.qtd             #  ponderada entre 2 valores
                else:
                    try:
                        self.preco_medio_sem_div = (self.preco_medio_sem_div * self.qtd_atual +
                                                    evento.corretagem + evento.valor_aplicado * evento.qtd) / (self.qtd_atual + evento.qtd)
                    except ZeroDivisionError as z:
                        self.preco_medio_sem_div = 0

                if self.data_media_aquisicao == dt.datetime(1, 1, 1):
                    self.data_media_aquisicao = evento.data_aplicacao

                else:
                    peso = (evento.qtd * evento.valor_aplicado) / (self.valor_investido + (evento.qtd * evento.valor_aplicado))
                                                                                         # A data média ponderada é
                    dif = evento.data_aplicacao - self.data_media_aquisicao                        # calculada com base na qtd de
                    self.data_media_aquisicao = self.data_media_aquisicao + (dif * peso) # ações compradas com relação
                                                                                         # à qtd existente.

                self.qtd_atual += evento.qtd                            # Grandezas que não demandam condições
                self.valor_investido += ((evento.valor_aplicado * evento.qtd) + evento.corretagem)
                self.valor_compra_total += (evento.valor_aplicado * evento.qtd)
                self.corretagem_total += evento.corretagem

            elif evento.tipo_operacao == "Venda":

                self.qtd_atual -= evento.qtd
                self.rendimento_vendas += (
                        ((evento.valor_aplicado * evento.qtd) + evento.corretagem) - (self.preco_medio_sem_div * evento.qtd))
                evento.preju_lucro = (evento.valor_aplicado * evento.qtd) + evento.corretagem - (self.preco_medio_sem_div * evento.qtd)
                evento.imposto_renda_prev = 0.15*evento.preju_lucro

                self.AtualizaEvento(evento)

                if self.qtd_atual == 0:
                    self.data_media_aquisicao = dt.datetime(1, 1, 1)
                    self.preco_medio_sem_div = 0
                    self.valor_investido = 0
                    self.rendimento_vendas = 0
                    self.preco_medio_com_div = 0
                    self.soma_dividendo = 0
                else:
                    self.valor_investido -= (evento.valor_aplicado * evento.qtd) + evento.corretagem

                self.valor_venda_total += (evento.valor_aplicado * evento.qtd)
                self.corretagem_total += evento.corretagem

            elif evento.tipo_operacao == "Rendimento":

                if self.qtd_atual == 0:
                    continue
                else:
                    self.soma_dividendo += evento.valor_aplicado
                    self.preco_medio_com_div = (self.qtd_atual * self.preco_medio_sem_div - self.soma_dividendo)/self.qtd_atual
                self.valor_dividendo_total += evento.valor_aplicado

            else:
                print("Erro! O tipo de evento é {}".format(evento.tipo_operacao))
            try:
                self.retorno_total = (((self.valor_venda_total + self.valor_dividendo_total - self.corretagem_total)/self.valor_compra_total)-1)*100
            except ZeroDivisionError as z:
                print("Erro no calculo do retorno total da classe Acao.  " + str(z))
                self.retorno_total = 0

        # Fim do loop de eventos

        

        if self.soma_dividendo == 0:
            self.preco_medio_com_div = self.preco_medio_sem_div

        # Busca a cotação da ação se a qtd for maior que zero
        if self.qtd_atual > 0:
            try:
                self.cotacao_atual = self.CotacaoAtual()
                self.inflacao_acum = self.CalculaInflacaoAcumulada()
                self.valor_atual = self.qtd_atual*self.cotacao_atual
            except KeyError as e:
                self.cotacao_atual = 0
        else:
            self.cotacao_atual = 0
            self.inflacao_acum = 0


        self.RetornoSemDiv, self.RetornoRealSemDiv, self.RetornoComDiv, self.RetornoRealComDiv = self.CalculaRetornos()

        try:
            self.div_yield = (self.soma_dividendo / self.valor_investido)
            hj = dt.datetime.today()
            self.qtd_meses = ((hj - self.data_media_aquisicao).days)/30
            self.div_yield_mensal = (((1+self.div_yield)**(1/self.qtd_meses))-1)*100
        except ZeroDivisionError as e:
            pass

    def AtualizaEvento(self, evento):

        con = sql.connect(self.usuario+".db")
        cursor = con.cursor()

        cursor.execute('''UPDATE ACOES SET IR_previa= ? , Prejuizo_lucro = ? WHERE id = ?;''', (evento.imposto_renda_prev,
                                                                                                 evento.preju_lucro,
                                                                                                 evento.id,))
        con.commit()
        con.close()

        return

    def CalculaInflacaoAcumulada(self):

        lista_ipca = busca_IPCA_m()

        data_media_ipca = dt.datetime.replace(self.data_media_aquisicao,day=1,hour=0,minute=0,second=0,microsecond=0)
        ipca_acum = 1

        for i, data in enumerate(lista_ipca.data):
            if dt.datetime.strptime(data,"%d/%m/%Y") >= data_media_ipca:
                ipca_acum *= (1+(float(lista_ipca.valor[i].replace(',','.'))/100))

        ipca_acum = (ipca_acum - 1)*100

        return ipca_acum

    def busca_eventos_DB(self):

        con = sql.connect(self.usuario+".db")
        cursor = con.cursor()

        self.lista_de_eventos = cursor.execute('''  SELECT * FROM ACOES WHERE acao= ? ORDER BY data ASC''', (self.codigo,))
        con.commit()

        self.lista_de_eventos = cursor.fetchall()

        con.close()
        return

    def CotacaoAtual(self):

        papel = self.codigo.ljust(12)
        ano_atual_cot = str(dt.datetime.today().year)
        con = sql.connect(os.getcwd() + '\\base\\' + 'db_hist_' + ano_atual_cot + '.db')
        fech_ano = pd.read_sql_query("SELECT PREULT FROM hist_bovespa WHERE CODNEG = '" + papel + "'", con)
        CotacaoAtual = list(fech_ano['PREULT'])[-1]
        con.commit()
        con.close()
        # c = sql.connect("renda_variavel.db")
        # cursor = c.cursor()
        # query = '''SELECT close FROM {} ORDER BY id DESC LIMIT 1'''.format(self.codigo)
        # query1 = '''SELECT date FROM {} ORDER BY id DESC LIMIT 1'''.format(self.codigo)
        # hj = dt.datetime.today()
        #
        # try:
        #     self.data_db = cursor.execute(query1).fetchone()[0]
        #     self.data_db = str(self.data_db)[:10]
        #     self.data_db = dt.datetime.strptime(self.data_db, "%Y-%m-%d")
        #
        #     if self.data_db < hj - dt.timedelta(days=3):
        #
        #         CotacaoAtual = si.get_live_price(self.codigo + ".SA")
        #
        #     else:
        #         CotacaoAtual = cursor.execute(query).fetchone()[0]
        #
        # except:
        #     try:
        #         CotacaoAtual = si.get_live_price(self.codigo + ".SA")
        #     except:
        #         CotacaoAtual = cursor.execute(query).fetchone()[0]
        #
        # c.close()

        return CotacaoAtual

    def CalculaRetornos(self):

        if self.preco_medio_sem_div == 0:
            VariacaoSemDiv , VariacaoRealSemDiv = 0, 0
        else:
            VariacaoSemDiv = ((self.cotacao_atual - self.preco_medio_sem_div) / self.preco_medio_sem_div) * 100
            VariacaoRealSemDiv = ((((VariacaoSemDiv / 100) + 1) / ((self.inflacao_acum / 100) + 1)) - 1) * 100

        if self.preco_medio_com_div == 0:
            VariacaoComDiv, VariacaoRealComDiv = VariacaoSemDiv, VariacaoRealSemDiv
        else:
            VariacaoComDiv = ((self.cotacao_atual - self.preco_medio_com_div)/self.preco_medio_com_div)*100
            VariacaoRealComDiv = ((((VariacaoComDiv/100)+1)/((self.inflacao_acum/100)+1))-1)*100

        return VariacaoSemDiv, VariacaoRealSemDiv, VariacaoComDiv, VariacaoRealComDiv

    def criaEventos(self):

        self.eventos = [Evento(linha[1], linha[2], linha[3], linha[4], linha[5], linha[6], linha[7], linha[0]) for linha in
                   self.lista_de_eventos]

        return

    def ApagaEvento(self, id):

        con = sql.connect(self.usuario+".db")
        cursor = con.cursor()

        cursor.execute('''  DELETE FROM ACOES WHERE id= ? ''',(id,))
        con.commit()
        con.close()
        return


class FII:

    def __init__(self, cod_fii, usuario="acao"):

        # Cria os campos de cada FII

        self.usuario = usuario
        self.codigo = cod_fii

        self.busca_eventos_DB()                                     # Busca os eventos já registrados no banco de dados
        self.criaEventos()                                          # Gera a lista com os objetos Eventos

        self.preco_medio_sem_div = 0                                # Atribui valores iniciais
        self.qtd_atual = 0
        self.data_media_aquisicao = dt.datetime(1, 1, 1)
        self.valor_investido = 0
        self.rendimento_vendas = 0
        self.soma_dividendo = 0
        self.preco_medio_com_div = 0
        self.valor_compra_total = 0
        self.valor_venda_total = 0
        self.valor_dividendo_total = 0
        self.retorno_total = 0
        self.corretagem_total = 0

        # Loop de cálculo para cada evento da lista de eventos do Banco de Dados

        for evento in self.eventos:

            if evento.tipo_operacao == "Compra":

                if self.preco_medio_sem_div == 0:
                    self.preco_medio_sem_div = ((evento.valor_aplicado * evento.qtd) + evento.corretagem) / evento.qtd
                else:
                    self.preco_medio_sem_div = (self.preco_medio_sem_div * self.qtd_atual +
                                                evento.corretagem + evento.valor_aplicado * evento.qtd) / (
                                                       self.qtd_atual + evento.qtd)
                if self.data_media_aquisicao == dt.datetime(1, 1, 1):
                    self.data_media_aquisicao = evento.data_aplicacao

                else:
                    peso = (evento.qtd * evento.valor_aplicado) / (self.valor_investido + (evento.qtd * evento.valor_aplicado))
                    # A data média ponderada é
                    dif = evento.data_aplicacao - self.data_media_aquisicao  # calculada com base na qtd de
                    self.data_media_aquisicao = self.data_media_aquisicao + (dif * peso)  # ações compradas com relação
                    # à qtd existente.

                self.qtd_atual += evento.qtd  # Grandezas que não demandam condições
                self.valor_investido += ((evento.valor_aplicado * evento.qtd) + evento.corretagem)
                self.valor_compra_total += (evento.valor_aplicado * evento.qtd)
                self.corretagem_total += evento.corretagem

            elif evento.tipo_operacao == "Venda":

                self.qtd_atual -= evento.qtd
                self.rendimento_vendas += (
                        ((evento.valor_aplicado * evento.qtd) + evento.corretagem) - (self.preco_medio_sem_div * evento.qtd))
                evento.preju_lucro = (evento.valor_aplicado * evento.qtd) + evento.corretagem - (
                        self.preco_medio_sem_div * evento.qtd)
                evento.imposto_renda_prev = 0.15 * evento.preju_lucro

                self.AtualizaEvento(evento)

                if self.qtd_atual == 0:
                    self.data_media_aquisicao = dt.datetime(1, 1, 1)
                    self.preco_medio_sem_div = 0
                    self.valor_investido = 0
                    self.rendimento_vendas = 0
                    self.preco_medio_com_div = 0
                    self.soma_dividendo = 0
                else:
                    self.valor_investido -= (evento.valor_aplicado * evento.qtd) + evento.corretagem

                self.valor_venda_total += (evento.valor_aplicado * evento.qtd)
                self.corretagem_total += evento.corretagem

            elif evento.tipo_operacao == "Rendimento":

                if self.qtd_atual == 0:
                    continue
                else:
                    self.soma_dividendo += evento.valor_aplicado
                    self.preco_medio_com_div = (
                                                       self.qtd_atual * self.preco_medio_sem_div - self.soma_dividendo) / self.qtd_atual
                self.valor_dividendo_total += evento.valor_aplicado

            else:
                print("Erro! O tipo de evento é {}".format(evento.tipo_operacao))

            self.retorno_total = (((self.valor_venda_total + self.valor_dividendo_total - self.corretagem_total) / self.valor_compra_total) - 1) * 100

        # Fim do loop de eventos

        

        if self.soma_dividendo == 0:
            self.preco_medio_com_div = self.preco_medio_sem_div

        # Busca a cotação da ação se a qtd for maior que zero
        if self.qtd_atual > 0:
            try:
                self.cotacao_atual = self.CotacaoAtual()
                self.inflacao_acum = self.CalculaInflacaoAcumulada()
                self.valor_atual = self.qtd_atual*self.cotacao_atual

            except KeyError as e:
                self.cotacao_atual = 0
        else:
            self.cotacao_atual = 0
            self.inflacao_acum = 0

            try:
                self.retorno_total = (((self.valor_venda_total + self.valor_dividendo_total - self.corretagem_total)/self.valor_compra_total)-1)*100
            except ZeroDivisionError as e:
                pass

        self.RetornoSemDiv, self.RetornoRealSemDiv, self.RetornoComDiv, self.RetornoRealComDiv = self.CalculaRetornos()

        try:
            self.div_yield = (self.soma_dividendo / self.valor_investido)
            hj = dt.datetime.today()
            self.qtd_meses = ((hj - self.data_media_aquisicao).days)/30
            self.div_yield_mensal = (((1+self.div_yield)**(1/self.qtd_meses))-1)*100
        except ZeroDivisionError as e:
            pass

    def __str__(self):
        return "{}".format(self.codigo)

    def __repr__(self):
        return "{}__".format(self.codigo)

    def AtualizaEvento(self, evento):

        con = sql.connect(self.usuario+".db")
        cursor = con.cursor()

        cursor.execute('''UPDATE FII SET IR_previa= ? , Prejuizo_lucro = ? WHERE id = ?;''', (evento.imposto_renda_prev,
                                                                                                 evento.preju_lucro,
                                                                                                 evento.id,))
        con.commit()
        con.close()

        return

    def CalculaInflacaoAcumulada(self):

        lista_ipca = busca_IPCA_m()

        data_media_ipca = dt.datetime.replace(self.data_media_aquisicao,day=1,hour=0,minute=0,second=0,microsecond=0)
        ipca_acum = 1

        for i, data in enumerate(lista_ipca.data):
            if dt.datetime.strptime(data,"%d/%m/%Y") >= data_media_ipca:
                ipca_acum *= (1+(float(lista_ipca.valor[i].replace(',','.'))/100))

        ipca_acum = (ipca_acum - 1)*100

        return ipca_acum

    def busca_eventos_DB(self):

        con = sql.connect(self.usuario+".db")
        cursor = con.cursor()
        try:
            self.lista_de_eventos = cursor.execute('''  SELECT * FROM FII WHERE FII= ? ORDER BY data ASC''', (self.codigo,))
            con.commit()
            self.lista_de_eventos = cursor.fetchall()
        except sql.OperationalError as e:
            self.lista_de_eventos = []
        con.close()
        return

    def CotacaoAtual(self):

        papel = self.codigo.ljust(12)
        ano_atual_cot = str(dt.datetime.today().year)
        con = sql.connect(os.getcwd() + '\\base\\' + 'db_hist_' + ano_atual_cot + '.db')
        fech_ano = pd.read_sql_query("SELECT PREULT FROM hist_bovespa WHERE CODNEG = '" + papel + "'", con)
        CotacaoAtual = list(fech_ano['PREULT'])[-1]
        con.commit()
        con.close()

        # c = sql.connect("renda_variavel.db")
        # cursor = c.cursor()
        # query = '''SELECT close FROM {} ORDER BY id DESC LIMIT 1'''.format(self.codigo)
        #
        # try:
        #     CotacaoAtual = cursor.execute(query).fetchone()[0]
        # except:
        #     CotacaoAtual = si.get_live_price(self.codigo + ".SA")
        #
        # c.close()

        return CotacaoAtual

    def CalculaRetornos(self):

        if self.preco_medio_sem_div == 0:
            VariacaoSemDiv , VariacaoRealSemDiv = 0, 0
        else:
            VariacaoSemDiv = ((self.cotacao_atual - self.preco_medio_sem_div) / self.preco_medio_sem_div) * 100
            VariacaoRealSemDiv = ((((VariacaoSemDiv / 100) + 1) / ((self.inflacao_acum / 100) + 1)) - 1) * 100

        if self.preco_medio_com_div == 0:
            VariacaoComDiv, VariacaoRealComDiv = VariacaoSemDiv, VariacaoRealSemDiv
        else:
            VariacaoComDiv = ((self.cotacao_atual - self.preco_medio_com_div)/self.preco_medio_com_div)*100
            VariacaoRealComDiv = ((((VariacaoComDiv/100)+1)/((self.inflacao_acum/100)+1))-1)*100

        return VariacaoSemDiv, VariacaoRealSemDiv, VariacaoComDiv, VariacaoRealComDiv

    def criaEventos(self):

        self.eventos = [Evento(linha[1], linha[2], linha[3], linha[4], linha[5], linha[6], linha[7], linha[0]) for linha in
                   self.lista_de_eventos]
        return

    def ApagaEvento(self, id):

        con = sql.connect(self.usuario+".db")
        cursor = con.cursor()

        cursor.execute('''  DELETE FROM FII WHERE id= ? ''',(id,))
        con.commit()
        con.close()
        return


class RendaFixa:

    def __init__(self, codigo, usuario="acao"):

        self.codigo = codigo
        self.usuario = usuario

        self.busca_eventos_DB()  # Busca os eventos já registrados no banco de dados
        self.criaEventos()  # Gera a lista com os objetos Eventos

        # Loop de eventos

        self.valor_investido = 0
        self.valor_aplicado = 0
        self.valor_resgatado = 0
        self.rendimento = 0
        self.ipca_acumulado = 0
        self.valor_atual = 0
        self.liquidez = 0
        self.ir = 0

        for evento in self.eventos:
            if evento.tipo_operacao== "Compra":
                self.valor_investido += evento.valor_aplicado
                self.ipca_acumulado = self.CalculaInflacaoAcumulada(evento.data_aplicacao)
                self.rendimento = self.CalculaRendimento(evento)
                self.data_compra = evento.data_aplicacao
                self.data_carencia = evento.data_carencia
                self.data_vencimento = evento.data_vencimento
                self.valor_aplicado = self.valor_investido

            elif evento.tipo_operacao == "Resgate":
                self.valor_investido -= evento.valor_aplicado
                self.valor_resgatado += evento.valor_aplicado


            if evento.corretagem == "Sim":
                self.ir = 0
            else:
                self.ir = self.CalculaIR()


        self.valor_atual_bruto = self.rendimento + self.valor_investido
        self.valor_atual_liq = self.valor_atual_bruto - self.ir
        self.valor_final_liq = self.valor_resgatado - self.ir
        try:
            self.taxa_atual_liq = (self.valor_atual_liq / self.valor_investido -1)*100
        except ZeroDivisionError as z:
            self.taxa_atual_liq = 0
            print("Valor investido em Renda Fixa é igual a 0. " + str(z))
        try:
            self.taxa_final_liq = (self.valor_final_liq / self.valor_aplicado -1)*100
        except ZeroDivisionError as z:
            self.taxa_final_liq = 0
            print("Valor aplicado em Renda Fixa é igual a 0. " + str(z))

    def CalculaRendimento(self, evento):

        rendimento = 0
        hoje = dt.datetime.today()
        data_aplicacao = evento.data_aplicacao
        dif_datas = hoje - data_aplicacao
        dias = dif_datas.days
        dias_uteis = DiasUteis(data_aplicacao)

        if evento.tipo_taxa == "Préfixado":
            taxa_aa = evento.valor_taxa
            taxa_ad = ((taxa_aa)+1)**(1/252)
            TaxaFixaAcumulada = (taxa_ad**dias_uteis)-1
            rendimento = evento.valor_aplicado*TaxaFixaAcumulada

        if evento.tipo_taxa == "% CDI":
            cdi = BuscaCDI(data_aplicacao)
            try:
                cdi_acum = reduce(lambda x,y: x*y,cdi) - 1
            except:
                cdi_acum = 0
            taxa_rend = cdi_acum * evento.valor_taxa
            rendimento = evento.valor_aplicado*taxa_rend

        if evento.tipo_taxa == "IPCA +":
            IPCA_acum = self.CalculaInflacaoAcumulada(data_aplicacao)/100
            taxa_aa = evento.valor_taxa
            taxa_ad = ((taxa_aa)+1)**(1/360)
            TaxaFixaAcumulada = (taxa_ad**dias)-1
            taxa_rend = IPCA_acum + TaxaFixaAcumulada
            rendimento = evento.valor_aplicado*taxa_rend
            
        if evento.tipo_taxa =="CDI +":
            cdi = BuscaCDI(data_aplicacao)
            cdi_acum = reduce(lambda x,y: x*y,cdi) - 1
            taxa_aa = evento.valor_taxa
            taxa_ad = ((taxa_aa)+1)**(1/360)
            TaxaFixaAcumulada = (taxa_ad**dias)-1
            taxa_rend = cdi_acum + TaxaFixaAcumulada
            rendimento = evento.valor_aplicado*taxa_rend
        
        #if evento.tipo =="SELIC": #PRA ESSE TEM QUE ACESSAR E BAIXAR NO DADOS_BASICOS COM A SELIC

        return rendimento

    def CalculaIR(self):

        hoje = dt.datetime.today()
        dif_datas = hoje - self.data_compra
        dias = dif_datas.days
        taxa_ir = 0

        if dias < 181:
            taxa_ir = 0.225
        elif dias < 361:
            taxa_ir = 0.2
        elif dias < 721:
            taxa_ir = 0.175
        elif dias >= 721:
            taxa_ir = 0.15
        else:
            print("Erro no cálculo da taxa de imposto de renda para a Renda Fixa.")

        ir = taxa_ir * self.rendimento

        return ir

    def busca_eventos_DB(self):

        con = sql.connect(self.usuario+".db")
        cursor = con.cursor()
        try:
            self.lista_de_eventos = cursor.execute('''  SELECT * FROM RENDA_FIXA WHERE titulo=? ORDER BY data_compra ASC''',
                                                (self.codigo,))
            con.commit()
            self.lista_de_eventos = cursor.fetchall()
        except sql.OperationalError as e:
            self.lista_de_eventos = []
        con.close()
        return

    def criaEventos(self):

        self.eventos = [Evento(linha[1], linha[2], linha[6], linha[7], linha[10], linha[11], linha[0], linha[0],
                               linha[3], linha[8], linha[9], linha[4], linha[5]) for linha in self.lista_de_eventos]

        return

    def ApagaEvento(self, id):

        con = sql.connect(self.usuario+".db")
        cursor = con.cursor()

        cursor.execute('''  DELETE FROM RENDA_FIXA WHERE id= ? ''',(id,))
        con.commit()
        con.close()
        return

    # VERIFICAR SE ESTA FUNCAO AINDA É NECESSÁRIA
    def AtualizaEvento(self, evento):

        con = sql.connect(self.usuario+".db")
        cursor = con.cursor()

        cursor.execute('''UPDATE RENDA_FIXA SET IR_previa= ? , Prejuizo_lucro = ? WHERE id = ?;''', (evento.imposto_renda_prev,
                                                                                                 evento.preju_lucro,
                                                                                                 evento.id,))
        con.commit()
        con.close()

        return

    def CalculaInflacaoAcumulada(self,data):

        lista_ipca = busca_IPCA_m()

        data_media_ipca = dt.datetime.replace(data,day=1,hour=0,minute=0,second=0,microsecond=0)
        ipca_acum = 1

        for i, data in enumerate(lista_ipca.data):
            if dt.datetime.strptime(data,"%d/%m/%Y") >= data_media_ipca:
                ipca_acum *= (1+(float(lista_ipca.valor[i].replace(',','.'))/100))

        ipca_acum = (ipca_acum - 1)*100

        return ipca_acum


class Dinheiro:

    def __init__(self, usuario="acao"):

        self.usuario = usuario

        self.busca_eventos_DB()  # Busca os eventos já registrados no banco de dados

        self.criaEventos()  # Gera a lista com os objetos Eventos

        self.depositos = 0
        self.resgates = 0
        self.evento_dinheiro_corr = 0
        self.soma_dinheiro_corr_ipca = 0
        self.data_media_dinheiro = dt.datetime(1, 1, 1)

        for evento in self.eventos:

            if evento.tipo_operacao == "Deposito":
                self.depositos += evento.valor_aplicado
                self.ipca_acum_evento = self.CalculaInflacaoAcumulada(evento.data_aplicacao)
                self.evento_dinheiro_corr = evento.valor_aplicado*(1+self.ipca_acum_evento/100)
                self.soma_dinheiro_corr_ipca += self.evento_dinheiro_corr

            elif evento.tipo_operacao == "Resgate":
                self.resgates += evento.valor_aplicado
                self.ipca_acum_evento = self.CalculaInflacaoAcumulada(evento.data_aplicacao)
                self.evento_dinheiro_corr = evento.valor_aplicado * (1 + self.ipca_acum_evento / 100) * (-1)
                self.soma_dinheiro_corr_ipca += self.evento_dinheiro_corr

        self.soma_dinheiro_aplicado = self.depositos - self.resgates
        try:
            self.taxa_ipca_acum_dinheiro = (self.soma_dinheiro_corr_ipca / self.soma_dinheiro_aplicado -1)*100
        except ZeroDivisionError as z:
            print("Erro de divisão por zero no cálculo do IPCA acumulado para o objeto Dinheiro.")
            self.taxa_ipca_acum_dinheiro = 0

        self.soma_eventos_anteriores = 0

        for evento in self.eventos:

            if evento.tipo_operacao == "Deposito":

                if self.data_media_dinheiro == dt.datetime(1, 1, 1):
                    self.data_media_dinheiro = evento.data_aplicacao
                else:
                    peso = (evento.valor_aplicado) / (self.soma_eventos_anteriores + (evento.valor_aplicado))
                    dif = evento.data_aplicacao - self.data_media_dinheiro
                    self.data_media_dinheiro = self.data_media_dinheiro + (dif * peso)
                    self.soma_eventos_anteriores += evento.valor_aplicado

            if evento.tipo_operacao == "Resgate":

                peso = (evento.valor_aplicado) / (self.soma_eventos_anteriores + (evento.valor_aplicado))
                dif = evento.data_aplicacao - self.data_media_dinheiro
                self.data_media_dinheiro = self.data_media_dinheiro - (dif * peso)
                self.soma_eventos_anteriores -= evento.valor_aplicado

    def CalculaInflacaoAcumulada(self,data):

        lista_ipca = busca_IPCA_m()

        data_media_ipca = dt.datetime.replace(data,day=1,hour=0,minute=0,second=0,microsecond=0)
        ipca_acum = 1

        for i, data in enumerate(lista_ipca.data):
            if dt.datetime.strptime(data,"%d/%m/%Y") >= data_media_ipca:
                ipca_acum *= (1+(float(lista_ipca.valor[i].replace(',','.'))/100))

        ipca_acum = (ipca_acum - 1)*100

        return ipca_acum

    def busca_eventos_DB(self):

        con = sql.connect(self.usuario+".db")
        cursor = con.cursor()
        try:
            self.lista_de_eventos = cursor.execute('''  SELECT * FROM DINHEIRO ORDER BY data ASC''')
            con.commit()
            self.lista_de_eventos = cursor.fetchall()
            
        except sql.OperationalError as e:
            self.lista_de_eventos = []
        con.close()
        return

    def criaEventos(self):

        self.eventos = [Evento("", linha[1], linha[3], linha[2], "", "", "", linha[0]) for linha in self.lista_de_eventos]

        return

    def ApagaEvento(self, id):

        con = sql.connect(self.usuario+".db")
        cursor = con.cursor()

        cursor.execute('''  DELETE FROM DINHEIRO WHERE id= ? ''',(id,))
        con.commit()
        con.close()
        return

    def AtualizaEvento(self, evento):

        con = sql.connect(self.usuario+".db")
        cursor = con.cursor()

        cursor.execute('''UPDATE DINHEIRO SET data= ? , valor = ? WHERE id = ?;''', (evento.data, evento.valor, evento.id,))
        con.commit()
        con.close()

        return


class Carteira:

    def __init__(self, usuario):

        self.usuario = usuario
        self.lista_acoes, self.lista_fii = buscaRendaVar(usuario)
        self.lista_renda_fixa = buscaRendaFixa(usuario)
        self.criaAcoes()
        self.criaFII()
        self.criaRF()
        self.criarDinheiro()
        return

    def criaAcoes(self):

        self.acoes = [Acao(acao,self.usuario) for acao in self.lista_acoes]
        return

    def criaFII(self):
        self.fii = [FII(fii,self.usuario) for fii in self.lista_fii]
        return

    def criaRF(self):
        self.rf = [RendaFixa(renda_fixa,self.usuario) for renda_fixa in self.lista_renda_fixa]

    def criarDinheiro(self):
        self.dinheiro = Dinheiro(self.usuario)


class Resumao:

    def __init__(self, usuario,saldo,proventos,porc_acoes,porc_fiis,porc_rf):

        self.saldo = saldo
        self.proventos = proventos
        self.porc_acoes = porc_acoes
        self.porc_fiis = porc_fiis
        self.porc_rf = porc_rf
        self.total_carteiras(usuario,saldo,proventos,porc_acoes,porc_fiis,porc_rf)

        return

    def total_carteiras(self, usuario,saldo,proventos,porc_acoes,porc_fiis,porc_rf):

        hj = dt.datetime.today()

        self.ir = Calc_ir(usuario)

        self.saldo = saldo
        self.proventos = proventos
        self.porc_acoes = porc_acoes
        self.porc_fiis = porc_fiis
        self.porc_rf = porc_rf

        self.carteira = Carteira(usuario)
        self.acoes = self.carteira.acoes
        self.fii = self.carteira.fii
        self.rf = self.carteira.rf
        self.dinheiro = self.carteira.dinheiro

        self.ir = Calc_ir(usuario)

        self.dinheiro_aplic = self.dinheiro.soma_dinheiro_aplicado
        self.taxa_inflacao_dinheiro = self.dinheiro.taxa_ipca_acum_dinheiro
        self.dinheiro_corr = self.dinheiro.soma_dinheiro_corr_ipca

        self.custo_total_acoes = 0
        self.valor_total_acoes = 0
        self.nr_acoes = 0
        for acao in self.acoes:

            if acao.qtd_atual > 0:
                self.nr_acoes += 1
                self.custo_total_acoes += acao.valor_investido
                self.valor_total_acoes += acao.valor_atual

        self.taxa_ret_acoes = (self.valor_total_acoes / self.custo_total_acoes -1)*100
        self.meta_ind_acoes = self.valor_total_acoes / self.nr_acoes

        self.custo_total_fiis = 0
        self.valor_total_fiis = 0
        self.nr_fiis = 0
        for fii in self.fii:

            if fii.qtd_atual > 0:
                self.nr_fiis += 1
                self.custo_total_fiis += fii.valor_investido
                self.valor_total_fiis += fii.valor_atual

        self.taxa_ret_fiis = (self.valor_total_fiis / self.custo_total_fiis - 1) * 100
        self.meta_ind_fiis = self.valor_total_fiis / self.nr_fiis

        self.custo_total_rfs = 0
        self.valor_total_rfs = 0
        self.liq_imediata = 0
        self.liq_30 = 0
        self.liq_60 = 0
        self.liq_90 = 0
        self.liq_180 = 0
        self.liq_360 = 0
        self.liq_maior_360 = 0

        for rf in self.rf:

            if rf.valor_investido > 0:

                self.custo_total_rfs += rf.valor_investido
                self.valor_total_rfs += rf.valor_atual_bruto

                if rf.data_carencia <= hj:
                    self.liq_imediata += rf.valor_atual_bruto
                elif hj < rf.data_carencia <= hj + dt.timedelta(days=30):
                    self.liq_30 += rf.valor_atual_bruto
                elif hj + dt.timedelta(days=30) < rf.data_carencia <= hj + dt.timedelta(days=60):
                    self.liq_60 += rf.valor_atual_bruto
                elif hj + dt.timedelta(days=60) < rf.data_carencia <= hj + dt.timedelta(days=90):
                    self.liq_90 += rf.valor_atual_bruto
                elif hj + dt.timedelta(days=90) < rf.data_carencia <= hj + dt.timedelta(days=180):
                    self.liq_180 += rf.valor_atual_bruto
                elif hj + dt.timedelta(days=180) < rf.data_carencia <= hj + dt.timedelta(days=360):
                    self.liq_360 += rf.valor_atual_bruto
                elif rf.data_carencia > hj + dt.timedelta(days=360):
                    self.liq_maior_360 += rf.valor_atual_bruto

        self.taxa_ret_rf = (self.valor_total_rfs / self.custo_total_rfs -1)*100

        self.total_cart = self.saldo + self.proventos + self.valor_total_acoes + self.valor_total_fiis + self.valor_total_rfs
        self.taxa_ret_carteira = (self.total_cart / self.dinheiro_aplic - 1) * 100
        self.ret_real_carteira = (self.total_cart / self.dinheiro_corr - 1) * 100

        try:
            self.yield_carteira = ((self.total_cart - self.dinheiro_aplic) / self.dinheiro_aplic)
            self.qtd_meses = ((hj - self.dinheiro.data_media_dinheiro).days)/30
            self.ret_mensal_carteira = (((1+self.yield_carteira)**(1/self.qtd_meses))-1)*100
            self.ret_anual_carteira = (((1+(self.ret_mensal_carteira/100))**12)-1)*100

        except ZeroDivisionError as e:
            pass

        self.total_cart_liq = self.total_cart - self.ir.soma_ir_total_carteira
        self.taxa_ret_cart_liq = (self.total_cart_liq / self.dinheiro_aplic - 1) * 100
        self.ret_real_cart_liq = (self.total_cart_liq / self.dinheiro_corr - 1) * 100

        try:
            self.yield_cart_liq = ((self.total_cart_liq - self.dinheiro_aplic) / self.dinheiro_aplic)
            self.ret_mensal_cart_liq = (((1+self.yield_cart_liq)**(1/self.qtd_meses))-1)*100
            self.ret_anual_cart_liq = (((1+(self.ret_mensal_cart_liq/100))**12)-1)*100

        except ZeroDivisionError as e:
            pass

        self.meta_acoes = self.porc_acoes * self.total_cart
        self.meta_fiis = self.porc_fiis * self.total_cart
        self.meta_rf = self.porc_rf * self.total_cart
        self.meta_ind_acoes = self.meta_acoes / self.nr_acoes
        self.meta_ind_fiis = self.meta_fiis / self.nr_fiis

        self.desvio_acoes = self.valor_total_acoes - self.meta_acoes
        self.desvio_fiis = self.valor_total_fiis - self.meta_fiis
        self.desvio_rf = self.valor_total_rfs - self.meta_rf

        self.desvio_ind_acoes = []
        self.desvio_ind_fiis = []
        self.lista_acoes = []
        self.lista_fiis = []

        for acao in self.acoes:

            if acao.qtd_atual >0:

                self.lista_acoes.append(acao.codigo)

                self.desvio_ind_acoes.append(acao.valor_atual - self.meta_ind_acoes)

        self.desvio_ind_acoes = ['$ {:,}'.format(round(desvio, 2)) for desvio in self.desvio_ind_acoes]

        for fii in self.fii:

            if fii.qtd_atual > 0:

                self.lista_fiis.append(fii.codigo)

                self.desvio_ind_fiis.append(fii.valor_atual - self.meta_ind_fiis)

        self.desvio_ind_fiis = ['$ {:,}'.format(round(desvio, 2)) for desvio in self.desvio_ind_fiis]

        self.porc_liq_imediata = (self.liq_imediata / self.total_cart)*100
        self.porc_liq_30 = (self.liq_30 / self.total_cart) * 100
        self.porc_liq_60 = (self.liq_60 / self.total_cart) * 100
        self.porc_liq_90 = (self.liq_90 / self.total_cart) * 100
        self.porc_liq_180 = (self.liq_180 / self.total_cart) * 100
        self.porc_liq_360 = (self.liq_360 / self.total_cart) * 100
        self.porc_liq_maior_360 = (self.liq_maior_360 / self.total_cart) * 100

        return

class Calc_ir:

    def __init__(self, usuario):
        self.usuario = usuario

        lista_vendas, lista_res_mes_acoes, lista_preju_acoes, lista_ir_acoes, soma_ir_total_acoes = self.Calc_ir_acoes(usuario)
        lista_res_mes_fiis, lista_preju_fiis, lista_ir_fiis, soma_ir_total_fiis = self.Calc_ir_fiis(usuario)
        ir_rf_total = self.Calc_ir_rfs(usuario)

        lista_ir_total = [x + y for x, y in
                               zip_longest(reversed(lista_ir_acoes), reversed(lista_ir_fiis), fillvalue=0)][
                              ::-1]

        nr_linhas = 12 + dt.datetime.today().month

        self.lista_vendas = lista_vendas[-nr_linhas:]
        self.lista_res_mes_acoes = lista_res_mes_acoes[-nr_linhas:]
        self.lista_preju_acoes = lista_preju_acoes[-nr_linhas:]
        self.lista_ir_acoes = lista_ir_acoes[-nr_linhas:]

        self.lista_res_mes_fiis = lista_res_mes_fiis[-nr_linhas:]
        self.lista_preju_fiis = lista_preju_fiis[-nr_linhas:]
        self.lista_ir_fiis = lista_ir_fiis[-nr_linhas:]

        self.lista_ir_total = lista_ir_total[-nr_linhas:]

        self.soma_ir_total_acoes = soma_ir_total_acoes
        self.soma_ir_total_fiis = soma_ir_total_fiis
        self.soma_ir_total_rfs = ir_rf_total
        self.soma_ir_total_carteira = soma_ir_total_fiis + soma_ir_total_acoes + ir_rf_total
        return

    def Calc_ir_acoes(self,usuario):

        hj = dt.datetime.today()

        con = sql.connect(usuario + ".db")
        self.venda_acoes = pd.read_sql('''  SELECT * FROM ACOES WHERE TIPO_DE_EVENTO="Venda" ORDER BY data ASC''',con)
        self.venda_acoes["Valor em Real"]=self.venda_acoes["valor"]*self.venda_acoes["qtd"]

        self.venda_acoes["data"] = pd.to_datetime(self.venda_acoes["data"])
        self.d1 = self.venda_acoes.iloc[0,4]

        self.nr_meses = dif_mes(hj, self.d1)+1

        self.datas = [self.d1]
        lista_vendas = []
        self.preju_acum = 0
        lista_preju = []
        lista_res_mes = []
        lista_ir_acoes = []

        for i in range(self.nr_meses):
            self.mes_atual = self.datas[-1]
            self.proximo_mes = (self.mes_atual+dt.timedelta(days=31)).replace(day=1,hour=0,minute=0,second=0)
            self.datas.append(self.proximo_mes)

            self.venda_acoes_filt = self.venda_acoes[(self.venda_acoes["data"] >= self.mes_atual) & (self.venda_acoes["data"] < self.proximo_mes)]

            if not self.venda_acoes_filt.empty:
                self.soma_vendas = self.venda_acoes_filt["Valor em Real"].sum()
                lista_vendas.append(self.soma_vendas)
            else:
                self.soma_vendas = 0
                lista_vendas.append(self.soma_vendas)

            self.res_mes = self.venda_acoes_filt["Prejuizo_lucro"].sum()
            lista_res_mes.append(self.res_mes)

            if self.preju_acum >= 0:
                lista_preju.append(self.preju_acum)
                if self.res_mes >= 0:
                    self.preju_acum = 0
                else:
                    self.preju_acum = self.res_mes
            else:
                lista_preju.append(self.preju_acum)
                if self.res_mes >= 0:
                    self.saldo = self.res_mes + self.preju_acum
                    if self.saldo >= 0:
                        self.preju_acum = 0
                    else:
                        self.preju_acum = self.saldo
                else:
                    self.preju_acum = self.res_mes + self.preju_acum

            if self.soma_vendas > 0:
                if self.soma_vendas < 20000:
                    self.ir_devido_acoes = 0
                else:
                    self.res_total = self.res_mes + lista_preju[i]
                    if self.res_total >= 0:
                        self.ir_devido_acoes = self.res_total*0.15
                    else:
                        self.ir_devido_acoes = 0
            else:
                self.ir_devido_acoes = 0

            lista_ir_acoes.append(self.ir_devido_acoes)

        soma_ir_total_acoes = sum(lista_ir_acoes)

        if len(lista_res_mes) < 24:
            n = 24 - len(lista_res_mes)
            self.lista_zeros = [0]*n
            lista_vendas = self.lista_zeros + lista_vendas
            lista_res_mes = self.lista_zeros + lista_res_mes
            lista_preju = self.lista_zeros + lista_preju
            lista_ir_acoes = self.lista_zeros + lista_ir_acoes

        con.commit()
        con.close()

        return lista_vendas, lista_res_mes, lista_preju, lista_ir_acoes, soma_ir_total_acoes

    def Calc_ir_fiis(self,usuario):

        hj = dt.datetime.today()

        con = sql.connect(usuario + ".db")
        self.venda_fiis = pd.read_sql('''  SELECT * FROM FII WHERE TIPO_DE_EVENTO="Venda" ORDER BY data ASC''',con)
        self.venda_fiis["Valor em Real"]=self.venda_fiis["valor"]*self.venda_fiis["qtd"]

        self.venda_fiis["data"] = pd.to_datetime(self.venda_fiis["data"])
        self.d1 = self.venda_fiis.iloc[0,4]

        self.nr_meses = dif_mes(hj, self.d1)+1

        self.datas = [self.d1]
        self.lista_vendas = []
        self.preju_acum = 0
        lista_preju = []
        lista_res_mes = []
        lista_ir_fiis = []

        for i in range(self.nr_meses):
            self.mes_atual = self.datas[-1]
            self.proximo_mes = (self.mes_atual+dt.timedelta(days=31)).replace(day=1,hour=0,minute=0,second=0)
            self.datas.append(self.proximo_mes)

            self.venda_fiis_filt = self.venda_fiis[(self.venda_fiis["data"] >= self.mes_atual) & (self.venda_fiis["data"] < self.proximo_mes)]

            self.res_mes = self.venda_fiis_filt["Prejuizo_lucro"].sum()
            lista_res_mes.append(self.res_mes)

            if self.preju_acum >= 0:
                lista_preju.append(self.preju_acum)
                if self.res_mes >= 0:
                    self.preju_acum = 0
                else:
                    self.preju_acum = self.res_mes
            else:
                lista_preju.append(self.preju_acum)
                if self.res_mes >= 0:
                    self.saldo = self.res_mes + self.preju_acum
                    if self.saldo >= 0:
                        self.preju_acum = 0
                    else:
                        self.preju_acum = self.saldo
                else:
                    self.preju_acum = self.res_mes + self.preju_acum

            if self.res_mes != 0:
                self.res_total = self.res_mes + lista_preju[i]
                if self.res_total >= 0:
                    self.ir_devido_fiis = self.res_total*0.20
                else:
                    self.ir_devido_fiis = 0
            else:
                self.ir_devido_fiis = 0

            lista_ir_fiis.append(self.ir_devido_fiis)

        soma_ir_total_fiis = sum(lista_ir_fiis)

        if len(lista_res_mes) < 24:
            n = 24 - len(lista_res_mes)
            self.lista_zeros = [0]*n
            lista_res_mes = self.lista_zeros + lista_res_mes
            lista_preju = self.lista_zeros + lista_preju
            lista_ir_fiis = self.lista_zeros + lista_ir_fiis

        con.commit()
        con.close()

        return lista_res_mes, lista_preju, lista_ir_fiis, soma_ir_total_fiis

    def Calc_ir_rfs(self, usuario):

        con = sql.connect(usuario + ".db")

        titulos_ir_rf = pd.read_sql('''  SELECT * FROM RENDA_FIXA WHERE TIPO_DE_EVENTO="Resgate" AND ISENTO_IR="Não"''',
                                    con)
        titulos_ir_rf = list(titulos_ir_rf['titulo'])

        ir_rf = []
        for titulos in titulos_ir_rf:
            df_temp = pd.read_sql_query("SELECT * FROM RENDA_FIXA WHERE TITULO = '" + titulos + "'", con)
            qtd_resgate = df_temp[df_temp['tipo_de_evento'] == 'Resgate']['qtd']
            valor_unit = df_temp['valor_compra'] / df_temp['qtd']
            rend_unit = float(valor_unit.diff()[-1:])
            rend_total = rend_unit * qtd_resgate
            tempo_aplicado = float(pd.to_datetime(df_temp['data_compra']).diff()[-1:] / np.timedelta64(1, 'D'))

            if tempo_aplicado < 181:
                taxa_ir = 0.225
            elif tempo_aplicado < 361:
                taxa_ir = 0.2
            elif tempo_aplicado < 721:
                taxa_ir = 0.175
            else:
                taxa_ir = 0.15

            ir = taxa_ir * rend_total
            ir = list(ir)[-1]
            ir_rf.append(ir)

        ir_rf_total = sum(ir_rf)

        return ir_rf_total



if __name__ == "__main__":

    Calc_ir("Higor_Lopes")
