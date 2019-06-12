
# -*- coding: utf-8 -*-

"""
__author__ = "Eduardo Rosa", "Higor_Lopes", "Marcelo Bulhões"
__version__ = "1.0.1"
"""

# PRÓXIMAS IMPLEMENTAÇÕES

# todo Gráfico de Evolução da Carteira
# todo Back-test de estratégias
# todo Erro do gráfico do peste black no pc do Marselhesa
# todo Nota de Oportunidade
# todo Gráfico da aba gráficos plota um abaixo do outro
# todo Criar README para o GitHub
# todo OCR nas notas de corretagem

import threading
import pandas as pd
import matplotlib
#from matplotlib.backends._backend_tk import NavigationToolbar2Tk

from PyQt5 import QtCore, QtGui, QtWidgets
from cal import Ui_Dialog
import sqlite3 as sql
import os

matplotlib.use('TkAgg')

pd.core.common.is_list_like = pd.api.types.is_list_like

# from pandas_datareader import data
# import fix_yahoo_finance as yf
# yf.pdr_override()

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import Calc_pb_v2 as calc
import DB_pb_v2 as db

import Carteira as ct
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Canvas
import datetime as dt
from Carteira import timethis

from tkcalc import calculator

import re

import numpy as np
import seaborn as sb

# Usuários cadastrados
usuarios = ["Higor_Lopes", "Eduardo_Rosa", "Marcelo_Bulhoes" ]


class AutoScrollbar(ttk.Scrollbar):

    # Somente funciona se utilizar o GRID
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        ttk.Scrollbar.set(self, lo, hi)
        return

# CRIA LABEL DE TEXTO QUANDO PASSA O MOUSE EM CIMA
class HoverInfo(tk.Menu):
    def __init__(self, parent, text, command=None):
        self._com = command
        tk.Menu.__init__(self,parent, tearoff=0)
        if not isinstance(text, str):
            raise TypeError('Trying to initialise a Hover Menu with a non string type: ' + text.__class__.__name__)
        toktext=re.split('\n', text)
        for t in toktext:
            self.add_command(label = t)
            self._displayed=False
            self.master.bind("<Enter>",self.Display )
            self.master.bind("<Leave>",self.Remove )

    def __del__(self):
        self.master.unbind("<Enter>")
        self.master.unbind("<Leave>")

    def Display(self,event):
        if not self._displayed:
            self._displayed=True
            self.post(event.x_root, event.y_root)
        if self._com != None:
            self.master.unbind_all("<Return>")
            self.master.bind_all("<Return>", self.Click)

    def Remove(self, event):

        self.grid_forget()
        if self._displayed:
            self._displayed=False
            self.unpost()
        if self._com != None:
            self.unbind_all("Return")

    def Click(self, event):
        self._com()


class EventosGUI:

    def __init__(self, usuario, investimento, tipo):

        self.tipo = tipo
        self.win = tk.Tk()
        self.win.geometry('1180x400')
        #self.win.resizable(0, 0)
        self.win.title("Eventos")
        self.win.iconbitmap(r'peste_black_icon.ico')

        # FRAME E MENU
        self.fr_novos_eventos = ttk.LabelFrame(self.win, text=self.tipo)
        self.fr_novos_eventos.pack(expand=1, fill=tk.BOTH)

        # FUNÇÃO PARA CRIAR OS WIDGETS
        if self.tipo == "RENDA_FIXA":
            self.cria_widgets_renda_fixa()
        elif self.tipo == "DINHEIRO":
            self.cria_widgets_dinheiro()
        else:
            self.cria_widgets()
            
        if self.tipo == "DINHEIRO":
            investimento = ""
            self.investimento1 = investimento
        else:
            self.investimento1 = investimento

        self.usuario = usuario

        self.mostra_eventos()
        
        if self.tipo == "RENDA_FIXA":
            self.mostra_valores_renda_fixa()

        elif self.tipo == "ACOES" or self.tipo == "FII":
            self.mostra_valores()

        elif self.tipo == "DINHEIRO":
            self.mostra_valores_dinheiro()

        return

    def cria_widgets(self):

        # Labels

        self.lb_tipo = ttk.Label(self.fr_novos_eventos, text="Tipo de evento")
        self.lb_valor = ttk.Label(self.fr_novos_eventos, text="Valor")
        self.lb_qtd = ttk.Label(self.fr_novos_eventos, text="Quantidade")
        self.lb_corr = ttk.Label(self.fr_novos_eventos, text="Corretagem")
        self.lb_data = ttk.Label(self.fr_novos_eventos, text="Data")


        # Textos

        self.st_tipos = tk.StringVar()
        self.tx_tipo = ttk.Combobox(self.fr_novos_eventos, textvariable= self.st_tipos, width=20,height=5)
        self.tx_tipo["values"] = ["Compra","Venda", "Rendimento"]

        self.st_valor = tk.StringVar(value=0)
        self.tx_valor = ttk.Entry(self.fr_novos_eventos, width=10, textvariable=self.st_valor)

        self.st_qtd = tk.StringVar(value=0)
        self.tx_qtd = ttk.Entry(self.fr_novos_eventos, width=10, textvariable=self.st_qtd)

        self.st_corr = tk.StringVar(value=0)
        self.tx_corr = ttk.Entry(self.fr_novos_eventos, width=10, textvariable=self.st_corr)

        self.st_data = tk.StringVar(value="")
        self.tx_data = ttk.Entry(self.fr_novos_eventos, width=10, textvariable=self.st_data)

        self.tx_log = scrolledtext.ScrolledText(self.fr_novos_eventos, width=100, height=1, wrap=tk.WORD)

        self.st_id = tk.StringVar(value=0)
        self.tx_id = ttk.Entry(self.fr_novos_eventos, width=10, textvariable=self.st_id)

        self.tx_eventos = scrolledtext.ScrolledText(self.fr_novos_eventos, width=100, height=12, wrap=tk.WORD)

        # Botões

        self.bt_salva_evento = ttk.Button(self.fr_novos_eventos, text="Salva Evento", command=self.salva_evento)

        self.bt_apaga_evento = ttk.Button(self.fr_novos_eventos, text="Apaga Evento", command=self.apaga_evento)

        self.bt_mostra_evento = ttk.Button(self.fr_novos_eventos, text="Atualiza Eventos", command=self.mostra_eventos)

        self.bt_cal_data = ttk.Button(self.fr_novos_eventos, text="...", command=self.chama_cal_ev)
        self.bt_cal_data.config(width=1)

        # Layout

        self.lb_tipo.grid(row=0, column=0, sticky=tk.W, padx='5')
        self.lb_valor.grid(row=0, column=1,  padx='5')
        self.lb_qtd.grid(row=0, column=2, padx='5')
        self.lb_corr.grid(row=0, column=3, padx='5')
        self.lb_data.grid(row=0, column=4, sticky=tk.W,  padx='5')

        self.bt_salva_evento.grid(row=1, column=6, padx='10')

        self.tx_tipo.grid(row=1, column=0, sticky=tk.W, padx='5')
        self.tx_valor.grid(row=1, column=1,  padx='5')
        self.tx_qtd.grid(row=1, column=2, padx='5')
        self.tx_corr.grid(row=1, column=3, sticky=tk.W, padx='5')
        self.tx_data.grid(row=1, column=4, sticky=tk.W, padx='5')
        self.bt_cal_data.grid(row=1, column=5)

        self.tx_log.grid(row=2, column=0, columnspan=7, sticky=tk.W, padx='10')

        self.tx_id.grid(row=3, column=0)

        self.bt_apaga_evento.grid(row=3, column=1, sticky=tk.W, padx='20')

        self.bt_mostra_evento.grid(row=3, column=2, sticky=tk.W, padx='20')

        self.tx_eventos.grid(row=4,column=0,columnspan=7, sticky=tk.W, rowspan=11,padx='10')
        return

    def cria_widgets_dinheiro(self):

        # Labels

        self.lb_tipo = ttk.Label(self.fr_novos_eventos, text="Deposito/Resgate")
        self.lb_data = ttk.Label(self.fr_novos_eventos, text="Data")
        self.lb_valor = ttk.Label(self.fr_novos_eventos, text="Valor")

        # Textos

        self.st_tipos = tk.StringVar()
        self.tx_tipo = ttk.Combobox(self.fr_novos_eventos, textvariable=self.st_tipos, width=10, height=5)
        self.tx_tipo["values"] = ["Deposito", "Resgate"]

        self.st_data = tk.StringVar(value="")
        self.tx_data = ttk.Entry(self.fr_novos_eventos, width=10, textvariable=self.st_data)

        self.st_valor = tk.StringVar(value=0)
        self.tx_valor = ttk.Entry(self.fr_novos_eventos, width=10, textvariable=self.st_valor)

        self.tx_log = scrolledtext.ScrolledText(self.fr_novos_eventos, width=100, height=1, wrap=tk.WORD)

        self.st_id = tk.StringVar(value=0)
        self.tx_id = ttk.Entry(self.fr_novos_eventos, width=10, textvariable=self.st_id)

        self.tx_eventos = scrolledtext.ScrolledText(self.fr_novos_eventos, width=100, height=12, wrap=tk.WORD)

        # Botões

        self.bt_salva_evento = ttk.Button(self.fr_novos_eventos, text="Salva Evento", command=self.salva_evento)

        self.bt_apaga_evento = ttk.Button(self.fr_novos_eventos, text="Apaga Evento", command=self.apaga_evento)

        self.bt_mostra_evento = ttk.Button(self.fr_novos_eventos, text="Atualiza Eventos", command=self.mostra_eventos)

        self.bt_cal_data = ttk.Button(self.fr_novos_eventos, text="...", command=self.chama_cal_ev)
        self.bt_cal_data.config(width=1)

        # Layout

        self.lb_tipo.grid(row=0, column=0, sticky=tk.W, padx='5')
        self.lb_data.grid(row=0, column=1, padx='5')
        self.lb_valor.grid(row=0, column=3, padx='5')

        self.bt_salva_evento.grid(row=1, column=4, padx='10')

        self.tx_tipo.grid(row=1, column=0, sticky=tk.W, padx='5')
        self.tx_data.grid(row=1, column=1, padx='5')

        self.tx_valor.grid(row=1, column=3, padx='5')

        self.bt_cal_data.grid(row=1, column=2)


        self.tx_log.grid(row=2, column=0, columnspan=6, sticky=tk.W, padx='10')

        self.tx_id.grid(row=3, column=0)

        self.bt_apaga_evento.grid(row=3, column=1, sticky=tk.W, padx='20')

        self.bt_mostra_evento.grid(row=3, column=2, sticky=tk.W, padx='20')

        self.tx_eventos.grid(row=4, column=0, columnspan=6, sticky=tk.W, rowspan=11, padx='10')

        return

    def cria_widgets_renda_fixa(self):

        # Labels

        self.lb_tipo = ttk.Label(self.fr_novos_eventos, text="Compra/Resgate")
        self.lb_tipo_aplicacao = ttk.Label(self.fr_novos_eventos, text="Tipo de aplicação")
        self.lb_tipo_taxa = ttk.Label(self.fr_novos_eventos, text="Tipo de taxa")
        self.lb_valor_taxa = ttk.Label(self.fr_novos_eventos, text="Valor do rendimento (%)")
        self.lb_valor = ttk.Label(self.fr_novos_eventos, text="Valor da operação")
        self.lb_qtd = ttk.Label(self.fr_novos_eventos, text="Quantidade")
        self.lb_data_carencia = ttk.Label(self.fr_novos_eventos, text="Data de carência")
        self.lb_data_vencimento = ttk.Label(self.fr_novos_eventos, text="Data de vencimento")
        self.lb_corr = ttk.Label(self.fr_novos_eventos, text="Isento de IR ?")
        self.lb_data = ttk.Label(self.fr_novos_eventos, text="Data")

        # Textos

        self.st_tipos = tk.StringVar()
        self.tx_tipo = ttk.Combobox(self.fr_novos_eventos, textvariable=self.st_tipos, width=10, height=5)
        self.tx_tipo["values"] = ["Compra", "Resgate"]

        self.st_tipo_aplicacao = tk.StringVar()
        self.tx_tipo_aplicacao = ttk.Combobox(self.fr_novos_eventos, textvariable=self.st_tipo_aplicacao, width=12,
                                              height=5)
        self.tx_tipo_aplicacao["values"] = ["CDB", "LCI", "LCA", "CRI", "CRA", "DEBENTURE", "LC", "TESOURO"]

        self.st_tipo_taxa = tk.StringVar()
        self.tx_tipo_taxa = ttk.Combobox(self.fr_novos_eventos, textvariable=self.st_tipo_taxa, width = 10, height=5)
        self.tx_tipo_taxa["values"] = ["% CDI", "IPCA +", "Préfixado", "SELIC", "CDI +"]

        self.st_valor_taxa = tk.StringVar(value=0)
        self.tx_valor_taxa = ttk.Entry(self.fr_novos_eventos, width=10, textvariable=self.st_valor_taxa)

        self.st_valor = tk.StringVar(value=0)
        self.tx_valor = ttk.Entry(self.fr_novos_eventos, width=10, textvariable=self.st_valor)

        self.st_qtd = tk.StringVar(value=0)
        self.tx_qtd = ttk.Entry(self.fr_novos_eventos, width=10, textvariable=self.st_qtd)

        self.st_data_carencia = tk.StringVar(value="")
        self.tx_data_carencia = ttk.Entry(self.fr_novos_eventos, width=10, textvariable=self.st_data_carencia)

        self.st_data_vencimento = tk.StringVar(value="")
        self.tx_data_vencimento = ttk.Entry(self.fr_novos_eventos, width=10, textvariable=self.st_data_vencimento)

        self.st_corr = tk.StringVar()
        self.tx_corr = ttk.Combobox(self.fr_novos_eventos, width=10, height=5, textvariable=self.st_corr)
        self.tx_corr["values"] = ["Sim", "Não"]

        self.st_data = tk.StringVar(value="")
        self.tx_data = ttk.Entry(self.fr_novos_eventos, width=10, textvariable=self.st_data)

        # CAMPO DO LOG DE EVENTOS
        self.tx_log = scrolledtext.ScrolledText(self.fr_novos_eventos, width=100, height=1, wrap=tk.WORD)

        # CAMPO DO ID PARA APAGAR OS EVENTOS
        self.st_id = tk.StringVar(value=0)
        self.tx_id = ttk.Entry(self.fr_novos_eventos, width=10, textvariable=self.st_id)

        # CAMPO QUE EXIBE OS EVENTOS
        self.tx_eventos = scrolledtext.ScrolledText(self.fr_novos_eventos, width=100, height=12, wrap=tk.WORD)

        # Botões

        self.bt_salva_evento = ttk.Button(self.fr_novos_eventos, text="Salva Evento", command=self.salva_evento)

        self.bt_apaga_evento = ttk.Button(self.fr_novos_eventos, text="Apaga Evento", command=self.apaga_evento)

        self.bt_mostra_evento = ttk.Button(self.fr_novos_eventos, text="Atualiza Eventos", command=self.mostra_eventos)

        self.bt_cal_data_car = ttk.Button(self.fr_novos_eventos, text="...", command=self.chama_cal_rf_car)
        self.bt_cal_data_car.config(width=1)

        self.bt_cal_data_venc = ttk.Button(self.fr_novos_eventos, text="...", command=self.chama_cal_rf_venc)
        self.bt_cal_data_venc.config(width=1)

        self.bt_cal_data = ttk.Button(self.fr_novos_eventos, text="...", command=self.chama_cal_ev)
        self.bt_cal_data.config(width=1)

        # Layout

        self.lb_tipo.grid(row=0, column=0, padx='1')
        self.lb_tipo_aplicacao.grid(row=0, column=1, padx='1')
        self.lb_tipo_taxa.grid(row=0, column=2, padx='1')
        self.lb_valor_taxa.grid(row=0, column=3, padx='1')
        self.lb_valor.grid(row=0, column=4, padx='1')
        self.lb_qtd.grid(row=2, column=0, padx='1')
        self.lb_data_carencia.grid(row=2, column=1, padx='1')
        self.lb_data_vencimento.grid(row=2, column=3, padx='1')
        self.lb_corr.grid(row=2, column=5, padx='1')
        self.lb_data.grid(row=2, column=6, padx='1')


        self.bt_salva_evento.grid(row=1, column=9, padx='2')

        self.tx_tipo.grid(row=1, column=0, padx='1')
        self.tx_tipo_aplicacao.grid(row=1, column=1, padx='1')
        self.tx_tipo_taxa.grid(row=1, column=2, padx='1')
        self.tx_valor_taxa.grid(row=1, column=3, padx='1')
        self.tx_valor.grid(row=1, column=4, padx='1')
        self.tx_qtd.grid(row=3, column=0, padx='1')
        self.tx_data_carencia.grid(row=3, column=1, padx='1')
        self.bt_cal_data_car.grid(row=3, column=2)
        self.tx_data_vencimento.grid(row=3, column=3, padx='1')
        self.bt_cal_data_venc.grid(row=3, column=4)
        self.tx_corr.grid(row=3, column=5, padx='1')
        self.tx_data.grid(row=3, column=6, padx='1')
        self.bt_cal_data.grid(row=3, column=7)


        self.tx_log.grid(row=4, column=0, columnspan=10, padx='4', sticky=tk.W)

        self.tx_id.grid(row=5, column=0)

        self.bt_apaga_evento.grid(row=5, column=1, padx='4')

        self.bt_mostra_evento.grid(row=5, column=2, padx='4')

        self.tx_eventos.grid(row=6, column=0, columnspan=11, rowspan=11, padx='4', sticky=tk.W)

        return

    # --------------- FUNÇÕES AUXILIARES ----------

    def chama_cal_ev(self):

        import sys
        app = QtWidgets.QApplication(sys.argv)
        Dialog = QtWidgets.QDialog()
        ui = Ui_Dialog()
        ui.setupUi(Dialog)
        Dialog.show()
        rsp = Dialog.exec_()
        if rsp == 1:
            date = ui.envia_data()

        data = str(date.toPyDate())
        data = data[-2:] + "/" + data[-5:-3] + "/" + data[:4]

        self.tx_data.delete(0, tk.END)
        self.tx_data.insert(0, data)

        return

    def chama_cal_rf_car(self):

        import sys
        app = QtWidgets.QApplication(sys.argv)
        Dialog = QtWidgets.QDialog()
        ui = Ui_Dialog()
        ui.setupUi(Dialog)
        Dialog.show()
        rsp = Dialog.exec_()
        if rsp == 1:
            date = ui.envia_data()

        data = str(date.toPyDate())
        data = data[-2:] + "/" + data[-5:-3] + "/" + data[:4]

        self.tx_data_carencia.delete(0, tk.END)
        self.tx_data_carencia.insert(0, data)

        return

    def chama_cal_rf_venc(self):

        import sys
        app = QtWidgets.QApplication(sys.argv)
        Dialog = QtWidgets.QDialog()
        ui = Ui_Dialog()
        ui.setupUi(Dialog)
        Dialog.show()
        rsp = Dialog.exec_()
        if rsp == 1:
            date = ui.envia_data()

        data = str(date.toPyDate())
        data = data[-2:] + "/" + data[-5:-3] + "/" + data[:4]

        self.tx_data_vencimento.delete(0, tk.END)
        self.tx_data_vencimento.insert(0, data)

        return

    # --------------- FUNÇÕES REFERENTES AOS EVENTOS ----------

    def apaga_evento(self):

        self.investimento.ApagaEvento(id=str(self.tx_id.get()))
        self.mostra_eventos()
        if self.tipo == "RENDA_FIXA":
            self.mostra_valores_renda_fixa()

        elif self.tipo == "ACOES" or self.tipo == "FII":
            self.mostra_valores()

        elif self.tipo == "DINHEIRO":
            self.mostra_valores_dinheiro()

        return

    def mostra_eventos(self):

        self.tx_eventos.delete('1.0', tk.END)
        if self.tipo == "ACOES":
            self.investimento = ct.Acao(self.investimento1, self.usuario)
            self.tx_eventos.insert(tk.INSERT,"ID - AÇÃO  -  TIPO  - VALOR  -  DATA  -  QTD  -  COR  -   IR   - PL  \n")
        elif self.tipo == "FII":
            self.investimento = ct.FII(self.investimento1, self.usuario)
            self.tx_eventos.insert(tk.INSERT,"ID -  FII  -  TIPO  -  VALOR  -  DATA  -  QTD  -  COR  -  IR  -  PL  \n")
        elif self.tipo == "RENDA_FIXA":
            self.investimento = ct.RendaFixa(self.investimento1, self.usuario)
            self.tx_eventos.insert(tk.INSERT, "ID  COD    OPER  TIPO RENDIM TX VALOR     DATA_C " +
                                              "  DATA_CAR    DATA_VENC  QTD  ISENTO_IR \n")
        elif self.tipo == "DINHEIRO":
            self.investimento = ct.Dinheiro(self.usuario)
            self.tx_eventos.insert(tk.INSERT,"ID - OPERAÇÃO - DATA - VALOR \n")
        else:
            print("Erro! Tipo de investimento incorreto!")


        for evento in self.investimento.lista_de_eventos:
            for campo in evento:
                self.tx_eventos.insert(tk.INSERT, " " + str(campo)[0:10] + " ")
            self.tx_eventos.insert(tk.INSERT,"\n")

        return

    def salva_evento(self):

        # Trata os dados

        usuario = self.usuario
        investimento = self.investimento1
        tipo = str(self.tx_tipo.get())
        valor = float(str(self.tx_valor.get().replace(",",".")))
        data = str(self.tx_data.get())

        if self.tipo == "RENDA_FIXA":
            tipo_aplicacao = str(self.tx_tipo_aplicacao.get())
            tipo_taxa = str(self.tx_tipo_taxa.get())
            valor_taxa = float(str(self.tx_valor_taxa.get()).replace(",","."))/100
            data_carencia = str(self.tx_data_carencia.get())
            data_vencimento = str(self.tx_data_vencimento.get())

        else:
            tipo_aplicacao = ""
            tipo_taxa = ""
            valor_taxa = 0
            data_carencia = ""
            data_vencimento = ""

        if self.tipo != "DINHEIRO":
            if self.tx_qtd.get() == "":
                qtd = ""
            else:
                qtd = float(str(self.tx_qtd.get()).replace(",","."))

            if self.tx_corr.get() == "":
                corretagem = 0
            else:
                if self.tipo == "RENDA_FIXA":
                    corretagem = str(self.tx_corr.get())
                else:
                    corretagem = float(str(self.tx_corr.get()).replace(",","."))

            if investimento == "" or data == "":
                self.tx_log.insert(tk.INSERT,"Evento não criado pois existem campos em branco" + "\n")
            else:
                ev = ct.Evento(investimento, tipo, valor, data, qtd, corretagem, usuario, tipo_aplicacao=tipo_aplicacao,
                               data_carencia=data_carencia,data_vencimento=data_vencimento,tipo_taxa=tipo_taxa,
                               valor_taxa=valor_taxa)

                ct.salvaDB(ev.usuario, self.tipo, ev.codigo, ev.tipo_operacao, ev.valor_aplicado, ev.data_aplicacao, ev.qtd,
                           ev.corretagem, ev.imposto_renda_prev, ev.preju_lucro, ev.tipo_aplicacao, ev.data_carencia,
                           ev.data_vencimento, ev.tipo_taxa, ev.valor_taxa)

                self.tx_log.insert(tk.INSERT,"\n" + "{0} de {1} salvo no banco de dados".format(ev.tipo_operacao, ev.codigo))
                self.tx_log.see(tk.END)
        else:
            qtd = 0
            corretagem = 0

            if data == "":
                self.tx_log.insert(tk.INSERT,"Evento não criado pois existem campos em branco" + "\n")
            else:
                ev = ct.Evento(investimento, tipo, valor, data, qtd, corretagem, usuario, tipo_aplicacao=tipo_aplicacao,
                               data_carencia=data_carencia,data_vencimento=data_vencimento,tipo_taxa=tipo_taxa,
                               valor_taxa=valor_taxa)

                ct.salvaDB(ev.usuario, self.tipo, ev.codigo, ev.tipo_operacao, ev.valor_aplicado, ev.data_aplicacao, ev.qtd,
                           ev.corretagem, ev.imposto_renda_prev, ev.preju_lucro, ev.tipo_aplicacao, ev.data_carencia,
                           ev.data_vencimento, ev.tipo_taxa, ev.valor_taxa)

                self.tx_log.insert(tk.INSERT,"\n" + "{0} de {1} salvo no banco de dados".format(ev.tipo_operacao, ev.codigo))
                self.tx_log.see(tk.END)

        self.mostra_eventos()
        if self.tipo == "RENDA_FIXA":
            self.mostra_valores_renda_fixa()

        elif self.tipo == "ACOES" or self.tipo == "FII":
            self.mostra_valores()

        elif self.tipo == "DINHEIRO":
            self.mostra_valores_dinheiro()

        return

    # --------------- FUNÇÕES PARA APARECER OS DADOS NA LATERAL ----------

    def mostra_valores_renda_fixa(self):
        
        if self.investimento.valor_investido > 0:
            
            self.campos_nome = ["Data de aplicação", "Data de Carência", "Data de Vencimento","Valor aplicado (R$)", "Valor atual Bruto (R$)",
                                "Valor Atual Líq. (R$)","Taxa de Retorno liq. (%)"]
            
            self.campos_acao = [self.investimento.data_compra.strftime("%d / %m / %Y"),
                                self.investimento.data_carencia.strftime("%d / %m / %Y"),
                                self.investimento.data_vencimento.strftime("%d / %m / %Y"),
                                '$ {:,}'.format(round(self.investimento.valor_investido, 2)),
                                '$ {:,}'.format(round(self.investimento.valor_atual_bruto, 2)),
                                '$ {:,}'.format(round(self.investimento.valor_atual_liq, 2)),
                                '{} %'.format(round(self.investimento.taxa_atual_liq, 2))]
            
            self.entries = []
            
            tk.Label(self.fr_novos_eventos, text=self.investimento.codigo).grid(row=0, column=11)

            for i, campo in enumerate(self.campos_acao):
                # Cria os labels dos campos da ação
                tk.Label(self.fr_novos_eventos, text=self.campos_nome[i]).grid(row=i + 1, column=10)
                # Cria as entries
                self.entries.append(tk.Entry(self.fr_novos_eventos, bg='white', width=15))
                # Insere o valor dos campos
                self.entries[i].insert('end', str(campo))
                # Posiciona as entries
                self.entries[i].grid(row=i + 1, column=11)
                
        else:
            self.campos_nome = ["Data de aplicação", "Data de Vencimento","Valor aplicado (R$)", "Valor Resgatado Bruto (R$)",
                                "Imposto de Renda (R$)", "Valor Final Líquido", "Taxa de Retorno liq. (%)"]
            
            self.campos_acao = [self.investimento.data_compra.strftime("%d / %m / %Y"),
                                self.investimento.data_vencimento.strftime("%d / %m / %Y"),
                                '$ {:,}'.format(round(self.investimento.valor_aplicado, 2)),
                                '$ {:,}'.format(round(self.investimento.valor_resgatado, 2)),
                                '$ {:,}'.format(round(self.investimento.ir, 2)),
                                '$ {:,}'.format(round(self.investimento.valor_final_liq, 2)),
                                '{} %'.format(round(self.investimento.taxa_final_liq, 2))]
            
            self.entries = []
            
            tk.Label(self.fr_novos_eventos, text=self.investimento.codigo).grid(row=0, column=11)

            for i, campo in enumerate(self.campos_acao):
                # Cria os labels dos campos da ação
                tk.Label(self.fr_novos_eventos, text=self.campos_nome[i]).grid(row=i + 1, column=10)
                # Cria as entries
                self.entries.append(tk.Entry(self.fr_novos_eventos, bg='white', width=15))
                # Insere o valor dos campos
                self.entries[i].insert('end', str(campo))
                # Posiciona as entries
                self.entries[i].grid(row=i + 1, column=11)
        

        return

    def mostra_valores_dinheiro(self):

        self.campos_nome = ["Total de Depósito (R$)", "Total de Resgates (R$)", "Total Aplicado (R$)",
                            "Total Corr. IPCA ($)", "IPCA acumulado (%)"]

        self.campos_acao = [ '$ {:,}'.format(round(self.investimento.depositos, 2)),
                             '$ {:,}'.format(round(self.investimento.resgates, 2)),
                             '$ {:,}'.format(round(self.investimento.soma_dinheiro_aplicado, 2)),
                             '$ {:,}'.format(round(self.investimento.soma_dinheiro_corr_ipca, 2)),
                             '{} %'.format(round(self.investimento.taxa_ipca_acum_dinheiro, 2))]

        self.entries = []

        for i, campo in enumerate(self.campos_acao):
            # Cria os labels dos campos da ação
            tk.Label(self.fr_novos_eventos, text=self.campos_nome[i]).grid(row=i + 1, column=10)
            # Cria as entries
            self.entries.append(tk.Entry(self.fr_novos_eventos, bg='white', width=15))
            # Insere o valor dos campos
            self.entries[i].insert('end', str(campo))
            # Posiciona as entries
            self.entries[i].grid(row=i + 1, column=11)

        return

    def mostra_valores(self):

        if self.investimento.qtd_atual > 0:

            self.campos_nome = ["Qtd atual", "Preço médio (R$)", "Valor Investido (R$)","Cotação atual (R$)", "Valor atual (R$)",
                                "Variação sem div. (%)", "Dividendos (R$)", "Div. Yield mensal (%)", "Variação c/ div. (%)", "Data média aq.",
                                "Inflação acumulada (%)", "Variação Real (%)"]

            self.campos_acao = [self.investimento.qtd_atual, '$ {:,}'.format(round(self.investimento.preco_medio_sem_div, 2)),
                                '$ {:,}'.format(round(self.investimento.valor_investido, 2)),
                                '$ {:,}'.format(round(self.investimento.cotacao_atual, 2)),
                                '$ {:,}'.format(round(self.investimento.valor_atual, 2)),
                                '{} %'.format(round(self.investimento.RetornoSemDiv, 2)),
                                '$ {:,}'.format(round(self.investimento.soma_dividendo, 2)),
                                '{} %'.format(round(self.investimento.div_yield_mensal, 2)),
                                '{} %'.format(round(self.investimento.RetornoComDiv, 2)),
                                self.investimento.data_media_aquisicao.strftime("%d / %m / %Y"),
                                '{} %'.format(round(self.investimento.inflacao_acum, 2)),
                                '{} %'.format(round(self.investimento.RetornoRealSemDiv, 2))]

            self.entries = []

            try:
                tk.Label(self.fr_novos_eventos, text=self.investimento.codigo).grid(row=0, column=7)
            except AttributeError as e:
                tk.Label(self.fr_novos_eventos, text=self.investimento.fii).grid(row=0, column=7)

            for i, campo in enumerate(self.campos_acao):
                # Cria os labels dos campos da ação
                tk.Label(self.fr_novos_eventos, text=self.campos_nome[i]).grid(row=i + 1, column=7)
                # Cria as entries
                self.entries.append(tk.Entry(self.fr_novos_eventos, bg='white', width=15))
                # Insere o valor dos campos
                self.entries[i].insert('end', str(campo))
                # Posiciona as entries
                self.entries[i].grid(row=i + 1, column=8)

        else:
            self.campos_nome = ["Qtd atual","Total de Compras", "Total de Vendas", "Total de Rendimentos",
                                "Total de Corretagem","Retorno Global"]
            self.campos_acao = [self.investimento.qtd_atual, '$ {:,}'.format(round(self.investimento.valor_compra_total, 2)),
                                '$ {:,}'.format(round(self.investimento.valor_venda_total, 2)),
                                '$ {:,}'.format(round(self.investimento.valor_dividendo_total, 2)),
                                '$ {:,}'.format(round(self.investimento.corretagem_total, 2)),
                                '{} %'.format(round(self.investimento.retorno_total, 2))]
            self.entries = []

            tk.Label(self.fr_novos_eventos, text=self.investimento.codigo).grid(row=0, column=7)

            for i, campo in enumerate(self.campos_acao):
                # Cria os labels dos campos da ação
                tk.Label(self.fr_novos_eventos, text=self.campos_nome[i]).grid(row=i + 1, column=7)
                # Cria as entries
                self.entries.append(tk.Entry(self.fr_novos_eventos, bg='white', width=15))
                # Insere o valor dos campos
                self.entries[i].insert('end', str(campo))
                # Posiciona as entries
                self.entries[i].grid(row=i + 1, column=8)

        return


class MainGUI:

    def __init__(self):

        self.win = tk.Tk()
        self.win.geometry('1000x805')
        self.win.title("Carteira de Investimentos")
        self.win.iconbitmap(r'peste_black_icon.ico')

        vscrollbar = AutoScrollbar(self.win, orient=tk.VERTICAL)
        vscrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        hscrollbar = AutoScrollbar(self.win, orient=tk.HORIZONTAL)
        hscrollbar.grid(row=1, column=0, sticky=tk.E + tk.W)

        self.canvas = Canvas(self.win,
                        yscrollcommand=vscrollbar.set,
                        xscrollcommand=hscrollbar.set)
        self.canvas.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)

        vscrollbar.config(command=self.canvas.yview)
        hscrollbar.config(command=self.canvas.xview)

        # make the canvas expandable
        self.win.grid_rowconfigure(0, weight=1)
        self.win.grid_columnconfigure(0, weight=1)

        # create canvas contents

        # FRAME
        self.fr_principal = ttk.Frame(self.canvas)
        self.fr_botoes = tk.Frame(self.fr_principal, padx='10')

        # HOVER LABEL
        self.lb_hover = tk.Label(self.fr_principal, text="AQUI")

        # NOTEBOOK

        self.note = ttk.Notebook(self.fr_principal)
        self.tab_resumao = tk.Frame(self.note, width=730, height=630)
        self.tab_dados = tk.Frame(self.note)
        self.tab_peste_black = tk.Frame(self.note)
        self.tab_calc_ir = tk.Frame(self.note)
        self.tab_graf = tk.Frame(self.note)

        self.note.add(self.tab_resumao, text="Resumão")
        self.note.add(self.tab_dados, text="Títulos")
        self.note.add(self.tab_peste_black, text="Peste Black")
        self.note.add(self.tab_calc_ir, text="Calc. IR")
        self.note.add(self.tab_graf, text="Gráficos")

        # HABILITA A BUSCA DOS TITULOS CLICANDO NA ABA
        self.primeiro_clique = True
        self.note.bind('<Button-1>', self.clica_notebook)

        self.fr_principal.rowconfigure(1, weight=1)
        self.fr_principal.columnconfigure(1, weight=1)

        self.fr_principal.pack(expand=1, fill=tk.BOTH)

        # FUNÇÃO PARA CRIAR OS WIDGETS
        self.cria_widgets()

        #FUNÇÃO PARA OS GRÁFICOS
        self.graficos()

        # FUNÇÃO CRIA PESTE BLACK
        self.peste_black()

        self.fr_botoes.grid(row=0, column=0, columnspan=5, sticky=tk.W)
        self.note.grid(row=1, column=0)
        self.lb_hover.grid(row=2, column=0, sticky=tk.W)


        self.canvas.create_window(0, 0, anchor=tk.NW, window=self.fr_principal)
        self.fr_principal.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        #FUNÇÃO PARA ABA RESUMAO
        self.widgets_resumao()

        # FUNÇÃO PARA ABA CALCULADORA DE IR
        self.widgets_calc_ir()

        self.atualiza_db()

        # CRIAÇÃO DO MENU
        self.menuBar = tk.Menu(self.win)
        self.win.config(menu=self.menuBar)

        # MENU ARQUIVO
        self.fileMenu = tk.Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label="Calculadora", command=self._calc, accelerator="Ctrl+Q")
        self.fileMenu.add_separator()
        self.menuBar.add_cascade(label="Arquivo", menu=self.fileMenu)

        self.win.bind_all("<Control-q>", self._calc)

        self.fr_principal.bind_all("<Enter>", self.on_enter)
        self.fr_principal.bind_all("<Leave>", self.on_leave)

        return

    def clica_notebook(self, event):

        clicked_tab = self.note.tk.call(self.note._w, "identify", "tab", event.x, event.y)

        active_tab = self.note.index(self.note.select())

        if clicked_tab == 1 & self.primeiro_clique == True:
            self.busca_titulos()
            self.primeiro_clique = False

        return

    def cria_widgets(self):

        # Label

        self.lb_codigo = ttk.Label(self.fr_botoes, text="Código")
        self.lb_user = ttk.Label(self.fr_botoes, text="Usuário")

        # Texto

        self.st_codigo = tk.StringVar(value="")
        self.tx_codigo = ttk.Combobox(self.fr_botoes, width=20, textvariable=self.st_codigo, height = 5)

        self.st_user = tk.StringVar(value="Higor_Lopes")
        self.tx_user = ttk.Combobox(self.fr_botoes,textvariable= self.st_user, width=15,height=5)
        self.tx_user["values"] = (usuarios)
        self.tx_user.bind("<<ComboboxSelected>>", self.combo_titulos)

        # Entries

        self.lista_entries = []

        # Botões

        self.bt_abre_eventos_acao = ttk.Button(self.fr_botoes, text="ACOES",
                                               command=lambda: self.abre_eventos(str(self.tx_user.get()),
                                                                            str(self.tx_codigo.get()).upper().replace(" ","_"),"ACOES"))

        self.bt_abre_eventos_FII = ttk.Button(self.fr_botoes, text="FII",
                                              command=lambda: self.abre_eventos(str(self.tx_user.get()),
                                                                                str(self.tx_codigo.get()).upper().replace(" ","_"),"FII"))

        self.bt_abre_eventos_RF = ttk.Button(self.fr_botoes, text="RENDA FIXA",
                                              command=lambda: self.abre_eventos(str(self.tx_user.get()),
                                                                                str(self.tx_codigo.get()).upper().replace(" ","_"),"RENDA_FIXA"))

        self.bt_abre_eventos_Dinheiro = ttk.Button(self.fr_botoes, text="DINHEIRO",
                                             command=lambda: self.abre_eventos(str(self.tx_user.get()),
                                                                               str(self.tx_codigo.get()).upper().replace(" ", "_"), "DINHEIRO"))

        # Layout

        self.lb_user.grid(row=0, column=0, sticky=tk.W, padx='5')
        self.lb_codigo.grid(row=0, column=1, sticky=tk.W, padx='5')

        self.tx_user.grid(row=1, column=0, sticky=tk.W, padx='5')
        self.tx_codigo.grid(row=1, column=1, sticky=tk.W, padx='5')

        self.bt_abre_eventos_acao.grid(row=1, column=2, padx='5')
        self.bt_abre_eventos_FII.grid(row=1, column=3, padx='5')
        self.bt_abre_eventos_RF.grid(row=1, column=4, padx='5')
        self.bt_abre_eventos_Dinheiro.grid(row=1, column=5, padx='5')

        return

    # --------------- FUNÇÕES AUXILIARES ----------

    def on_enter(self, event):

        self.lb_hover.configure(text=str(event.x_root) + "," + str(event.y_root))
        return

    def on_leave(self, event):
        self.lb_hover.configure(text="")
        return

    def combo_titulos(self, parametro_lixo):

        lista_de_acoes, lista_de_fii = ct.buscaRendaVar(self.tx_user.get())
        lista_renda_fixa = ct.buscaRendaFixa(self.tx_user.get())
        self.tx_codigo["values"] = ["--ACOES--"] + lista_de_acoes + ["---FII---"] + lista_de_fii + ["--RENDA_FIXA--"] + lista_renda_fixa

        # HABILITA O RECALCULO DOS TITULOS COM A MUDANCA DO USUARIO
        self.primeiro_clique = True

        return

    def _calc(self,parametro=""):

        print(parametro)
        ventana = tk.Tk()
        objeto = calculator(ventana)
        ventana.mainloop()

    def atualiza_scroll(self):

        self.canvas.create_window(0, 0, anchor=tk.NW, window=self.fr_principal)

        self.fr_principal.update_idletasks()

        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        return

    def atualiza_db(self):

        self.progress = ttk.Progressbar(self.fr_principal, orient="horizontal", length=900, mode='determinate')

        def atualiza():
            self.progress.place(relx=0.03,rely=0.99)
            self.progress.start()
            ct.atualiza_SELIC()
            ct.atualiza_ipca_mensal()

            # ATUALIZA O CDI CASO NECESSÁRIO
            try:
                ct.atualiza_cdi()
            except IndexError as e:
                print("O CDI já está atualizado. ERRO: " + str(e))

            # ATUALIZA ACOES
            # try:
            #     # BUSCA A ÚLTIMA COTACÁO DO DIA ANTERIOR. IMPEDE O ERRO DE FICAR ATUALIZANDO COM AS COTACOES DO DIA
            #     data_fim = dt.datetime.today() - dt.timedelta(days=1)
            #     data_fim = data_fim.replace(hour=0, minute=0, second=0, microsecond=0)
            #
            #     for usuario in usuarios:
            #         if usuario == "":
            #             pass
            #         else:
            #             lista_acoes, lista_fii = ct.buscaRendaVar(usuario)
            #             for acao in lista_acoes:
            #                 ct.busca_salva_cotacoes(acao, data_fim)
            #             for fii in lista_fii:
            #                 ct.busca_salva_cotacoes(fii, data_fim)
            # except:
            #     print("Ocorreu erro durante atualização das cotações no DB!")
            #     pass
            #
            # print("Atualizou todos os títulos.")
            self.progress.stop()
            self.progress.place_forget()

            return

        t3 = threading.Thread(target=atualiza)
        t3.daemon = True
        t3.start()

        return

    # --------------- FUNÇÕES PARA OS EVENTOS ----------

    def abre_eventos(self, usuario, codigo , tipo):

        if tipo == "DINHEIRO":
            gui = EventosGUI(usuario, codigo, tipo)
            while True:
                try:
                    gui.win.mainloop()
                    break
                except UnicodeDecodeError:
                    pass
        else:
            if self.tx_codigo.get() == "":
                messagebox.showerror("FALTA DE INFORMAÇÕES","O campo Código está em branco")
            else:
                gui = EventosGUI(usuario, codigo, tipo)
                while True:
                    try:
                        gui.win.mainloop()
                        break
                    except UnicodeDecodeError:
                        pass


        return

    # --------------- FUNÇÕES PARA A ABA TÍTULOS ----------

    def busca_titulos(self):

        self.progress = ttk.Progressbar(self.fr_principal, orient="horizontal", length=900, mode='determinate')

        def busca():

            self.progress.grid(row=2, column=1)
            self.progress.start()

            # APAGA OS CAMPOS DAS AÇÕES DO OUTRO USUÁRIO
            for entry in self.lista_entries:
                entry.destroy()

            self.carteira = ct.Carteira(usuario=str(self.tx_user.get()))
            self.acoes = self.carteira.acoes
            self.fii = self.carteira.fii
            self.rf = self.carteira.rf

            tk.Label(self.tab_dados, text="AÇÕES", font='Cambria 18').grid(row=3, column=2)

            j = 0
            for acao in self.acoes:

                if acao.qtd_atual > 0:

                    self.campos_nome = ["Qtd atual", "Preço médio (R$)",  "Cotação atual (R$)", "Valor atual (R$)",
                                        "Variação sem div. (%)", "Variação c/ div. (%)", "Variação Real (%)"]

                    self.campos_acao = [acao.qtd_atual, '$ {:,}'.format(round(acao.preco_medio_sem_div,2)),
                                        '$ {:,}'.format(round(acao.cotacao_atual,2)),
                                        '$ {:,}'.format(round(acao.valor_atual,2)),
                                        '{} %'.format(round(acao.RetornoSemDiv,2)),
                                        '{} %'.format(round(acao.RetornoComDiv,2)),
                                        '{} %'.format(round(acao.RetornoRealSemDiv,2))]

                    self.entries = []

                    # CRIA O RÓTULO DAS AÇÕES
                    label = tk.Label(self.tab_dados, text=acao.codigo)
                    self.lista_entries.append(label)
                    label.grid(row=4, column=j+1)

                    for i,campo in enumerate(self.campos_acao):
                        # Cria os labels dos campos da ação
                        tk.Label(self.tab_dados, text=self.campos_nome[i]).grid(row=i+5, column=0)
                        # Cria as entries
                        self.entries.append(tk.Entry(self.tab_dados, bg='white', width=15))
                        # Insere o valor dos campos
                        self.entries[i].insert('end', str(campo))
                        # Posiciona as entries
                        self.entries[i].grid(row=i+5, column=j+1)

                    j += 1

                    self.lista_entries += self.entries

            tk.Label(self.tab_dados, text="FII", font='Cambria 18').grid(row=16, column=2)

            j = 0
            for fii in self.fii:

                if fii.qtd_atual > 0:
                    self.campos_nome_fii = ["Qtd atual", "Preço médio (R$)", "Cotação atual (R$)", "Valor atual (R$)",
                                        "Variação sem div. (%)", "Variação c/ div. (%)", "Div. Yield mensal (%)"]

                    self.campos_fii = [fii.qtd_atual, '$ {:,}'.format(round(fii.preco_medio_sem_div, 2)),
                                        '$ {:,}'.format(round(fii.cotacao_atual, 2)),
                                        '$ {:,}'.format(round(fii.valor_atual, 2)),
                                        '{} %'.format(round(fii.RetornoSemDiv, 2)),
                                        '{} %'.format(round(fii.RetornoComDiv, 2)),
                                        '{} %'.format(round(fii.div_yield_mensal, 2))]

                    self.entries_fii = []

                    label2 = tk.Label(self.tab_dados, text=fii.codigo)
                    self.lista_entries.append(label2)
                    label2.grid(row=17, column=j + 1)

                    for i, campo in enumerate(self.campos_fii):
                        # Cria os labels dos campos da ação
                        tk.Label(self.tab_dados, text=self.campos_nome_fii[i]).grid(row=i + 19, column=0)
                        # Cria as entries
                        self.entries_fii.append(tk.Entry(self.tab_dados, bg='white', width=15))
                        # Insere o valor dos campos
                        self.entries_fii[i].insert('end', str(campo))
                        # Posiciona as entries
                        self.entries_fii[i].grid(row=i + 19, column=j + 1)

                    j += 1

                    self.lista_entries += self.entries_fii

            tk.Label(self.tab_dados, text="RF", font='Cambria 18').grid(row=26, column=2)

            j = 0
            for rf in self.rf:

                if rf.valor_investido > 0:

                    self.campos_nome_rf = ["Data de aplicação", "Data de Carência", "Data de Vencimento",
                                        "Valor aplicado (R$)", "Valor atual Bruto (R$)",
                                        "Valor Atual Líq. (R$)", "Taxa de Retorno liq. (%)"]

                    self.campos_rf = [rf.data_compra.strftime("%d / %m / %Y"),
                                        rf.data_carencia.strftime("%d / %m / %Y"),
                                        rf.data_vencimento.strftime("%d / %m / %Y"),
                                        '$ {:,}'.format(round(rf.valor_investido, 2)),
                                        '$ {:,}'.format(round(rf.valor_atual_bruto, 2)),
                                        '$ {:,}'.format(round(rf.valor_atual_liq, 2)),
                                        '{} %'.format(round(rf.taxa_atual_liq, 2))]

                    self.entries_rf = []

    #                tk.Label(self.fr_principal, text=rf.codigo).grid(row=27, column=1)
                    label3 = tk.Label(self.tab_dados, text=rf.codigo)
                    self.lista_entries.append(label3)
                    label3.grid(row=27, column=j + 1)


                    for i, campo in enumerate(self.campos_rf):
                        # Cria os labels dos campos da ação
                        tk.Label(self.tab_dados, text=self.campos_nome_rf[i]).grid(row=i + 28, column=0)
                        # Cria as entries
                        self.entries_rf.append(tk.Entry(self.tab_dados, bg='white', width=15))
                        # Insere o valor dos campos
                        self.entries_rf[i].insert('end', str(campo))
                        # Posiciona as entries
                        self.entries_rf[i].grid(row=i + 28, column=j+1)

                    j += 1

                    self.lista_entries += self.entries_rf

                self.atualiza_scroll()

            self.progress.stop()
            self.progress.grid_forget()

            return

        t4 = threading.Thread(target=busca)
        t4.daemon = True
        t4.start()

        return

    # --------------- FUNÇÕES PARA A ABA PESTE BLACK ----------

    def peste_black(self):

        self.fr_pb = ttk.LabelFrame(self.tab_peste_black, text="PROPORÇÕES DE CARTEIRA")

        self.fr_filtro = ttk.LabelFrame(self.tab_peste_black, text="CARTEIRA DE AÇÔES")

        self.fr_gr_pb = ttk.LabelFrame(self.tab_peste_black, text="GRÁFICOS PROPORÇÕES")

        Ano_atual = dt.date.today().year
        # LABELS
        self.lb_data_ent = ttk.Label(self.fr_pb, text="Data final:")
        self.lb_qtd_mes = ttk.Label(self.fr_pb, text="Qtd de meses anteriores:")

        # TEXTOS

        self.tx_saida = scrolledtext.ScrolledText(self.fr_pb, width=55, height=15.45, wrap=tk.WORD)

        self.tx_fund = scrolledtext.ScrolledText(self.fr_filtro, width=120, height=10, wrap=tk.WORD)

        self.data1 = tk.StringVar(value=dt.datetime.now().strftime('%d/%m/%Y'))
        self.tx_data_entrada = ttk.Entry(self.fr_pb, width=12, textvariable=self.data1)

        self.qtd_meses_dado = tk.IntVar(value=12)
        self.tx_qtd_meses = ttk.Entry(self.fr_pb, textvariable=self.qtd_meses_dado)

        self.tx_entry_pl = tk.StringVar(value=0)
        self.en_pl = ttk.Entry(self.fr_filtro, width=3, textvariable=self.tx_entry_pl, state='disabled')

        self.tx_entry_pvp = tk.StringVar(value=0)
        self.en_pvp = ttk.Entry(self.fr_filtro, width=3, textvariable=self.tx_entry_pvp, state='disabled')

        self.tx_entry_dy = tk.StringVar(value=0)
        self.en_dy = ttk.Entry(self.fr_filtro, width=3, textvariable=self.tx_entry_dy, state='disabled')

        self.tx_entry_p_ebit = tk.StringVar(value=0)
        self.en_p_ebit = ttk.Entry(self.fr_filtro, width=3, textvariable=self.tx_entry_p_ebit, state='disabled')

        self.tx_entry_liq = tk.StringVar(value=1000000)
        self.en_liq = ttk.Entry(self.fr_filtro, width=12, textvariable=self.tx_entry_liq, state='disabled')

        self.tx_entry_div = tk.StringVar(value=Ano_atual - 15)
        self.en_div = ttk.Entry(self.fr_filtro, width=4, textvariable=self.tx_entry_div, state='disabled')

        # BOTÕES

        self.bt_cal_pb = ttk.Button(self.fr_pb, text="...", command=self.chama_cal_pb)
        self.bt_cal_pb.config(width=1)

        self.bt_atualiza_db = ttk.Button(self.tab_peste_black, text="Atualiza Dados", command=self.atual_progress)

        self.bt_calc = ttk.Button(self.fr_pb, text="Calcular", command=self.calc_pb)

        self.check1 = tk.IntVar()
        self.bt_PL = tk.Checkbutton(self.fr_filtro, text="P/L > ", variable=self.check1, command=self.habilita_en_pl)

        self.check2 = tk.IntVar()
        self.bt_PVP = tk.Checkbutton(self.fr_filtro, text="P/VP > ", variable=self.check2, command=self.habilita_en_pvp)

        self.check3 = tk.IntVar()
        self.bt_DY = tk.Checkbutton(self.fr_filtro, text="DY > ", variable=self.check3, command=self.habilita_en_dy)

        self.check4 = tk.IntVar()
        self.bt_P_EBIT = tk.Checkbutton(self.fr_filtro, text="P/EBIT >= ", variable=self.check4,
                                        command=self.habilita_en_p_ebit)

        self.check5 = tk.IntVar()
        self.bt_LIQ = tk.Checkbutton(self.fr_filtro, text="Liq. 2m. >= ", variable=self.check5, command=
        self.habilita_en_liq)

        self.check6 = tk.IntVar()
        self.bt_DIV = tk.Checkbutton(self.fr_filtro, text="Div. desde:", variable=self.check6,
                                     command=self.habilita_en_div)

        self.bt_fund = ttk.Button(self.fr_filtro, text="Filtra ações", command=self.calc_fund)

        # LAYOUT

        # PRESENTES NO FRAME PRINCIPAL
        self.fr_filtro.grid(row=2, column=0, columnspan=6)
        self.fr_pb.grid(row=0, column=0)
        self.fr_gr_pb.grid(row=0, column=1)
        self.bt_atualiza_db.grid(row=8, column=0, sticky=tk.W, padx='20')

        # NO FRAME DO PESTE BLACK
        self.lb_data_ent.grid(row=1, column=0)
        self.lb_qtd_mes.grid(row=1, column=1, columnspan=2)
        self.tx_saida.grid(row=3, column=0, pady='5', padx='5', columnspan=4)
        self.tx_data_entrada.grid(row=2, column=0)
        self.bt_cal_pb.grid(row=2, column=1)
        self.bt_calc.grid(row=2, column=3)
        self.tx_qtd_meses.grid(row=2, column=2)

        # NO FRAME DOS FILTROS DE AÇÕES
        self.bt_PL.grid(row=0, column=0, padx='15', sticky=tk.W)
        self.en_pl.grid(row=0, column=1, sticky=tk.W)
        self.en_pvp.grid(row=0, column=3, sticky=tk.W)
        self.en_dy.grid(row=1, column=1, sticky=tk.W)
        self.en_p_ebit.grid(row=1, column=3, sticky=tk.W)
        self.bt_PVP.grid(row=0, column=2, padx='15', sticky=tk.W)
        self.bt_DY.grid(row=1, column=0, padx='15', sticky=tk.W)
        self.bt_P_EBIT.grid(row=1, column=2, padx='15', sticky=tk.W)
        self.tx_fund.grid(row=5, column=0, pady='5', padx='5', columnspan=5)
        self.bt_fund.grid(row=0, column=4)
        self.en_liq.grid(row=2, column=1, sticky=tk.W)
        self.bt_LIQ.grid(row=2, column=0, padx='15', sticky=tk.W)
        self.bt_DIV.grid(row=2, column=2, padx='15', sticky=tk.W)
        self.en_div.grid(row=2, column=3, sticky=tk.W)

        # GRÁFICO
        self.fig = Figure(figsize=(5, 3), facecolor='white')
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.canvas_2 = FigureCanvasTkAgg(self.fig, master=self.fr_gr_pb)
        self.canvas_2._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        return

    def chama_cal_pb(self):

        import sys
        app = QtWidgets.QApplication(sys.argv)
        Dialog = QtWidgets.QDialog()
        ui = Ui_Dialog()
        ui.setupUi(Dialog)
        Dialog.show()
        rsp = Dialog.exec_()
        if rsp == 1:
            date = ui.envia_data()

        data = str(date.toPyDate())
        data = data[-2:] + "/" + data[-5:-3] + "/" + data[:4]

        self.tx_data_entrada.delete(0, tk.END)
        self.tx_data_entrada.insert(0, data)

        return

    def calc_pb(self):
        self.progress = ttk.Progressbar(self.fr_pb, orient="horizontal", length=400, mode='determinate')

        def calcula():
            self.progress.grid(row=4, column=0, columnspan=3)
            self.progress.start()
            self.tx_saida.delete("1.0", tk.END)
            self.proporcoes, self.prop_graf ,self.datas = calc.itera_pb(dt.datetime.strptime(self.data1.get(), '%d/%m/%Y'),
                                                                   int(self.qtd_meses_dado.get()))
            for resultado in self.proporcoes:
                self.tx_saida.insert(tk.INSERT, resultado + "\n")
            self.progress.stop()
            self.progress.grid_forget()
            self.bt_calc['state'] = 'normal'

            # CRIA GRÁFICO DAS PROPORÇÕES

            self.ax.cla()
            for pos, resultado in enumerate(self.prop_graf):
                self.ax.barh(-pos, 100, color='red')
                self.ax.barh(-pos, resultado, color='blue')

            if len(self.datas)<= 18:
                self.ax.set_yticks(range(0,- len(self.datas),-1 ))
                self.ax.set_yticklabels(self.datas)

            else:
                self.ax.set_yticks(range(0,- len(self.datas),-1 ))
                self.ax.set_yticklabels(self.datas, fontsize='8')

            self.fig.tight_layout()
            #self.canvas_2.draw()
            #self.fr_gr_pb.update()

            return

        self.bt_calc['state'] = 'disabled'
        t1 = threading.Thread(target=calcula)
        t1.daemon = True
        t1.start()

        return

    def habilita_en_pl(self):
        if self.check1.get() == 1:
            self.en_pl.configure(state='enabled')
        else:
            self.en_pl.configure(state='disabled')
        return

    def habilita_en_pvp(self):
        if self.check2.get() == 1:
            self.en_pvp.configure(state='enabled')
        else:
            self.en_pvp.configure(state='disabled')
        return

    def habilita_en_dy(self):
        if self.check3.get() == 1:
            self.en_dy.configure(state='enabled')
        else:
            self.en_dy.configure(state='disabled')
        return

    def habilita_en_p_ebit(self):
        if self.check4.get() == 1:
            self.en_p_ebit.configure(state='enabled')
        else:
            self.en_p_ebit.configure(state='disabled')
        return

    def habilita_en_liq(self):
        if self.check5.get() == 1:
            self.en_liq.configure(state='enabled')
        else:
            self.en_liq.configure(state='disabled')
        return

    def habilita_en_div(self):
        if self.check6.get() == 1:
            self.en_div.configure(state='enabled')
        else:
            self.en_div.configure(state='disabled')

        return

    def calc_fund(self):
        self.tx_fund.delete("1.0", tk.END)
        self.fund = calc.le_fundamentus()
        if self.check1.get() == 1:
            self.fund = self.fund[(self.fund['P/L'] > int(self.en_pl.get()))]
            self.fund.sort_values(by='SOMA', inplace=True)
        # self.fund.reset_index(drop=True, inplace=True)
        if self.check2.get() == 1:
            self.fund = self.fund[(self.fund['P/VP'] > int(self.en_pvp.get()))]
            self.fund.sort_values(by='SOMA', inplace=True)
        # self.fund.reset_index(drop=True, inplace=True)
        if self.check3.get() == 1:
            self.fund = self.fund[(self.fund["DY"] > int(self.en_dy.get()))]
            self.fund.sort_values(by='SOMA', inplace=True)
        # self.fund.reset_index(drop=True, inplace=True)
        if self.check4.get() == 1:
            self.fund = self.fund[(self.fund["P/EBIT"] >= int(self.en_p_ebit.get()))]
            self.fund.sort_values(by="SOMA", inplace=True)
        # self.fund.reset_index(drop=True, inplace=True)
        if self.check5.get() == 1:
            self.fund = self.fund[(self.fund['Liq.2m.'] >= int(self.en_liq.get()))]
            self.fund.sort_values(by="SOMA", inplace=True)
        # self.fund.reset_index(drop=True, inplace=True)
        if self.check6.get() == 1:
            self.fund = self.fund[(self.fund['Ano Inicio Div.'] <= int(self.en_div.get()))]
            self.fund.sort_values(by="SOMA", inplace=True)
        # self.fund.reset_index(drop=True, inplace=True)

        self.tx_fund.tag_configure('center', justify='center')
        df = self.fund.loc[:,[ 'Nome', 'P/L(fin)_EV/EBIT', 'ROE(fin)_ROIC', 'DY', 'P/VP', 'Cresc.5a']]
        self.tx_fund.insert(tk.INSERT, df.to_string())
        # como faz pra colocar outros dados além do nome no resultado???? ,,,'Cresc.5a'

        return

    def atual_progress(self):
        self.progress = ttk.Progressbar(self.tab_peste_black, orient="horizontal", length=800, mode='determinate')

        def atualiza_db():
            self.progress.grid(row=4, column=0, columnspan=3, sticky =tk.W, padx='15')
            self.progress.start()
            self.tx_saida.delete("1.0", tk.END)
            # ATUALIZA IPCA E IBOV
            at_ipca_ibov = messagebox.askyesno('Confirma a atualização do DB', 'Deseja atualizar o IBOV e o IPCA ?')
            if at_ipca_ibov == True:
                db.atualiza_ipca_ibov(hj=dt.datetime.now())
            # ATUALIZA FUNDAMENTUS
            at_fund = messagebox.askyesno('Confirma a atualização do DB', 'Deseja atualizar os dados do FUNDAMENTUS ?')
            if at_fund == True:
                db.busca_fundamentus()
            # ATUALIZA HISTORICO DO FUNDAMENTUS
            at_hist_fund = messagebox.askyesno('Confirma a atualização do DB', 'Deseja atualizar HISTÓRICO DO FUNDAMENTUS ?')
            if at_hist_fund == True:
                db.atualiza_hist_fund()
            self.progress.stop()
            self.progress.grid_forget()
            self.bt_atualiza_db['state'] = 'normal'

        self.bt_atualiza_db['state'] = 'disabled'
        t2 = threading.Thread(target=atualiza_db)
        t2.daemon = True
        t2.start()

        return

    # --------------- FUNÇÕES PARA A ABA RESUMÃO ----------

    def exibe_resumao(self):

        self.saldo = float(str(self.tx_saldo.get()).replace(",","."))
        self.proventos = float(str(self.tx_proventos.get()).replace(",","."))
        self.porc_acoes = float(str(self.tx_porc_acoes.get()).replace(",","."))/100
        self.porc_fiis = float(str(self.tx_porc_fiis.get()).replace(",","."))/100
        self.porc_rf = float(str(self.tx_porc_rf.get()).replace(",","."))/100

        try:
            self.totais = ct.Resumao(usuario=self.tx_user.get(),saldo=self.saldo,proventos=self.proventos,porc_acoes=self.porc_acoes,
                                 porc_fiis=self.porc_fiis,porc_rf=self.porc_rf)
            self.dados_ir = ct.Calc_ir(usuario=self.tx_user.get())
        except ZeroDivisionError as z:
            messagebox.showerror("ERRO","O Usuário selecionado não possui títulos no banco de dados!")

        self.colunas = ["Carteira","Ações","FIIs","RF"]

        for k, nome in enumerate(self.colunas):

            if k == 0:

                tk.Label(self.tab_resumao, text=nome, font='Cambria 18').grid(row=2, column=0, columnspan=2)
                tk.Label(self.tab_resumao, text="Valores", font='Cambria 10').grid(row=3, column=0, columnspan=2)
                tk.Label(self.tab_resumao, text="Taxas Brutas", font='Cambria 10').grid(row=6, column=0, columnspan=2)
                tk.Label(self.tab_resumao, text="Imposto de Renda", font='Cambria 10').grid(row=12, column=0, columnspan=2)
                tk.Label(self.tab_resumao, text="Taxas Líquidas", font='Cambria 10').grid(row=17, column=0, columnspan=2)

                self.campos_nome_cart = ["Valor Aplicado (R$)", "Valor Atual (R$)"]
                self.campos_nome_cart1 = ["Taxa de Retorno (%)", "Retorno Mensal (%)","Retorno Anual (%)",
                                         "Inflação Acum. (%)", "Retorno Real (%)"]
                self.campos_nome_cart2 = ["IR Total Ações (R$)", "IR Total FIIs (R$)", "IR Total RFs (R$)",
                                          "IR Total Carteira (R$)"]
                self.campos_nome_cart3 = ["Retorno Liq. (%)", "Retorno Real Liq. (%)", "Retorno Mensal Liq. (%)", "Retorno Anual Liq. (%)"]

                self.campos_cart = ['$ {:,}'.format(round(self.totais.dinheiro_aplic, 2)),
                                    '$ {:,}'.format(round(self.totais.total_cart, 2))]
                self.campos_cart1 = ['{} %'.format(round(self.totais.taxa_ret_carteira, 2)),
                                    '{} %'.format(round(self.totais.ret_mensal_carteira, 2)),
                                    '{} %'.format(round(self.totais.ret_anual_carteira, 2)),
                                    '{} %'.format(round(self.totais.taxa_inflacao_dinheiro, 2)),
                                    '{} %'.format(round(self.totais.ret_real_carteira, 2))]
                self.campos_cart2 = ['$ {:,}'.format(round(self.dados_ir.soma_ir_total_acoes, 2)),
                                    '$ {:,}'.format(round(self.dados_ir.soma_ir_total_fiis, 2)),
                                    '$ {:,}'.format(round(self.dados_ir.soma_ir_total_rfs, 2)),
                                    '$ {:,}'.format(round(self.dados_ir.soma_ir_total_carteira, 2))]
                self.campos_cart3 = ['{} %'.format(round(self.totais.taxa_ret_cart_liq, 2)),
                                    '{} %'.format(round(self.totais.ret_real_cart_liq, 2)),
                                    '{} %'.format(round(self.totais.ret_mensal_cart_liq, 2)),
                                    '{} %'.format(round(self.totais.ret_anual_cart_liq, 2))]

                self.entries_cart = []

                for i, campo in enumerate(self.campos_cart):
                    # Cria os labels dos campos da ação
                    tk.Label(self.tab_resumao, text=self.campos_nome_cart[i]).grid(row=i + 4, column=0)
                    # Cria as entries
                    self.entries_cart.append(tk.Entry(self.tab_resumao, bg='white', width=15))
                    # Insere o valor dos campos
                    self.entries_cart[i].insert('end', str(campo))
                    # Posiciona as entries
                    self.entries_cart[i].grid(row=i + 4, column=1)

                self.entries_cart1 = []

                for i, campo in enumerate(self.campos_cart1):
                    # Cria os labels dos campos da ação
                    tk.Label(self.tab_resumao, text=self.campos_nome_cart1[i]).grid(row=i + 7, column=0)
                    # Cria as entries
                    self.entries_cart1.append(tk.Entry(self.tab_resumao, bg='white', width=15))
                    # Insere o valor dos campos
                    self.entries_cart1[i].insert('end', str(campo))
                    # Posiciona as entries
                    self.entries_cart1[i].grid(row=i + 7, column=1)

                self.entries_cart2 = []

                for i, campo in enumerate(self.campos_cart2):
                    # Cria os labels dos campos da ação
                    tk.Label(self.tab_resumao, text=self.campos_nome_cart2[i]).grid(row=i + 13, column=0)
                    # Cria as entries
                    self.entries_cart2.append(tk.Entry(self.tab_resumao, bg='white', width=15))
                    # Insere o valor dos campos
                    self.entries_cart2[i].insert('end', str(campo))
                    # Posiciona as entries
                    self.entries_cart2[i].grid(row=i + 13, column=1)

                self.entries_cart3 = []

                for i, campo in enumerate(self.campos_cart3):
                    # Cria os labels dos campos da ação
                    tk.Label(self.tab_resumao, text=self.campos_nome_cart3[i]).grid(row=i + 18, column=0)
                    # Cria as entries
                    self.entries_cart3.append(tk.Entry(self.tab_resumao, bg='white', width=15))
                    # Insere o valor dos campos
                    self.entries_cart3[i].insert('end', str(campo))
                    # Posiciona as entries
                    self.entries_cart3[i].grid(row=i + 18, column=1)

            elif k == 1:

                tk.Label(self.tab_resumao, text=nome, font='Cambria 18').grid(row=2, column=2, columnspan=2)
                tk.Label(self.tab_resumao, text="Desvios Indv.:", font='Cambria 10').grid(row=8, column=2)
                tk.Label(self.tab_resumao, text="R$", font='Cambria 10').grid(row=8, column=3)

                self.campos_nome_cart = ["Custo Aquisição (R$)", "Valor Atual (R$)", "Taxa Retorno (%)",
                                       "Meta Carteira (%)", "Desvio Carteira (%)"]

                self.campos_cart = ['$ {:,}'.format(round(self.totais.custo_total_acoes, 2)),
                                    '$ {:,}'.format(round(self.totais.valor_total_acoes, 2)),
                                    '{} %'.format(round(self.totais.taxa_ret_acoes, 2)),
                                    '$ {:,}'.format(round(self.totais.meta_acoes, 2)),
                                    '$ {:,}'.format(round(self.totais.desvio_acoes, 2))]

                self.entries_cart = []

                for i, campo in enumerate(self.campos_cart):
                    # Cria os labels dos campos da ação
                    tk.Label(self.tab_resumao, text=self.campos_nome_cart[i]).grid(row=i + 3, column=2)
                    # Cria as entries
                    self.entries_cart.append(tk.Entry(self.tab_resumao, bg='white', width=15))
                    # Insere o valor dos campos
                    self.entries_cart[i].insert('end', str(campo))
                    # Posiciona as entries
                    self.entries_cart[i].grid(row=i + 3, column=3)

                self.entries_desvios_acoes = []

                for i, campo in enumerate(self.totais.desvio_ind_acoes):
                    # Cria os labels dos campos da ação
                    tk.Label(self.tab_resumao, text=self.totais.lista_acoes[i]).grid(row=i + 9, column=2)
                    # Cria as entries
                    self.entries_desvios_acoes.append(tk.Entry(self.tab_resumao, bg='white', width=15))
                    # Insere o valor dos campos
                    self.entries_desvios_acoes[i].insert('end', str(campo))
                    # Posiciona as entries
                    self.entries_desvios_acoes[i].grid(row=i + 9, column=3)

            elif k == 2:

                tk.Label(self.tab_resumao, text=nome, font='Cambria 18').grid(row=2, column=4, columnspan=2)
                tk.Label(self.tab_resumao, text="Desvios Indv.:", font='Cambria 10').grid(row=8, column=4)
                tk.Label(self.tab_resumao, text="R$", font='Cambria 10').grid(row=8, column=5)

                self.campos_nome_cart = ["Custo Aquisição (R$)", "Valor Atual (R$)", "Taxa Retorno (%)",
                                         "Meta Carteira (%)", "Desvio Carteira (%)"]

                self.campos_cart = ['$ {:,}'.format(round(self.totais.custo_total_fiis, 2)),
                                    '$ {:,}'.format(round(self.totais.valor_total_fiis, 2)),
                                    '{} %'.format(round(self.totais.taxa_ret_fiis, 2)),
                                    '$ {:,}'.format(round(self.totais.meta_fiis, 2)),
                                    '$ {:,}'.format(round(self.totais.desvio_fiis, 2))]

                self.entries_cart = []

                for i, campo in enumerate(self.campos_cart):
                    # Cria os labels dos campos da ação
                    tk.Label(self.tab_resumao, text=self.campos_nome_cart[i]).grid(row=i + 3, column=4)
                    # Cria as entries
                    self.entries_cart.append(tk.Entry(self.tab_resumao, bg='white', width=15))
                    # Insere o valor dos campos
                    self.entries_cart[i].insert('end', str(campo))
                    # Posiciona as entries
                    self.entries_cart[i].grid(row=i + 3, column=5)

                self.entries_desvios_fiis = []

                for i, campo in enumerate(self.totais.desvio_ind_fiis):
                    # Cria os labels dos campos da ação
                    tk.Label(self.tab_resumao, text=self.totais.lista_fiis[i]).grid(row=i + 9, column=4)
                    # Cria as entries
                    self.entries_desvios_fiis.append(tk.Entry(self.tab_resumao, bg='white', width=15))
                    # Insere o valor dos campos
                    self.entries_desvios_fiis[i].insert('end', str(campo))
                    # Posiciona as entries
                    self.entries_desvios_fiis[i].grid(row=i + 9, column=5)




            elif k == 3:

                tk.Label(self.tab_resumao, text=nome, font='Cambria 18').grid(row=2, column=6, columnspan=3)
                tk.Label(self.tab_resumao, text="Liquidez:", font='Cambria 10').grid(row=8, column=6)
                tk.Label(self.tab_resumao, text="R$", font='Cambria 10').grid(row=8, column=7)
                tk.Label(self.tab_resumao, text="%", font='Cambria 10').grid(row=8, column=8)

                self.campos_nome_cart = ["Custo Aquisição (R$)", "Valor Atual (R$)", "Taxa Retorno (%)",
                                         "Meta Carteira (%)", "Desvio Carteira (%)"]

                self.campos_cart = ['$ {:,}'.format(round(self.totais.custo_total_rfs, 2)),
                                    '$ {:,}'.format(round(self.totais.valor_total_rfs, 2)),
                                    '{} %'.format(round(self.totais.taxa_ret_rf, 2)),
                                    '$ {:,}'.format(round(self.totais.meta_rf, 2)),
                                    '$ {:,}'.format(round(self.totais.desvio_rf, 2))]

                self.campos_nome_liq = ["Imediata", "até 30 dias", "até 60 dias", "até 90 dias", "até 180 dias", "até 360 dias", "> 360 dias"]

                self.campos_liq = ['$ {:,}'.format(round(self.totais.liq_imediata, 2)),
                                    '$ {:,}'.format(round(self.totais.liq_30, 2)),
                                    '$ {:,}'.format(round(self.totais.liq_60, 2)),
                                    '$ {:,}'.format(round(self.totais.liq_90, 2)),
                                    '$ {:,}'.format(round(self.totais.liq_180, 2)),
                                    '$ {:,}'.format(round(self.totais.liq_360, 2)),
                                    '$ {:,}'.format(round(self.totais.liq_maior_360, 2))]

                self.campos_porc_liq = ['{} %'.format(round(self.totais.porc_liq_imediata, 2)),
                                    '{} %'.format(round(self.totais.porc_liq_30, 2)),
                                    '{} %'.format(round(self.totais.porc_liq_60, 2)),
                                    '{} %'.format(round(self.totais.porc_liq_90, 2)),
                                    '{} %'.format(round(self.totais.porc_liq_180, 2)),
                                    '{} %'.format(round(self.totais.porc_liq_360, 2)),
                                    '{} %'.format(round(self.totais.porc_liq_maior_360, 2))]

                self.entries_cart = []
                self.entries_liq =[]
                self.entries_porc_liq = []

                for i, campo in enumerate(self.campos_cart):
                    # Cria os labels dos campos da ação
                    tk.Label(self.tab_resumao, text=self.campos_nome_cart[i]).grid(row=i + 3, column=6)
                    # Cria as entries
                    self.entries_cart.append(tk.Entry(self.tab_resumao, bg='white', width=15))
                    # Insere o valor dos campos
                    self.entries_cart[i].insert('end', str(campo))
                    # Posiciona as entries
                    self.entries_cart[i].grid(row=i + 3, column=7)

                for i, campo in enumerate(self.campos_liq):
                    # Cria os labels dos campos da ação
                    tk.Label(self.tab_resumao, text=self.campos_nome_liq[i]).grid(row=i + 9, column=6)
                    # Cria as entries
                    self.entries_liq.append(tk.Entry(self.tab_resumao, bg='white', width=15))
                    # Insere o valor dos campos
                    self.entries_liq[i].insert('end', str(campo))
                    # Posiciona as entries
                    self.entries_liq[i].grid(row=i + 9, column=7)


                for i, campo in enumerate(self.campos_porc_liq):
                    # Cria as entries
                    self.entries_porc_liq.append(tk.Entry(self.tab_resumao, bg='white', width=7))
                    # Insere o valor dos campos
                    self.entries_porc_liq[i].insert('end', str(campo))
                    # Posiciona as entries
                    self.entries_porc_liq[i].grid(row=i + 9, column=8)


        self.atualiza_scroll()

        return

    def widgets_resumao(self):

        # Labels

        self.lb_saldo = ttk.Label(self.tab_resumao, text="Saldo em Conta").grid(row=0, column=0, padx='5')
        self.lb_proventos = ttk.Label(self.tab_resumao, text="Proventos Projetados").grid(row=1, column=0, padx='5')
        self.lb_porc_acoes = ttk.Label(self.tab_resumao, text="% Ações").grid(row=0, column=3, padx='5')
        self.lb_porc_fiis = ttk.Label(self.tab_resumao, text="% FIIs").grid(row=0, column=5, padx='5')
        self.lb_porc_rf = ttk.Label(self.tab_resumao, text="% RF").grid(row=0, column=7, padx='5')

        # Textos

        self.st_saldo = tk.StringVar(value=0)
        self.tx_saldo = ttk.Entry(self.tab_resumao, width=10, textvariable=self.st_saldo)

        self.st_proventos = tk.StringVar(value=0)
        self.tx_proventos = ttk.Entry(self.tab_resumao, width=10, textvariable=self.st_proventos)

        self.st_porc_acoes= tk.StringVar(value=0)
        self.tx_porc_acoes = ttk.Entry(self.tab_resumao, width=10, textvariable=self.st_porc_acoes)

        self.st_porc_fiis= tk.StringVar(value=0)
        self.tx_porc_fiis = ttk.Entry(self.tab_resumao, width=10, textvariable=self.st_porc_fiis)

        self.st_porc_rf= tk.StringVar(value=0)
        self.tx_porc_rf = ttk.Entry(self.tab_resumao, width=10, textvariable=self.st_porc_rf)

        # Layout

        self.tx_saldo.grid(row=0, column=1, padx='5')
        self.tx_proventos.grid(row=1, column=1, padx='5')
        self.tx_porc_acoes.grid(row=1, column=3, padx='5')
        self.tx_porc_fiis.grid(row=1, column=5, padx='5')
        self.tx_porc_rf.grid(row=1, column=7, padx='5')

        # Botões

        self.bt_resumao = ttk.Button(self.tab_resumao, text="Exibe Resumão",
                                     command=lambda: self.exibe_resumao()).grid(row=0, column=8, padx='10', rowspan=3)


    # --------------- FUNÇÕES PARA A ABA GRÁFICOS ----------

    def graficos(self):

        #LABEL FRAMES
        self.lf_select = ttk.LabelFrame(self.tab_graf, text="SELEÇÃO DA AÇÃO")
        self.lf_textos = ttk.LabelFrame(self.tab_graf, text="INSTRUÇÕES DE USO")

        #TEXTOS
        self.instru = """
        - O programa lê arquivos de extensão .db na pasta "base", que contém o histórico de cotações da Bovespa;\n
        - Para atualizar a base de dados, deve-se baixar o arquivo .zip do ano atual no site da Bovespa, extraí-lo
        na pasta "base" e rodar o arquivos "script_atualiza_base.py";\n
        - Alternativamente, é possível utilizar o Yahoo Finance para baixar os dados, marcando o checkbox "yahoo".
        Essa opção demanda conexão com a internet.
        """
        self.lb_select1 = ttk.Label(self.lf_select, text="Selecione a ação:")
        self.lb_select2 = ttk.Label(self.lf_select, text="Data inicial:")
        self.lb_select3 = ttk.Label(self.lf_select, text="Data final:")
        self.lb_select4 = ttk.Label(self.lf_select, text="Médias móveis exponenciais:")
        self.lb_select5 = ttk.Label(self.lf_textos, text=self.instru)

        #COMBOBOX
        self.emp = pd.read_csv('empresas.csv')
        self.lista_emp = sorted(self.emp['acao'].tolist())
        self.cb_acoes = ttk.Combobox(self.lf_select,values=self.lista_emp, width=15,height=5)

        #ENTRYS
        self.st_data1 = tk.StringVar(value='2015-1-1')
        self.now = dt.datetime.now()
        self.st_data2 = tk.StringVar(value=str(self.now.year)+'-'+str(self.now.month)+'-'+str(self.now.day))
        self.en_data1 = ttk.Entry(self.lf_select, width=10, textvariable=self.st_data1)
        self.en_data2 = ttk.Entry(self.lf_select, width=10, textvariable=self.st_data2)

        #BOTÃO
        self.bt_plot = ttk.Button(self.lf_select, text="Gerar gráfico", command=self.calc_graf)
        self.bt_cal_data1 = ttk.Button(self.lf_select, text="...", command=self.chama_cal_graf1)
        self.bt_cal_data1.config(width=1)
        self.bt_cal_data2 = ttk.Button(self.lf_select, text="...", command=self.chama_cal_graf2)
        self.bt_cal_data2.config(width=1)

        #CHECK BUTTON
        self.check_mm90 = tk.IntVar()
        self.bt_mm90 = tk.Checkbutton(self.lf_select, text="90 dias", variable=self.check_mm90)
        self.check_mm180 = tk.IntVar()
        self.bt_mm180 = tk.Checkbutton(self.lf_select, text="180 dias", variable=self.check_mm180)
        self.check_mm360 = tk.IntVar()
        self.bt_mm360 = tk.Checkbutton(self.lf_select, text="360 dias", variable=self.check_mm360)
        
        self.check_yahoo = tk.IntVar()
        self.bt_yahoo = tk.Checkbutton(self.lf_select, text="yahoo", variable=self.check_yahoo)

        #LAYOUT
        self.lf_select.pack(fill=tk.BOTH)#grid(row=0, column=0, padx='5', pady='5')
        self.lf_textos.pack(fill=tk.BOTH)#grid(row=1, column=0, padx='5', pady='5')

        self.lb_select1.grid(row=0, column=0, padx='5')
        self.cb_acoes.grid(row=1, column=0, padx='5', pady='5')
        self.lb_select2.grid(row=0, column=1, padx='5')
        self.lb_select3.grid(row=0, column=3, padx='5')
        self.en_data1.grid(row=1, column=1, padx='5', pady='5')
        self.bt_cal_data1.grid(row=1, column=2)
        self.en_data2.grid(row=1, column=3, padx='5', pady='5')
        self.bt_cal_data2.grid(row=1, column=4)
        self.bt_plot.grid(row=4, column=4, padx='5', pady='5')
        self.lb_select4.grid(row=2, column=0, padx='5')
        self.bt_mm90.grid(row=3, column=0, padx='5')
        self.bt_mm180.grid(row=3, column=1, padx='5')
        self.bt_mm360.grid(row=3, column=3, padx='5')
        self.bt_yahoo.grid(row=0, column=4, padx='5')
        
        self.lb_select5.grid(row=0, column=0, padx='5')

    def chama_cal_graf1(self):

        import sys
        app = QtWidgets.QApplication(sys.argv)
        Dialog = QtWidgets.QDialog()
        ui = Ui_Dialog()
        ui.setupUi(Dialog)
        Dialog.show()
        rsp = Dialog.exec_()
        if rsp == 1:
            date = ui.envia_data()

        data = str(date.toPyDate())

        self.en_data1.delete(0, tk.END)
        self.en_data1.insert(0, data)

        return

    def chama_cal_graf2(self):

        import sys
        app = QtWidgets.QApplication(sys.argv)
        Dialog = QtWidgets.QDialog()
        ui = Ui_Dialog()
        ui.setupUi(Dialog)
        Dialog.show()
        rsp = Dialog.exec_()
        if rsp == 1:
            date = ui.envia_data()

        data = str(date.toPyDate())

        self.en_data2.delete(0, tk.END)
        self.en_data2.insert(0, data)

        return

    def calc_graf(self):
        
        if self.check_yahoo.get() == 0:
            #Cria dicionário que irá receber os dataframes com anos nas keys
            self.dic_base = {}
            #Loop através dos arquivos com extensão .db na pasta base
            for filename in os.listdir(os.getcwd()+'/base'):
                if filename.endswith(".db"):
                    self.con = sql.connect(os.getcwd()+'\\base\\'+filename)
                    #ljust completa uma string com espaços em branco, para bater com os 12 caracteres do .db
                    self.df_temp = pd.read_sql_query("SELECT * FROM hist_bovespa WHERE CODNEG = '"+self.cb_acoes.get().ljust(12)+"'", self.con)
                    #Adiciona o banco de dados do ano em questão ao dicionário, com o ano como a key
                    self.dic_base[filename[8:12]] = (self.df_temp)
                    self.con.commit()
                    self.con.close()
            #A linha abaixo faz a concatenação de todos os DataFrames
            self.df_base = pd.concat(list(self.dic_base.values()))
            #Coverte a coluna DATA em datetime
            self.df_base['DATA'] = pd.to_datetime(self.df_base['DATA'], format='%Y-%m-%d %H:%M:%S')

        if self.check_yahoo.get() == 1:
            #Baixa os dados e associa ao DataFrame df
            self.df_base = data.get_data_yahoo(self.cb_acoes.get()+'.SA',
                                    start=self.en_data1.get(),
                                    end=self.en_data2.get())
            self.df_base['DATA'] = self.df_base.index
            self.df_base.rename(columns={'Close':'PREULT'}, inplace=True)
        
        #Médias móveis exponenciais
        self.df_base['m90_rol'] = self.df_base['PREULT'].ewm(span=90, adjust=False).mean()
        self.df_base['m180_rol'] = self.df_base['PREULT'].ewm(span=180, adjust=False).mean()
        self.df_base['m360_rol'] = self.df_base['PREULT'].ewm(span=360, adjust=False).mean()
        
        self.df_base = self.df_base[(self.df_base['DATA'] >= self.en_data1.get()) & (self.df_base['DATA'] <= self.en_data2.get())]
        
        plt.plot(self.df_base['DATA'], self.df_base['PREULT'])
        plt.grid()
        plt.show()
        
        if (self.check_mm90.get()) == 1:
            plt.plot(self.df_base['DATA'], self.df_base['m90_rol'])
        if (self.check_mm180.get()) == 1:
            plt.plot(self.df_base['DATA'], self.df_base['m180_rol'])
        if (self.check_mm360.get()) == 1:
            plt.plot(self.df_base['DATA'], self.df_base['m360_rol'])

        self.atualiza_scroll()

    # --------------- FUNÇÕES PARA A ABA CALCULADORA DE IR ----------

    def widgets_calc_ir(self):

        self.dados_ir = ct.Calc_ir(usuario=self.tx_user.get())

        self.colunas0 = ["Ações", "FIIs", "IR TOTAL"]
        tk.Label(self.tab_calc_ir, text=self.colunas0[0], font='Cambria 14').grid(row=0, column=1, columnspan =4)
        tk.Label(self.tab_calc_ir, text="||", font='Cambria 12').grid(row=0, column=5)
        tk.Label(self.tab_calc_ir, text=self.colunas0[1], font='Cambria 14').grid(row=0, column=6, columnspan=3)
        tk.Label(self.tab_calc_ir, text="||", font='Cambria 12').grid(row=0, column=9)
        tk.Label(self.tab_calc_ir, text=self.colunas0[2], font='Cambria 14').grid(row=0, column=10, columnspan=3)

        self.colunas1 = ["Vendas","Lucro/Preju.","Preju. acum","IR Ações","||","Lucro/Preju.","Preju. acum","IR FIIs"] + \
                        ["||","IR devido","Vencimento"]
        for i, n in enumerate(self.colunas1):
            tk.Label(self.tab_calc_ir, text=self.colunas1[i], font='Cambria 11').grid(row=1, column=i+1)

        self.meses = ["JAN","FEV","MAR","ABR","MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ"]
        self.linhas = [self.meses[i]+"/{0}".format(dt.datetime.today().year -1) for i in range(12)] + \
                      [self.meses[i]+"/{0}".format(dt.datetime.today().year) for i in range(dt.datetime.today().month)]

        self.datas_temp = ["1/{0}/{1}".format(mes, dt.datetime.today().year - 1) for mes in range(1, 13)] + \
                          ["1/{0}/{1}".format(mes, dt.datetime.today().year) for mes in
                           range(1, dt.datetime.today().month + 1)]
        self.datas_temp = [dt.datetime.strptime(i, "%d/%m/%Y") for i in self.datas_temp]

        self.lista_data_venc = []
        for i, data in enumerate(self.datas_temp):
            self.data_venc = pd.date_range(data, periods=2, freq='BM').strftime("%d/%m/%Y")
            self.data_venc = str(self.data_venc[-1])[:10]
            self.lista_data_venc += [self.data_venc]

        for i in range(len(self.linhas)):

            tk.Label(self.tab_calc_ir, text=self.linhas[i]).grid(row=i+2, column=0)

            self.campos_ir_acoes = ['$ {:,}'.format(round(self.dados_ir.lista_vendas[i], 2)),
                              '$ {:,}'.format(round(self.dados_ir.lista_res_mes_acoes[i], 2)),
                              '$ {:,}'.format(round(self.dados_ir.lista_preju_acoes[i], 2)),
                              '$ {:,}'.format(round(self.dados_ir.lista_ir_acoes[i], 2))]

            self.entries_ir_acoes = []

            for j, campo in enumerate(self.campos_ir_acoes):
                # Cria as entries
                self.entries_ir_acoes.append(tk.Entry(self.tab_calc_ir, bg='white', width=12))
                # Insere o valor dos campos
                self.entries_ir_acoes[j].insert('end', str(campo))
                # Posiciona as entries
                self.entries_ir_acoes[j].grid(row=i+2, column=j+1)

            tk.Label(self.tab_calc_ir, text="||").grid(row=i + 2, column=5)

            self.campos_ir_fiis = ['$ {:,}'.format(round(self.dados_ir.lista_res_mes_fiis[i], 2)),
                              '$ {:,}'.format(round(self.dados_ir.lista_preju_fiis[i], 2)),
                              '$ {:,}'.format(round(self.dados_ir.lista_ir_fiis[i], 2))]

            self.entries_ir_fiis = []

            for j, campo in enumerate(self.campos_ir_fiis):
                # Cria as entries
                self.entries_ir_fiis.append(tk.Entry(self.tab_calc_ir, bg='white', width=12))
                # Insere o valor dos campos
                self.entries_ir_fiis[j].insert('end', str(campo))
                # Posiciona as entries
                self.entries_ir_fiis[j].grid(row=i+2, column=j+6)

            tk.Label(self.tab_calc_ir, text="||").grid(row=i + 2, column=9)

            self.campos_ir_total = ['$ {:,}'.format(round(self.dados_ir.lista_ir_total[i], 2))]

            self.entries_ir_total = []

            for j, campo in enumerate(self.campos_ir_total):
                # Cria as entries
                self.entries_ir_total.append(tk.Entry(self.tab_calc_ir, bg='white', width=12))
                # Insere o valor dos campos
                self.entries_ir_total[j].insert('end', str(campo))
                # Posiciona as entries
                self.entries_ir_total[j].grid(row=i + 2, column=j + 10)


            self.campos_data_venc = ['{0}'.format(self.lista_data_venc[i])]

            self.entries_data_venc = []

            if self.dados_ir.lista_ir_total[i] > 0:
                for j, campo in enumerate(self.campos_data_venc):
                    # Cria as entries
                    self.entries_data_venc.append(tk.Entry(self.tab_calc_ir, bg='white', width=12))
                    # Insere o valor dos campos
                    self.entries_data_venc[j].insert('end', str(campo))
                    # Posiciona as entries
                    self.entries_data_venc[j].grid(row=i + 2, column=j + 11)


        self.atualiza_scroll()

        return
        
if __name__ == "__main__":

    gui = MainGUI()
    while True:
        try:
            gui.win.mainloop()
            break
        except UnicodeDecodeError:
            pass
