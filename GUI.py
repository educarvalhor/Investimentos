#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
__author__ = "Eduardo Rosa", "Higor_Lopes", "Marcelo Bulhões"
__version__ = "1.0.1"
"""

# PRÓXIMAS IMPLEMENTAÇÕES

# todo Gráfico de Evolução da Carteira
# todo Back-test de estratégias
# todo Erro de atualização no notebook do peste
# todo Erro do gráfico do peste black no pc do Marselhesa
# todo Aba Resumão
# todo Calculadora de IR
# todo Nota de Oportunidade
# todo Gráfico da aba gráficos plota um abaixo do outro
# todo Criar Arquivo de resumo para o GitHub

import threading
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import datetime
import numpy as np

from pandas_datareader import data
import fix_yahoo_finance as yf
yf.pdr_override() 

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import Calc_pb_v2 as calc
import DB_pb_v2 as db

import Carteira as ct
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Canvas
import datetime as dt
from Carteira import timethis

usuarios = ["Higor_Lopes", "Eduardo_Rosa", "Marcelo_Bulhoes" ]


class AutoScrollbar(ttk.Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        ttk.Scrollbar.set(self, lo, hi)
        return


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

        # Layout

        self.lb_tipo.grid(row=0, column=0, sticky=tk.W, padx='5')
        self.lb_valor.grid(row=0, column=1,  padx='5')
        self.lb_qtd.grid(row=0, column=2, padx='5')
        self.lb_corr.grid(row=0, column=3, padx='5')
        self.lb_data.grid(row=0, column=4, sticky=tk.W,  padx='5')

        self.bt_salva_evento.grid(row=1, column=5, padx='10')

        self.tx_tipo.grid(row=1, column=0, sticky=tk.W, padx='5')
        self.tx_valor.grid(row=1, column=1,  padx='5')
        self.tx_qtd.grid(row=1, column=2, padx='5')
        self.tx_corr.grid(row=1, column=3, sticky=tk.W, padx='5')
        self.tx_data.grid(row=1, column=4, sticky=tk.W, padx='5')

        self.tx_log.grid(row=2, column=0, columnspan=6, sticky=tk.W, padx='10')

        self.tx_id.grid(row=3, column=0)

        self.bt_apaga_evento.grid(row=3, column=1, sticky=tk.W, padx='20')

        self.bt_mostra_evento.grid(row=3, column=2, sticky=tk.W, padx='20')

        self.tx_eventos.grid(row=4,column=0,columnspan=6, sticky=tk.W, rowspan=11,padx='10')
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

        # Layout

        self.lb_tipo.grid(row=0, column=0, sticky=tk.W, padx='5')
        self.lb_data.grid(row=0, column=1, padx='5')
        self.lb_valor.grid(row=0, column=2, padx='5')

        self.bt_salva_evento.grid(row=1, column=3, padx='10')

        self.tx_tipo.grid(row=1, column=0, sticky=tk.W, padx='5')
        self.tx_data.grid(row=1, column=1, padx='5')
        self.tx_valor.grid(row=1, column=2, padx='5')

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

        # Layout

        self.lb_tipo.grid(row=0, column=0, padx='1')
        self.lb_tipo_aplicacao.grid(row=0, column=1, padx='1')
        self.lb_tipo_taxa.grid(row=0, column=2, padx='1')
        self.lb_valor_taxa.grid(row=0, column=3, padx='1')
        self.lb_valor.grid(row=0, column=4, padx='1')
        self.lb_qtd.grid(row=2, column=0, padx='1')
        self.lb_data_carencia.grid(row=2, column=1, padx='1')
        self.lb_data_vencimento.grid(row=2, column=2, padx='1')
        self.lb_corr.grid(row=2, column=3, padx='1')
        self.lb_data.grid(row=2, column=4, padx='1')


        self.bt_salva_evento.grid(row=1, column=9, padx='2')

        self.tx_tipo.grid(row=1, column=0, padx='1')
        self.tx_tipo_aplicacao.grid(row=1, column=1, padx='1')
        self.tx_tipo_taxa.grid(row=1, column=2, padx='1')
        self.tx_valor_taxa.grid(row=1, column=3, padx='1')
        self.tx_valor.grid(row=1, column=4, padx='1')
        self.tx_qtd.grid(row=3, column=0, padx='1')
        self.tx_data_carencia.grid(row=3, column=1, padx='1')
        self.tx_data_vencimento.grid(row=3, column=2, padx='1')
        self.tx_corr.grid(row=3, column=3, padx='1')
        self.tx_data.grid(row=3, column=4, padx='1')


        self.tx_log.grid(row=4, column=0, columnspan=10, padx='4', sticky=tk.W)

        self.tx_id.grid(row=5, column=0)

        self.bt_apaga_evento.grid(row=5, column=1, padx='4')

        self.bt_mostra_evento.grid(row=5, column=2, padx='4')

        self.tx_eventos.grid(row=6, column=0, columnspan=11, rowspan=11, padx='4', sticky=tk.W)

        return

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
        # todo Caso reutilizemos esta estrutura de Eventos para Renda fixa é preciso mudar algumas o try abaixo
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
        self.win.geometry('990x805')
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

        # Notebook

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


        self.canvas.create_window(0, 0, anchor=tk.NW, window=self.fr_principal)
        self.fr_principal.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        #FUNÇÃO PARA ABA RESUMAO
        self.widgets_resumao()

        self.atualiza_db()

        return

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
        self.tx_data_entrada = ttk.Entry(self.fr_pb, textvariable=self.data1)

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
        self.lb_qtd_mes.grid(row=1, column=1)
        self.tx_saida.grid(row=3, column=0, pady='5', padx='5', columnspan=3)
        self.tx_data_entrada.grid(row=2, column=0)
        self.bt_calc.grid(row=2, column=2)
        self.tx_qtd_meses.grid(row=2, column=1)

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
            self.progress.stop()
            self.progress.grid_forget()
            self.bt_atualiza_db['state'] = 'normal'

        self.bt_atualiza_db['state'] = 'disabled'
        t2 = threading.Thread(target=atualiza_db)
        t2.daemon = True
        t2.start()

        return

    def clica_notebook(self, event):

        clicked_tab = self.note.tk.call(self.note._w, "identify", "tab", event.x, event.y)

        active_tab = self.note.index(self.note.select())

        if clicked_tab == 1 & self.primeiro_clique == True:
            self.busca_titulos()
            self.primeiro_clique = False

        return

    def atualiza_db(self):

        self.progress = ttk.Progressbar(self.fr_principal, orient="horizontal", length=900, mode='determinate')

        def atualiza():
            self.progress.place(relx=0.03,rely=0.98)
            self.progress.start()
            ct.atualiza_SELIC()
            ct.atualiza_ipca_mensal()

            # ATUALIZA O CDI CASO NECESSÁRIO
            try:
                ct.atualiza_cdi()
            except IndexError as e:
                print("O CDI já está atualizado. ERRO: " + str(e))

            # ATUALIZA ACOES

            # BUSCA A ÚLTIMA COTACÁO DO DIA ANTERIOR. IMPEDE O ERRO DE FICAR ATUALIZANDO COM AS COTACOES DO DIA
            data_fim = dt.datetime.today() - dt.timedelta(days=1)
            #data_fim = data_fim.replace(hour=0, minute=0, second=0, microsecond=0)

            for usuario in usuarios:
                if usuario == "":
                    pass
                else:
                    lista_acoes, lista_fii = ct.buscaRendaVar(usuario)
                    for acao in lista_acoes:
                        ct.busca_salva_cotacoes(acao, data_fim)
                    for fii in lista_fii:
                        ct.busca_salva_cotacoes(fii, data_fim)

            print("Atualizou todos os títulos.")
            self.progress.stop()
            self.progress.place_forget()

            return

        t3 = threading.Thread(target=atualiza)
        t3.daemon = True
        t3.start()

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
            self.custo_total_acoes = 0
            self.valor_total_acoes = 0
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

                    self.custo_total_acoes += acao.valor_investido
                    self.valor_total_acoes += acao.valor_atual
                    j += 1

                    self.lista_entries += self.entries

            tk.Label(self.tab_dados, text="FII", font='Cambria 18').grid(row=16, column=2)

            j = 0
            self.custo_total_fiis = 0
            self.valor_total_fiis = 0
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

                    self.custo_total_fiis += fii.valor_investido
                    self.valor_total_fiis += fii.valor_atual
                    j += 1

                    self.lista_entries += self.entries_fii

            tk.Label(self.tab_dados, text="RF", font='Cambria 18').grid(row=26, column=2)

            j = 0
            self.custo_total_rfs = 0
            self.valor_total_rfs = 0
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

                    self.custo_total_rfs += rf.valor_investido
                    self.valor_total_rfs += rf.valor_atual_bruto

                    j += 1

                    self.lista_entries += self.entries_rf

            self.canvas.create_window(0, 0, anchor=tk.NW, window=self.fr_principal)

            self.fr_principal.update_idletasks()

            self.canvas.config(scrollregion=self.canvas.bbox("all"))

            self.progress.stop()
            self.progress.grid_forget()

            return

        t4 = threading.Thread(target=busca)
        t4.daemon = True
        t4.start()

        #self.resumao()

        return

    def combo_titulos(self, parametro_lixo):

        lista_de_acoes, lista_de_fii = ct.buscaRendaVar(self.tx_user.get())
        lista_renda_fixa = ct.buscaRendaFixa(self.tx_user.get())
        self.tx_codigo["values"] = ["--ACOES--"] + lista_de_acoes + ["---FII---"] + lista_de_fii + ["--RENDA_FIXA--"] + lista_renda_fixa

        # HABILITA O RECALCULO DOS TITULOS COM A MUDANCA DO USUARIO
        self.primeiro_clique = True

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
                                     command=lambda: self.exibe_resumao()).grid(row=0, column=8, padx='10')

    def exibe_resumao(self):

        self.saldo = float(str(self.tx_saldo.get()).replace(",","."))
        self.proventos = float(str(self.tx_proventos.get()).replace(",","."))
        self.porc_acoes = float(str(self.tx_porc_acoes.get()).replace(",","."))/100
        self.porc_fiis = float(str(self.tx_porc_fiis.get()).replace(",","."))/100
        self.porc_rf = float(str(self.tx_porc_rf.get()).replace(",","."))/100

        self.totais = ct.Resumao(usuario=self.tx_user.get())

        self.custo_acoes = self.totais.custo_total_acoes
        self.valor_acoes = self.totais.valor_total_acoes
        self.taxa_ret_acoes = self.totais.taxa_ret_acoes

        self.custo_fiis = self.totais.custo_total_fiis
        self.valor_fiis = self.totais.valor_total_fiis
        self.taxa_ret_fiis = self.totais.taxa_ret_fiis

        self.custo_rfs = self.totais.custo_total_rfs
        self.valor_rfs = self.totais.valor_total_rfs
        self.taxa_ret_rf = self.totais.taxa_ret_rf

        self.dinheiro_aplic = self.totais.dinheiro_aplic
        self.inflacao_acum_dinheiro = self.totais.taxa_inflacao_dinheiro
        self.dinheiro_corr = self.totais.dinheiro_corr

        self.total_cart = self.saldo+self.proventos+self.valor_acoes+self.valor_fiis+self.valor_rfs
        self.taxa_ret_carteira = (self.total_cart / self.dinheiro_aplic -1)*100
        self.ret_real_carteira = (self.total_cart / self.dinheiro_corr -1)*100
        print(self.ret_real_carteira)

        self.meta_acoes = self.porc_acoes*self.total_cart
        self.meta_fiis = self.porc_fiis*self.total_cart
        self.meta_rf = self.porc_rf*self.total_cart

        self.desvio_acoes = self.valor_acoes - self.meta_acoes
        self.desvio_fiis = self.valor_fiis - self.meta_fiis
        self.desvio_rf = self.valor_rfs - self.meta_rf


        # self.lb_valor_aplic_din = ttk.Label(self.tab_resumao, text="Valor aplicado").grid(row=2, column=0, padx='5')
        # self.lb_valor_atual_cart = ttk.Label(self.tab_resumao, text="Valor atual").grid(row=3, column=0, padx='5')
        # self.lb_taxa_ret_cart = ttk.Label(self.tab_resumao, text="Taxa de retorno").grid(row=4, column=0, padx='5')
        # self.lb_taxa_inflacao_cart = ttk.Label(self.tab_resumao, text="Taxa de inflação").grid(row=5, column=0,
        #                                                                                        padx='5')
        # self.lb_retorno_real_cart = ttk.Label(self.tab_resumao, text="Retorno real").grid(row=6, column=0, padx='5')
        #
        # self.lb_custo_acoes = ttk.Label(self.tab_resumao, text="Custo das ações").grid(row=2, column=2, padx='5')
        # self.lb_valor_atual_acoes = ttk.Label(self.tab_resumao, text="Valor atual das ações").grid(row=3, column=2,
        #                                                                                            padx='5')
        # self.lb_taxa_ret_acoes = ttk.Label(self.tab_resumao, text="Taxa de retorno das ações").grid(row=4, column=2,
        #                                                                                             padx='5')
        # self.lb_meta_acoes = ttk.Label(self.tab_resumao, text="Meta das ações").grid(row=5, column=2, padx='5')
        # self.lb_desvio_acoes = ttk.Label(self.tab_resumao, text="Desvio das ações").grid(row=6, column=2, padx='5')
        #
        # self.lb_custo_fiis = ttk.Label(self.tab_resumao, text="Custo das FIIs").grid(row=2, column=4, padx='5')
        # self.lb_valor_atual_fiis = ttk.Label(self.tab_resumao, text="Valor atual dos FIIs").grid(row=3, column=4,
        #                                                                                          padx='5')
        # self.lb_taxa_ret_fiis = ttk.Label(self.tab_resumao, text="Taxa de retorno dos FIIs").grid(row=4, column=4,
        #                                                                                           padx='5')
        # self.lb_meta_fiis = ttk.Label(self.tab_resumao, text="Meta dos FIIs").grid(row=5, column=4, padx='5')
        # self.lb_desvio_fiis = ttk.Label(self.tab_resumao, text="Desvio das FIIs").grid(row=6, column=4, padx='5')
        #
        # self.lb_custo_rf = ttk.Label(self.tab_resumao, text="Custo da RF").grid(row=2, column=6, padx='5')
        # self.lb_valor_atual_rf = ttk.Label(self.tab_resumao, text="Valor atual da RF").grid(row=3, column=6, padx='5')
        # self.lb_taxa_ret_rf = ttk.Label(self.tab_resumao, text="Taxa de retorno da RF").grid(row=4, column=6, padx='5')
        # self.lb_meta_rf = ttk.Label(self.tab_resumao, text="Meta da RF").grid(row=5, column=6, padx='5')
        # self.lb_desvio_rf = ttk.Label(self.tab_resumao, text="Desvio da RF").grid(row=6, column=6, padx='5')
        # self.lb_liq_imediata_rf = ttk.Label(self.tab_resumao, text="Liq. imediata").grid(row=7, column=6, padx='5')
        # self.lb_loq_30_rf = ttk.Label(self.tab_resumao, text="Liq. 30 dias").grid(row=8, column=6, padx='5')
        # self.lb_90_rf = ttk.Label(self.tab_resumao, text="Liq. 90 dias").grid(row=9, column=6, padx='5')
        # self.lb_180_rf = ttk.Label(self.tab_resumao, text="Liq. 180 dias").grid(row=10, column=6, padx='5')
        # self.lb_360_rf = ttk.Label(self.tab_resumao, text="Liq. 360 dias").grid(row=11, column=6, padx='5')
        # self.lb_mais_de_360_rf = ttk.Label(self.tab_resumao, text="Loq. > 360 dias").grid(row=12, column=6, padx='5')


        return
    #travei aqui porque agora para o resumo da carteira, tenho que acessar as variáveis self.soma_dinheiro_aplicado
        #e self.taxa_ipca_acum_dinheiro que estão dentro do objeto Dinheiro no Carteira.py, mas também são utilizadas
        #na função mostra_valores_dinheiro da class EventoGUI. Com isso vou poder calcular
        #qual a taxa de retorno nominal e real da carteira. Mas to cansado e travei... faltou recurso de python agora...


    #Essa parte adiciona uma tab que permitirá plotar um gráfico com o preço da ação, médias móveis e possivelmente
    #outros parâmetros!

    def graficos(self):

        #df_acoes = data.get_data_yahoo(simbolo, data1, data2)

        #LABEL FRAMES
        self.lf_select = ttk.LabelFrame(self.tab_graf, text="SELEÇÃO DA AÇÃO")
        self.lf_grafico = ttk.LabelFrame(self.tab_graf, text="GRÁFICO")

        #TEXTOS
        self.lb_select1 = ttk.Label(self.lf_select, text="Selecione a ação:")
        self.lb_select2 = ttk.Label(self.lf_select, text="Data inicial:")
        self.lb_select3 = ttk.Label(self.lf_select, text="Data final:")

        #COMBOBOX
        self.emp = pd.read_csv('empresas.csv')
        self.lista_emp = self.emp['acao'].tolist()
        self.cb_acoes = ttk.Combobox(self.lf_select,values=self.lista_emp, width=15,height=5)

        #ENTRYS
        self.st_data1 = tk.StringVar(value='2015-1-1')
        now = datetime.datetime.now()
        self.st_data2 = tk.StringVar(value=str(now.year)+'-'+str(now.month)+'-'+str(now.day))
        self.en_data1 = ttk.Entry(self.lf_select, width=10, textvariable=self.st_data1)
        self.en_data2 = ttk.Entry(self.lf_select, width=10, textvariable=self.st_data2)

        #GRÁFICO
        #self.fig2 = Figure(figsize=(9, 5), facecolor='white')
        #self.ax2 = self.fig2.add_subplot(1, 1, 1)
        #self.canvas_3 = FigureCanvasTkAgg(self.fig2, master=self.lf_grafico)
        #self.canvas_3._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        #BOTÃO
        self.bt_plot = ttk.Button(self.lf_select, text="Gerar gráfico", command=self.calc_graf)

        #LAYOUT
        self.lf_select.grid(row=0, column=0)
        self.lf_grafico.grid(row=1, column=0)

        self.lb_select1.grid(row=0, column=0)
        self.cb_acoes.grid(row=1, column=0)
        self.lb_select2.grid(row=0, column=1)
        self.lb_select3.grid(row=0, column=2)
        self.en_data1.grid(row=1, column=1)
        self.en_data2.grid(row=1, column=2)
        self.bt_plot.grid(row=1, column=3)

    def calc_graf(self):
        #self.fig2 = Figure(figsize=(5, 4), dpi=100)
        #self.t = np.arange(0, 3, .01)
        #self.fig2.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

        #self.canvas = FigureCanvasTkAgg(fig, master=lf_grafico)
        #self.canvas.draw()
        #self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        self.fig2 = Figure(figsize=(9, 5), facecolor='white')
        self.fig2.add_subplot(111).plot(np.arange(0, 3, .01), 2 * np.sin(2 * np.pi * np.arange(0, 3, .01)))
        self.ax2 = self.fig2.add_subplot(1, 1, 1)
        self.ax2.cla()
        self.canvas_3 = FigureCanvasTkAgg(self.fig2, master=self.lf_grafico)
        self.canvas_3._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        

if __name__ == "__main__":

    gui = MainGUI()
    while True:
        try:
            gui.win.mainloop()
            break
        except UnicodeDecodeError:
            pass