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

def busca_IPCA_m():

    df = pd.read_csv('http://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados/ultimos/48?formato=csv',
                     encoding="ISO-8859-1", sep=';')
    return df


class Evento:

    def __init__(self,  acao, tipo, valor, data, qtd=0, corretagem=0, usuario="acao", id=0):

        self.id = id
        self.usuario = usuario
        self.acao = acao
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

        if self.tipo == "rendimento":
            self.imposto_renda_prev = self.valor * 0.15

        return

    def salvaDB(self):

        con = sql.connect(self.usuario+".db")
        cursor = con.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS ACOES (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        acao TEXT NOT NULL,
                        tipo_de_evento TEXT NOT NULL,
                        valor NUMERIC NOT NULL,
                        data TEXT NOT NULL,
                        qtd INTEGER,
                        corretagem NUMERIC,
                        IR_previa NUMERIC,
                        Prejuizo_lucro NUMERIC);''')

        con.commit()
        cursor.execute(''' INSERT INTO ACOES (acao, tipo_de_evento, valor, data, qtd, corretagem,
                                          IR_previa, Prejuizo_lucro)
                           VALUES(?,?,?,?,?,?,?,?);        
        ''',(self.acao, self.tipo, self.valor, self.data, self.qtd, self.corretagem,
             self.imposto_renda_prev, self.preju_lucro))

        con.commit()
        con.close()
        return


class Acao:


    def __init__(self, cod_acao, usuario="acao"):

        # Cria os campos de cada Ação

        self.usuario = usuario
        self.acao = cod_acao
        self.buscaDB()                                              # Busca os eventos já registrados no banco de dados
        self.criaEventos()                                          # Gera a lista com os objetos Eventos
        self.preco_medio_sem_div = 0                                # Atribui valores iniciais
        self.qtd_atual = 0
        self.data_media_aquisicao = dt.datetime(1, 1, 1)
        self.valor_investido = 0
        self.rendimento_vendas = 0
        self.soma_dividendo = 0
        self.preco_medio_com_div = 0

        # Loop de cálculo para cada evento da lista de eventos do Banco de Dados

        for evento in self.eventos:

            if evento.tipo == "Compra":

                self.qtd_atual += evento.qtd                            # Grandezas que não demandam condições
                self.valor_investido += ((evento.valor*evento.qtd)+evento.corretagem)

                if self.preco_medio_sem_div == 0:                       # A cada iteração do loop ele calcula a média
                    self.preco_medio_sem_div = ((evento.valor*evento.qtd)+evento.corretagem)/evento.qtd             #  ponderada entre 2 valores

                else:
                    self.preco_medio_sem_div = (self.preco_medio_sem_div * self.qtd_atual + evento.valor*evento.qtd)\
                                                                    / (self.qtd_atual + evento.qtd)

                if self.data_media_aquisicao == dt.datetime(1, 1, 1):
                    self.data_media_aquisicao = evento.data

                else:
                    peso = (evento.qtd*evento.valor)/(self.valor_investido + (evento.qtd * evento.valor))
                                                                                         # A data média ponderada é
                    dif = evento.data - self.data_media_aquisicao                        # calculada com base na qtd de
                    self.data_media_aquisicao = self.data_media_aquisicao + (dif * peso) # ações compradas com relação
                                                                                         # à qtd existente.

            elif evento.tipo == "Venda":

                self.qtd_atual -= evento.qtd
                self.rendimento_vendas += (
                        ((evento.valor * evento.qtd) + evento.corretagem) - (self.preco_medio_sem_div * evento.qtd))
                evento.preju_lucro = ((evento.valor * evento.qtd) + evento.corretagem) - (self.preco_medio_sem_div * evento.qtd)
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

        self.valor_atual = self.qtd_atual*self.preco_medio_sem_div

        if self.soma_dividendo == 0:
            self.preco_medio_com_div = self.preco_medio_sem_div

        if self.qtd_atual > 0:
            try:
                self.cotacao_atual = self.CotacaoAtual()                    # Busca a cotação atual, caso ocorra erro zera o valor
                self.inflacao_acum = self.CalculaInflacaoAcumulada()
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

    def buscaDB(self):

        con = sql.connect(self.usuario+".db")
        cursor = con.cursor()

        self.lista_de_eventos = cursor.execute('''  SELECT * FROM ACOES WHERE acao= ? ORDER BY data ASC''',(self.acao,))
        con.commit()

        self.lista_de_eventos = cursor.fetchall()

        con.close()
        return

    def CotacaoAtual(self):

        CotacaoAtual = si.get_live_price(self.acao+".SA")

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


class Carteira:

    def __init__(self, usuario):

        self.usuario = usuario
        self.lista_acoes = self.buscaAcoes()
        self.criaAcoes()

    def buscaAcoes(self):

        con = sql.connect(self.usuario + ".db")
        cursor = con.cursor()
        lista_acoes = cursor.execute(''' SELECT DISTINCT acao FROM ACOES ''').fetchall()
        con.close()

        return lista_acoes

    def criaAcoes(self):


        self.acoes = [Acao(str(acao)[2:7],self.usuario) for acao in self.lista_acoes]



if __name__ == "__main__":

    TRPL = Acao("TRPL4")

    print(TRPL.data_media_aquisicao)
    print(TRPL.qtd_atual)
    print(TRPL.preco_medio_sem_div)

    petr = Acao("PETR4","Eduardo_Rosa")

    print(petr.data_media_aquisicao, petr.valor_investido, petr.qtd_atual, petr.preco_medio_sem_div)