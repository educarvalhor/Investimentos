import Carteira as ct
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Canvas
from Carteira import timethis

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

class EventosGUI:

    def __init__(self, usuario, investimento, tipo):

        self.tipo = tipo
        self.win = tk.Tk()
        self.win.geometry('1130x350')
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

    def apaga_evento(self):

        self.investimento.ApagaEvento(id=str(self.tx_id.get()))
        self.mostra_eventos()

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
            self.investimento = ct.Dinheiro(self.investimento1, self.usuario)
            self.tx_eventos.insert(tk.INSERT,"ID - OPERAÇÃO - DATA - VALOR \n")
        else:
            print("ERRO")


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
        return

    @timethis
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

    @timethis
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
        self.win.geometry('800x800')
        #self.win.resizable(0, 0)
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

        #
        # create canvas contents

        # FRAME
        self.fr_principal = ttk.Frame(self.canvas)
        self.fr_botoes = tk.Frame(self.fr_principal)
        self.fr_dados = tk.Frame(self.fr_principal)

        self.fr_principal.rowconfigure(1, weight=1)
        self.fr_principal.columnconfigure(1, weight=1)

        #self.fr_principal.pack(expand=1, fill=tk.BOTH)


        # FUNÇÃO PARA CRIAR OS WIDGETS
        self.cria_widgets()

        ct.atualiza_SELIC()
        ct.atualiza_ipca_mensal()
        #self.cria_acoes()

        # ATUALIZA O CDI CASO NECESSÁRIO
        try:
            ct.atualiza_cdi()
        except IndexError as e:
            print("CDI já está atualizado. ERRO: " + str(e))

        self.fr_botoes.grid(row=0, column=0, columnspan=5, sticky=tk.W)
        self.fr_dados.grid(row=1, column=0, columnspan=10, sticky=tk.W)

        self.canvas.create_window(0, 0, anchor=tk.NW, window=self.fr_principal)

        self.fr_principal.update_idletasks()

        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def cria_widgets(self):

        # Label

        self.lb_codigo = ttk.Label(self.fr_botoes, text="Código")
        self.lb_user = ttk.Label(self.fr_botoes, text="Usuário")

        # Texto

        self.st_codigo = tk.StringVar(value="")
        self.tx_codigo = ttk.Combobox(self.fr_botoes, width=20, textvariable=self.st_codigo, height = 5)

        self.st_user = tk.StringVar(value="Higor_Lopes")
        self.tx_user = ttk.Combobox(self.fr_botoes,textvariable= self.st_user, width=15,height=5)
        self.tx_user["values"] = ("Higor_Lopes","Eduardo_Rosa","")
        self.tx_user.bind("<<ComboboxSelected>>", self.combo_acoes)

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

        self.bt_busca_titulos = ttk.Button(self.fr_botoes, text="Busca Títulos", command=self.busca_titulos)

        self.bt_abre_eventos_Dinheiro = ttk.Button(self.fr_botoes, text="DINHEIRO",
                                             command=lambda: self.abre_eventos(str(self.tx_user.get()),
                                                                               str(self.tx_codigo.get()).upper().replace(" ", "_"), "DINHEIRO"))

        self.bt_busca_titulos = ttk.Button(self.fr_botoes, text="Busca Títulos", command=self.busca_titulos)

        # Layout



        self.lb_user.grid(row=0, column=0, sticky=tk.W, padx='5')
        self.lb_codigo.grid(row=0, column=1, sticky=tk.W, padx='5')

        self.tx_user.grid(row=1, column=0, sticky=tk.W, padx='5')
        self.tx_codigo.grid(row=1, column=1, sticky=tk.W, padx='5')

        self.bt_abre_eventos_acao.grid(row=1, column=2, padx='5')
        self.bt_abre_eventos_FII.grid(row=1, column=3, padx='5')
        self.bt_abre_eventos_RF.grid(row=1, column=4, padx='5')
        self.bt_abre_eventos_Dinheiro.grid(row=1, column=5, padx='5')

        self.bt_busca_titulos.grid(row=2, column=0)

        return

    def abre_eventos(self, usuario, codigo , tipo):

#        if self.tipo == "DINHEIRO":
#            gui = EventosGUI(usuario, codigo, tipo)
#            while True:
#                try:
#                    gui.win.mainloop()
#                    break
#                except UnicodeDecodeError:
#                    pass
#
#        else:
#        if self.tx_codigo.get() == "":
#            messagebox.showerror("FALTA DE INFORMAÇÕES","O campo Código está em branco")
#        else:
        gui = EventosGUI(usuario, codigo, tipo)
        while True:
            try:
                gui.win.mainloop()
                break
            except UnicodeDecodeError:
                pass

        return

    def busca_titulos(self):

        # APAGA OS CAMPOS DAS AÇÕES DO OUTRO USUÁRIO
        for entry in self.lista_entries:
            entry.destroy()

        self.carteira = ct.Carteira(usuario=str(self.tx_user.get()))
        self.acoes = self.carteira.acoes
        self.fii = self.carteira.fii
        self.rf = self.carteira.rf

        tk.Label(self.fr_dados, text="AÇÕES", font='Cambria 18').grid(row=3, column=2)

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
                label = tk.Label(self.fr_dados, text=acao.codigo)
                self.lista_entries.append(label)
                label.grid(row=4, column=j+1)

                for i,campo in enumerate(self.campos_acao):
                    # Cria os labels dos campos da ação
                    tk.Label(self.fr_dados, text=self.campos_nome[i]).grid(row=i+5, column=0)
                    # Cria as entries
                    self.entries.append(tk.Entry(self.fr_dados, bg='white', width=15))
                    # Insere o valor dos campos
                    self.entries[i].insert('end', str(campo))
                    # Posiciona as entries
                    self.entries[i].grid(row=i+5, column=j+1)

                self.custo_total_acoes += acao.valor_investido
                self.valor_total_acoes += acao.valor_atual
                j += 1

                self.lista_entries += self.entries
        print("custo_total_acoes")
        print(self.custo_total_acoes)
        print("valor_total_acoes")
        print(self.valor_total_acoes)

        tk.Label(self.fr_dados, text="FII", font='Cambria 18').grid(row=16, column=2)

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

                label2 = tk.Label(self.fr_dados, text=fii.codigo)
                self.lista_entries.append(label2)
                label2.grid(row=17, column=j + 1)

                for i, campo in enumerate(self.campos_fii):
                    # Cria os labels dos campos da ação
                    tk.Label(self.fr_dados, text=self.campos_nome_fii[i]).grid(row=i + 19, column=0)
                    # Cria as entries
                    self.entries_fii.append(tk.Entry(self.fr_dados, bg='white', width=15))
                    # Insere o valor dos campos
                    self.entries_fii[i].insert('end', str(campo))
                    # Posiciona as entries
                    self.entries_fii[i].grid(row=i + 19, column=j + 1)

                self.custo_total_fiis += fii.valor_investido
                self.valor_total_fiis += fii.valor_atual
                j += 1

                self.lista_entries += self.entries_fii
        print("custo_total_fiis")
        print(self.custo_total_fiis)
        print("valor_total_fiis")
        print(self.valor_total_fiis)

        tk.Label(self.fr_dados, text="RENDA FIXA", font='Cambria 18').grid(row=26, column=2)

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
                label3 = tk.Label(self.fr_dados, text=rf.codigo)
                self.lista_entries.append(label3)
                label3.grid(row=27, column=j + 1)


                for i, campo in enumerate(self.campos_rf):
                    # Cria os labels dos campos da ação
                    tk.Label(self.fr_dados, text=self.campos_nome_rf[i]).grid(row=i + 28, column=0)
                    # Cria as entries
                    self.entries_rf.append(tk.Entry(self.fr_dados, bg='white', width=15))
                    # Insere o valor dos campos
                    self.entries_rf[i].insert('end', str(campo))
                    # Posiciona as entries
                    self.entries_rf[i].grid(row=i + 28, column=j+1)

                self.custo_total_rfs += rf.valor_investido
                self.valor_total_rfs += rf.valor_atual_bruto

                j += 1
            
            self.lista_entries += self.entries_rf
        print("custo_total_rfs")
        print(self.custo_total_rfs)
        print("valor_total_rfs")
        print(self.valor_total_rfs)

        self.canvas.create_window(0, 0, anchor=tk.NW, window=self.fr_principal)

        self.fr_principal.update_idletasks()

        self.canvas.config(scrollregion=self.canvas.bbox("all"))


        return

    def combo_acoes(self,parametro_lixo):

        lista_de_acoes, lista_de_fii = ct.buscaRendaVar(self.tx_user.get())
        lista_renda_fixa = ct.buscaRendaFixa(self.tx_user.get())
        self.tx_codigo["values"] = ["--ACOES--"] + lista_de_acoes + ["---FII---"] + lista_de_fii + ["--RENDA_FIXA--"] + lista_renda_fixa

        return

if __name__ == "__main__":

    gui = MainGUI()
    while True:
        try:
            gui.win.mainloop()
            break
        except UnicodeDecodeError:
            pass
