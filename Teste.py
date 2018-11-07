''' tk_entry_loop2.py
exploring Tkinter multiple labeled entry widgets
and using a for loop to create the widgets
'''
import tkinter as tk
from tkinter import ttk

class Peste_Black_GUI():

    def __init__(self):

        # INTERFACE
        self.win = tk.Tk()
        self.win.geometry('1000x700')
        #self.win.resizable(0, 0)
        self.win.title("PESTE BLACK")
        self.win.iconbitmap(r'peste_black_icon.ico')

        # FRAME E MENU
        self.note = ttk.Notebook(self.win)

        self.cab = ttk.Frame(self.win, width=500, height=350)
        self.tab1 = ttk.Frame(self.note,width=500, height=350)
        self.tab2 = ttk.Frame(self.note, width=500, height=350)

        self.note.add(self.tab1 ,text='Proporções e Rankings')
        self.note.add(self.tab2 ,text='Gráfico Evolução')

        self.cab.grid(row=0, column=0)
        self.note.grid(row=1, column=0)

        self.fr_pb = ttk.LabelFrame(self.tab1, text="PROPORÇÕES DE CARTEIRA", width=500, height=350)

        self.fr_filtro = ttk.LabelFrame(self.tab1, text="CARTEIRA DE AÇÔES", width=500, height=350)

        self.fr_gr_pb = ttk.LabelFrame(self.tab1, text="GRÁFICOS PROPORÇÕES")

        self.fr_gr_evolucao = ttk.LabelFrame(self.tab2,text='EVOLUÇÃO DA CARTEIRA',width=500, height=350)


if __name__ == "__main__":

    if __name__ == "__main__":

        gui = Peste_Black_GUI()
        while True:
            try:
                gui.win.mainloop()
                break
            except UnicodeDecodeError:
                pass