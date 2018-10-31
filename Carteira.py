#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
__author__ = "Eduardo Rosa"
__version__ = "1.0.1"
__email__ = "educarvalhor@gmail.com"
"""

import sqlite3 as sql
import datetime as dt
import pandas as pd
from yahoo_fin import stock_info as si
import time
from functools import wraps
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from os import chdir, getcwd
from functools import reduce

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

    c.close()


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
    lista_acoes = cursor.execute(''' SELECT DISTINCT acao FROM ACOES ''').fetchall()
    try:
        lista_fii = cursor.execute(''' SELECT DISTINCT FII FROM FII ''').fetchall()
    except sql.OperationalError as e:
        lista_fii = [""]
    con.close()

    return lista_acoes , lista_fii


def buscaRendaFixa(usuario):

    con = sql.connect(usuario + ".db")
    cursor = con.cursor()
    try:
        lista = cursor.execute(''' SELECT DISTINCT titulo FROM RENDA_FIXA ''').fetchall()
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
    print(fora_da_lista)


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
                    self.preco_medio_sem_div = (self.preco_medio_sem_div * self.qtd_atual +
                                                evento.corretagem + evento.valor_aplicado * evento.qtd) / (self.qtd_atual + evento.qtd)

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
                print("O tipo de evento é {}".format(evento.tipo_operacao))

            self.retorno_total = (((self.valor_venda_total + self.valor_dividendo_total - self.corretagem_total)/self.valor_compra_total)-1)*100

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

        CotacaoAtual = si.get_live_price(self.codigo + ".SA")

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
                print("O tipo de evento é {}".format(evento.tipo_operacao))

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

        try:
            CotacaoAtual = si.get_live_price(self.codigo + ".SA")
        except ValueError as e:
            CotacaoAtual = 0

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
        self.valor_resgatado = 0
        self.rendimento = 0
        self.ipca_acumulado = 0
        self.valor_atual = 0
        self.liquidez = 0

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
            cdi_acum = reduce(lambda x,y: x*y,cdi) - 1
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
            print("ERRO no cálculo da taxa do IR RENDA FIXA")

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


class Carteira:

    def __init__(self, usuario):

        self.usuario = usuario
        self.lista_acoes, self.lista_fii = buscaRendaVar(usuario)
        self.lista_renda_fixa = buscaRendaFixa(usuario)
        self.criaAcoes()
        self.criaFII()
        return

    def criaAcoes(self):

        self.acoes = [Acao(str(acao)[2:7],self.usuario) for acao in self.lista_acoes]
        return

    def criaFII(self):
        self.fii = [FII(str(fii)[2:8],self.usuario) for fii in self.lista_fii]
        return

if __name__ == "__main__":

#    TRPL = Acao("TRPL4")
#
#    print(TRPL.data_media_aquisicao)
#    print(TRPL.qtd_atual)
#    print(TRPL.preco_medio_sem_div)
#
#    petr = Acao("PETR4","Eduardo_Rosa")
#
#    print(petr.data_media_aquisicao, petr.valor_investido, petr.qtd_atual, petr.preco_medio_sem_div)
#
#    IPCA = busca_IPCA_m()
#    c = sql.connect("dados_basicos_pb.db")
#    IPCA.to_sql("IPCA_MENSAL", c, if_exists="append")
#    c.close()
    atualiza_ipca_mensal()