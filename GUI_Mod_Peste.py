import Carteira_Mod_Peste as ct
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class EventosGUI:

    def __init__(self,usuario,acao):

        self.win = tk.Tk()
        self.win.geometry('900x400')
        #self.win.resizable(0, 0)
        self.win.title("Eventos")
        self.win.iconbitmap(r'peste_black_icon.ico')

        # FRAME E MENU
        self.fr_novos_eventos = ttk.LabelFrame(self.win, text="EVENTOS")
        self.fr_novos_eventos.pack(expand=1, fill=tk.BOTH)

        # FUNÇÃO PARA CRIAR OS WIDGETS
        self.cria_widgets()
        self.acao1 = acao

        self.usuario = usuario

        self.mostra_eventos()

    def cria_widgets(self):

        # Labels

        self.lb_tipo = ttk.Label(self.fr_novos_eventos, text="Tipo de evento")
        self.lb_valor = ttk.Label(self.fr_novos_eventos, text="Valor")
        self.lb_qtd = ttk.Label(self.fr_novos_eventos, text="Quantidade")
        self.lb_corr = ttk.Label(self.fr_novos_eventos, text="Corretagem")
        self.lb_data = ttk.Label(self.fr_novos_eventos, text="Data")


        # Textos

        self.tx_tipo = tk.Listbox(self.fr_novos_eventos,width=20,height=1)
        lista_de_tipos = ["Compra","Venda", "Rendimento"]
        for tipo in lista_de_tipos:
            self.tx_tipo.insert(tk.END,tipo)

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
        self.lb_valor.grid(row=0, column=1, sticky=tk.W, padx='5')
        self.lb_qtd.grid(row=0, column=2, sticky=tk.W, padx='5')
        self.lb_corr.grid(row=0, column=3, sticky=tk.W, padx='5')
        self.lb_data.grid(row=0, column=4, sticky=tk.W, padx='5')

        self.bt_salva_evento.grid(row=0, column=6, sticky=tk.W, padx='10',rowspan=2)

        self.tx_tipo.grid(row=1, column=0, sticky=tk.W, padx='5')
        self.tx_valor.grid(row=1, column=1, sticky=tk.W, padx='5')
        self.tx_qtd.grid(row=1, column=2, sticky=tk.W, padx='5')
        self.tx_corr.grid(row=1, column=3, sticky=tk.W, padx='5')
        self.tx_data.grid(row=1, column=4, sticky=tk.W, padx='5')

        self.tx_log.grid(row=2, column=0, columnspan=6, sticky=tk.W, padx='5')

        self.tx_id.grid(row=3, column=0)

        self.bt_apaga_evento.grid(row=3, column=1, sticky=tk.W, padx='20')

        self.bt_mostra_evento.grid(row=3, column=2, padx='20')

        self.tx_eventos.grid(row=4,column=0,columnspan=6)

    def apaga_evento(self):

        self.acao.ApagaEvento(id=str(self.tx_id.get()))
        self.mostra_eventos()

    def mostra_eventos(self):

        self.tx_eventos.delete('1.0', tk.END)
        self.acao = ct.Acao(self.acao1, self.usuario)

        self.tx_eventos.insert(tk.INSERT,"ID - ACAO - TIPO - VALOR -   DATA   - QTD - COR - IR - PL  \n")
        for evento in self.acao.lista_de_eventos:
            for campo in evento:
                self.tx_eventos.insert(tk.INSERT, " " + str(campo)[0:10] + " ")
            self.tx_eventos.insert(tk.INSERT,"\n")

        return


    def salva_evento(self):

        # Trata os dados

        usuario = self.usuario
        acao = self.acao1
        tipo = str(self.tx_tipo.get(tk.ACTIVE))
        valor = float(str(self.tx_valor.get().replace(",",".")))
        data = str(self.tx_data.get())

        if self.tx_qtd.get() == "":
            qtd = ""
        else:
            qtd = float(str(self.tx_qtd.get()).replace(",","."))

        if self.tx_corr.get() == "":
            corretagem = 0
        else:
            corretagem = float(str(self.tx_corr.get()).replace(",","."))

        if acao == "" or data == "":
            self.tx_log.insert(tk.INSERT,"Evento não criado pois existem campos em branco" + "\n")
        else:
            ev = ct.Evento(acao,tipo,valor,data,qtd,corretagem,usuario)
            ev.salvaDB()

            self.tx_log.insert(tk.INSERT,"\n" + "{0} de {1} salvo no banco de dados".format(ev.tipo,ev.acao))
            self.tx_log.see(tk.END)

        self.mostra_eventos()
        return

class MainGUI:

    def __init__(self):

        self.win = tk.Tk()
        self.win.geometry('800x600')
        #self.win.resizable(0, 0)
        self.win.title("Carteira de Ações")
        self.win.iconbitmap(r'peste_black_icon.ico')

        # FRAME
        self.fr_principal = ttk.LabelFrame(self.win, text="PRINCIPAL")
        self.fr_principal.pack(expand=1, fill=tk.BOTH)

        # FUNÇÃO PARA CRIAR OS WIDGETS
        self.cria_widgets()

        #self.cria_acoes()

    def cria_widgets(self):

        # Label

        self.lb_acao = ttk.Label(self.fr_principal, text="Ação")
        self.lb_user = ttk.Label(self.fr_principal, text="Usuário")

        # Texto

        self.st_acao = tk.StringVar(value="")
        self.tx_acao = ttk.Entry(self.fr_principal, width=10, textvariable=self.st_acao)

        self.tx_user = tk.Listbox(self.fr_principal,width=20,height=1)
        lista_de_usuarios = ["Higor_Lopes","Eduardo_Rosa"]
        for user in lista_de_usuarios:
            self.tx_user.insert(tk.END,user)

        # Botões

        self.bt_abre_eventos = ttk.Button(self.fr_principal, text="Eventos",
                                          command=lambda: self.abre_eventos(str(self.tx_user.get(tk.ACTIVE)),
                                                                            str(self.tx_acao.get()).upper()))

        self.bt_cria_acoes = ttk.Button(self.fr_principal, text="Ações", command=self.cria_acoes)

        # Layout

        self.lb_user.grid(row=0, column=0, sticky=tk.W, padx='5')
        self.lb_acao.grid(row=0, column=1, sticky=tk.W, padx='5')

        self.tx_user.grid(row=1, column=0, sticky=tk.W, padx='5')
        self.tx_acao.grid(row=1, column=1, sticky=tk.W, padx='5')

        self.bt_abre_eventos.grid(row=0, column=2, rowspan=2)

        self.bt_cria_acoes.grid(row=2, column=0)

        return

    def abre_eventos(self, usuario, acao):

        if self.tx_acao.get() == "":
            messagebox.showerror("FALTA DE INFORMAÇÕES","O campo AÇÃO está em branco")

        else:
            gui = EventosGUI(usuario, acao)
            while True:
                try:
                    gui.win.mainloop()
                    break
                except UnicodeDecodeError:
                    pass
        return

    def cria_acoes(self):

        self.carteira = ct.Carteira(usuario=str(self.tx_user.get(tk.ACTIVE)))
        self.acoes = self.carteira.acoes

        for j, acao in enumerate(self.acoes):

            if acao.qtd_atual > 0:

                self.campos_nome = ["Qtd atual", "Preço médio (R$)",  "Cotação atual (R$)", "Valor aplicado (R$)",
                                    "Variação sem div. (%)", "Dividendos (R$)", "Variação c/ div. (%)", "Data média aq.",
                                    "Inflação acumulada (%)", "Variação Real (%)"]

                self.campos_acao = [acao.qtd_atual, '${:,}'.format(round(acao.preco_medio_sem_div,2)),
                                    '$ {:,}'.format(round(acao.cotacao_atual,2)),
                                    '$ {:,}'.format(round(acao.valor_atual,2)),
                                    '{} %'.format(round(acao.RetornoSemDiv,2)),
                                    '$ {:,}'.format(round(acao.soma_dividendo,2)),
                                    '{} %'.format(round(acao.RetornoComDiv,2)),
                                    acao.data_media_aquisicao.strftime("%d / %m / %Y"),
                                    '{} %'.format(round(acao.inflacao_acum,2)),
                                    '{} %'.format(round(acao.RetornoRealSemDiv,2))]

                self.entries = []

                tk.Label(self.fr_principal, text=acao.acao).grid(row=3, column=j+1)

                for i,campo in enumerate(self.campos_acao):
                    # Cria os labels dos campos da ação
                    tk.Label(self.fr_principal, text=self.campos_nome[i]).grid(row=i+4, column=0)
                    # Cria as entries
                    self.entries.append(tk.Entry(self.fr_principal, bg='white', width=15))
                    # Insere o valor dos campos
                    self.entries[i].insert('end', str(campo))
                    # Posiciona as entries
                    self.entries[i].grid(row=i+4, column=j+1)

        return


if __name__ == "__main__":

    gui = MainGUI()
    while True:
        try:
            gui.win.mainloop()
            break
        except UnicodeDecodeError:
            pass