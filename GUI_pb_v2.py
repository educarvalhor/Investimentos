import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import datetime as dt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import Calc_pb_v2 as calc
import DB_pb_v2 as db

class Peste_Black_GUI():

    def __init__(self):

        # INTERFACE
        self.win = tk.Tk()
        self.win.geometry('1000x700')
        self.win.resizable(0, 0)
        self.win.title("PESTE BLACK")
        self.win.iconbitmap(r'peste_black_icon.ico')

        # FRAME E MENU
        self.note = ttk.Notebook(self.win)

        self.tab1 = ttk.Frame(self.note)
        self.tab2 = ttk.Frame(self.note)

        self.note.add(self.tab1 ,text='Proporções e Rankings')
        self.note.add(self.tab2 ,text='Gráfico Evolução')
        self.note.pack(expand=1 ,fill='both')

        self.fr_pb = ttk.LabelFrame(self.tab1, text="PROPORÇÕES DE CARTEIRA")

        self.fr_filtro = ttk.LabelFrame(self.tab1, text="CARTEIRA DE AÇÔES")

        self.fr_gr_pb = ttk.LabelFrame(self.tab1, text="GRÁFICOS PROPORÇÕES")

        self.fr_gr_evolucao = ttk.LabelFrame(self.tab2,text='EVOLUÇÃO DA CARTEIRA')

        # FUNÇÃO PARA CRIAR OS WIDGETS
        self.cria_widgets()

    def cria_widgets(self):

        Ano_atual=dt.date.today().year
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

        self.tx_entry_div = tk.StringVar(value=Ano_atual-15)
        self.en_div = ttk.Entry(self.fr_filtro, width=4, textvariable=self.tx_entry_div, state='disabled')

        # BOTÕES

        self.bt_atualiza_db = ttk.Button(self.tab1, text="Atualiza Dados", command=self.atual_progress)

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
        self.bt_DIV = tk.Checkbutton(self.fr_filtro, text="Div. desde:", variable=self.check6, command
                                     =self.habilita_en_div)

        self.bt_fund = ttk.Button(self.fr_filtro, text="Filtra ações", command=self.calc_fund)

        # LAYOUT

        # PRESENTES NO FRAME PRINCIPAL
        self.fr_filtro.grid(row=2, column=0, columnspan =6)
        self.fr_pb.grid(row=0, column=0)
        self.fr_gr_pb.grid(row=0, column=1)
        self.bt_atualiza_db.grid(row=8, column=0,sticky =tk.W,padx= '20')

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

        # CRIAÇÃO DO MENU
        self.menuBar = tk.Menu(self.win)
        self.win.config(menu=self.menuBar)

        # MENU ARQUIVO
        self.fileMenu = tk.Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label="Novo", command=self._novo)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Fechar", command=self._exit)
        self.menuBar.add_cascade(label="Arquivo", menu=self.fileMenu)

        # MENU AJUDA
        self.helpMenu = tk.Menu(self.menuBar, tearoff=0)
        self.helpMenu.add_command(label='Sobre', command=self._sobre)
        self.menuBar.add_cascade(label="Ajuda", menu=self.helpMenu)

        # GRÁFICO
        self.fig = Figure(figsize=(5, 3), facecolor='white')
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.fr_gr_pb)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # GRAFICO EVOLUÇÃO

        self.fr_gr_evolucao.pack(expand=1,fill=tk.BOTH)
        self.fig2 = Figure(figsize=(5,5),facecolor='white')
        self.ax2 = self.fig2.add_subplot(1,1,1)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.fr_gr_evolucao)
        self.canvas2._tkcanvas.pack(fill=tk.BOTH, expand=1)

        # FUNCOES

    def calc_pb(self):
        self.progress = ttk.Progressbar(self.fr_pb, orient="horizontal", length=400, mode='indeterminate')

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
            self.canvas.draw()
            self.fr_gr_pb.update()

            # CRIA GRÁFICO BOKEH

            from bokeh.layouts import column
            from bokeh.models import CustomJS, ColumnDataSource, Slider, ranges, LabelSet
            from bokeh.plotting import figure, output_file, show

            output_file("callback.html")

            _, self.prop_graf, self.datas = calc.itera_pb(dt.datetime.strptime(self.data1.get(), '%d/%m/%Y'), int(self.qtd_meses_dado.get()))

            x_val = [x for x, _ in enumerate(self.datas)]

            y = self.prop_graf
            y = list(map(float, y))

            source = ColumnDataSource(data=dict(x=self.datas, y=y))

            plot = figure(plot_width=800, plot_height=200,
                          x_minor_ticks=len(self.datas),
                          x_range=source.data["x"],
                          y_range=ranges.Range1d(start=0, end=110))

            labels = LabelSet(x='x', y='y', text='y', level='glyph',
                              x_offset=-5, y_offset=0, source=source, render_mode='canvas')

            plot.vbar(source=source, x='x', top='y', bottom=0, width=0.3)

            plot.add_layout(labels)
            show(plot)


            # FIM DO TESTE DE GRÁFICO

        self.bt_calc['state'] = 'disabled'
        threading.Thread(target=calcula).start()

    def calc_gr_cdi(self):
        return

    def habilita_en_pl(self):
        if self.check1.get() == 1:
            self.en_pl.configure(state='enabled')
        else:
            self.en_pl.configure(state='disabled')

    def habilita_en_pvp(self):
        if self.check2.get() == 1:
            self.en_pvp.configure(state='enabled')
        else:
            self.en_pvp.configure(state='disabled')

    def habilita_en_dy(self):
        if self.check3.get() == 1:
            self.en_dy.configure(state='enabled')
        else:
            self.en_dy.configure(state='disabled')

    def habilita_en_p_ebit(self):
        if self.check4.get() == 1:
            self.en_p_ebit.configure(state='enabled')
        else:
            self.en_p_ebit.configure(state='disabled')

    def habilita_en_liq(self):
        if self.check5.get() == 1:
            self.en_liq.configure(state='enabled')
        else:
            self.en_liq.configure(state='disabled')

    def habilita_en_div(self):
        if self.check6.get() == 1:
            self.en_div.configure(state='enabled')
        else:
            self.en_div.configure(state='disabled')

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

    def atual_progress(self):
        self.progress = ttk.Progressbar(self.tab1, orient="horizontal", length=400, mode='indeterminate')

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
            at_cdi = messagebox.askyesno('Confirma a atualização do CDI ?','Deseja atualizar o CDI ?')
            if at_cdi == True:
                db.atualiza_cdi()
            self.progress.stop()
            self.progress.grid_forget()
            self.bt_atualiza_db['state'] = 'normal'

        self.bt_atualiza_db['state'] = 'disabled'
        threading.Thread(target=atualiza_db).start()

    def _exit(self):
        self.win.quit()
        self.win.destroy()
        exit()

    def _novo(self):
        pb2 = Peste_Black_GUI()
        pb2.win.mainloop()

    def _sobre(self):
        messagebox.showinfo('Sobre o software',
                            'Este é um software criado para análise de carteiras de investimentos. \n\n'
                            'Criado por Higor Lopes e Eduardo Rosa ')

if __name__ == '__main__':
    pb = Peste_Black_GUI()
    while True:
        try:
            pb.win.mainloop()
            break
        except UnicodeDecodeError:
            pass