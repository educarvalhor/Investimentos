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

def timethis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        r = func(*args, **kwargs)
        end = time.perf_counter()
        print('{}.{} : {}'.format(func.__module__,func.__name__, end - start))
        return r
    return wrapper

@timethis
def busca_IPCA_m():

    df = pd.read_csv('http://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados/ultimos/48?formato=csv',
                     encoding="ISO-8859-1", sep=';')
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


def salvaDB(usuario, tipo_inv, investimento, tipo, valor, data, qtd, corretagem, ir_prev, prej_lucro):

    con = sql.connect(usuario+".db")
    cursor = con.cursor()

    if tipo_inv == "ACOES":
        campo2 = "acao"
    elif tipo_inv == "FII":
        campo2 = tipo_inv
    else:
        campo2 = ""

    query = '''CREATE TABLE IF NOT EXISTS {} (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    {} TEXT NOT NULL,
                    tipo_de_evento TEXT NOT NULL,
                    valor NUMERIC NOT NULL,
                    data TEXT NOT NULL,
                    qtd INTEGER,
                    corretagem NUMERIC,
                    IR_previa NUMERIC,
                    Prejuizo_lucro NUMERIC);'''.format(tipo_inv, campo2)

    cursor.execute(query)

    con.commit()

    query2 = ''' INSERT INTO {} ({}, tipo_de_evento, valor, data, qtd, corretagem,
                                      IR_previa, Prejuizo_lucro)
                       VALUES(?,?,?,?,?,?,?,?);        '''.format(tipo_inv, campo2)

    cursor.execute(query2, (investimento, tipo, valor, data, qtd, corretagem, ir_prev, prej_lucro))

    con.commit()
    con.close()
    return


class Evento:

    def __init__(self,  investimento, tipo, valor, data, qtd=0, corretagem=0, usuario="acao", id=0):

        self.id = id
        self.usuario = usuario
        self.investimento = investimento
        self.tipo = tipo
        self.valor = valor

        data  = data.replace("-","/")                                       # Corrige a data se inserida com -
        data = data[0:10]                                                   # Busca somente a data e deixa as horas
        if data[2] == "/":                                                  # Verifica se é dd/mm/aaaa
            data = data[-4:]+data[2:6]+data[0:2]                            # Inverte para aaaa/mm/dd
        self.data = dt.datetime.strptime(data, "%Y/%m/%d")

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

            if evento.tipo == "Compra":

                if self.preco_medio_sem_div == 0:                       # A cada iteração do loop ele calcula a média
                    self.preco_medio_sem_div = ((evento.valor*evento.qtd)+evento.corretagem)/evento.qtd             #  ponderada entre 2 valores
                else:
                    self.preco_medio_sem_div = (self.preco_medio_sem_div * self.qtd_atual + self.corretagem_total +
                                                evento.corretagem + evento.valor*evento.qtd)/(self.qtd_atual + evento.qtd)

                if self.data_media_aquisicao == dt.datetime(1, 1, 1):
                    self.data_media_aquisicao = evento.data

                else:
                    peso = (evento.qtd*evento.valor)/(self.valor_investido + (evento.qtd * evento.valor))
                                                                                         # A data média ponderada é
                    dif = evento.data - self.data_media_aquisicao                        # calculada com base na qtd de
                    self.data_media_aquisicao = self.data_media_aquisicao + (dif * peso) # ações compradas com relação
                                                                                         # à qtd existente.

                self.qtd_atual += evento.qtd                            # Grandezas que não demandam condições
                self.valor_investido += ((evento.valor*evento.qtd)+evento.corretagem)


            elif evento.tipo == "Venda":

                self.qtd_atual -= evento.qtd
                self.rendimento_vendas += (
                        ((evento.valor * evento.qtd) + evento.corretagem) - (self.preco_medio_sem_div * evento.qtd))
                evento.preju_lucro = (evento.valor * evento.qtd) + evento.corretagem - (self.preco_medio_sem_div * evento.qtd)
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
                    self.valor_investido -= (evento.valor*evento.qtd)+evento.corretagem

            elif evento.tipo == "Rendimento":

                if self.qtd_atual == 0:
                    continue
                else:
                    self.soma_dividendo += evento.valor
                    self.preco_medio_com_div = (self.qtd_atual * self.preco_medio_sem_div - self.soma_dividendo)/self.qtd_atual

            else:
                print("O tipo de evento é {}".format(evento.tipo))

        # Fim do loop de eventos

        self.valor_atual = self.qtd_atual*self.preco_medio_sem_div

        if self.soma_dividendo == 0:
            self.preco_medio_com_div = self.preco_medio_sem_div

        # Busca a cotação da ação se a qtd for maior que zero
        if self.qtd_atual > 0:
            try:
                self.cotacao_atual = self.CotacaoAtual()
                self.inflacao_acum = self.CalculaInflacaoAcumulada()
            except KeyError as e:
                self.cotacao_atual = 0
        else:
            self.cotacao_atual = 0
            self.inflacao_acum = 0
            self.valor_compra_total = 0
            self.valor_venda_total = 0
            self.valor_dividendo_total = 0
            self.retorno_total = 0
            self.corretagem_total = 0

            for evento in self.eventos:
                if evento.tipo == "Compra":
                    self.valor_compra_total += (evento.valor*evento.qtd)
                    self.corretagem_total += evento.corretagem
                elif evento.tipo == "Venda":
                    self.valor_venda_total += (evento.valor*evento.qtd)
                    self.corretagem_total += evento.corretagem
                elif evento.tipo == "Rendimento":
                    self.valor_dividendo_total += evento.valor

                self.retorno_total = (((self.valor_venda_total + self.valor_dividendo_total - self.corretagem_total)/self.valor_compra_total)-1)*100


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


            if evento.tipo == "Compra":

                if self.preco_medio_sem_div == 0:                       # A cada iteração do loop ele calcula a média
                    self.preco_medio_sem_div = ((evento.valor*evento.qtd)+evento.corretagem)/evento.qtd             #  ponderada entre 2 valores
                else:
                    self.preco_medio_sem_div = (self.preco_medio_sem_div * self.qtd_atual + self.corretagem_total +
                                                evento.corretagem + evento.valor*evento.qtd)/(self.qtd_atual + evento.qtd)
                if self.data_media_aquisicao == dt.datetime(1, 1, 1):
                    self.data_media_aquisicao = evento.data

                else:
                    peso = (evento.qtd*evento.valor)/(self.valor_investido + (evento.qtd * evento.valor))
                                                                                         # A data média ponderada é
                    dif = evento.data - self.data_media_aquisicao                        # calculada com base na qtd de
                    self.data_media_aquisicao = self.data_media_aquisicao + (dif * peso) # ações compradas com relação
                                                                                         # à qtd existente.

                self.qtd_atual += evento.qtd                            # Grandezas que não demandam condições
                self.valor_investido += ((evento.valor * evento.qtd) + evento.corretagem)


            elif evento.tipo == "Venda":

                self.qtd_atual -= evento.qtd
                self.rendimento_vendas += (
                        ((evento.valor * evento.qtd) + evento.corretagem) - (self.preco_medio_sem_div * evento.qtd))
                evento.preju_lucro = (evento.valor * evento.qtd) + evento.corretagem - (self.preco_medio_sem_div * evento.qtd)
                evento.imposto_renda_prev = 0.20*evento.preju_lucro

                self.AtualizaEvento(evento)

                if self.qtd_atual == 0:
                    self.data_media_aquisicao = dt.datetime(1, 1, 1)
                    self.preco_medio_sem_div = 0
                    self.valor_investido = 0
                    self.rendimento_vendas = 0
                    self.preco_medio_com_div = 0
                    self.soma_dividendo = 0
                else:
                    self.valor_investido -= (evento.valor*evento.qtd)+evento.corretagem

            elif evento.tipo == "Rendimento":

                if self.qtd_atual == 0:
                    continue
                else:
                    self.soma_dividendo += evento.valor
                    self.preco_medio_com_div = (self.qtd_atual * self.preco_medio_sem_div - self.soma_dividendo)/self.qtd_atual

            else:
                print("O tipo de evento é {}".format(evento.tipo))

        # Fim do loop de eventos

        self.valor_atual = self.qtd_atual*self.preco_medio_sem_div

        if self.soma_dividendo == 0:
            self.preco_medio_com_div = self.preco_medio_sem_div

        # Busca a cotação da ação se a qtd for maior que zero
        if self.qtd_atual > 0:
            try:
                self.cotacao_atual = self.CotacaoAtual()
                self.inflacao_acum = self.CalculaInflacaoAcumulada()
            except KeyError as e:
                self.cotacao_atual = 0
        else:
            self.cotacao_atual = 0
            self.inflacao_acum = 0
            self.valor_compra_total = 0
            self.valor_venda_total = 0
            self.valor_dividendo_total = 0
            self.retorno_total = 0
            self.corretagem_total = 0

            for evento in self.eventos:
                if evento.tipo == "Compra":
                    self.valor_compra_total += (evento.valor*evento.qtd)
                    self.corretagem_total += evento.corretagem
                elif evento.tipo == "Venda":
                    self.valor_venda_total += (evento.valor*evento.qtd)
                    self.corretagem_total += evento.corretagem
                elif evento.tipo == "Rendimento":
                    self.valor_dividendo_total += evento.valor
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


class Carteira:

    def __init__(self, usuario):

        self.usuario = usuario
        self.lista_acoes, self.lista_fii = buscaRendaVar(usuario)
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

    TRPL = Acao("TRPL4")

    print(TRPL.data_media_aquisicao)
    print(TRPL.qtd_atual)
    print(TRPL.preco_medio_sem_div)

    petr = Acao("PETR4","Eduardo_Rosa")

    print(petr.data_media_aquisicao, petr.valor_investido, petr.qtd_atual, petr.preco_medio_sem_div)