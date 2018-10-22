''' tk_entry_loop2.py
exploring Tkinter multiple labeled entry widgets
and using a for loop to create the widgets
'''
from functools import partial
try:
    # Python2
    import Tkinter as tk
except ImportError:
    # Python3
    import tkinter as tk

class Gui(tk.Tk):
    def __init__(self):
        # the root will be self
        tk.Tk.__init__(self)

        self.title('multiple labeled entries')
        self.entries = []

        for n in range(20):
            # create left side info labels
            tk.Label(self, text="%2d: " % n).grid(row=n, column=0)
            # create entries list
            self.entries.append(tk.Entry(self, bg='yellow', width=40))
            # grid layout the entries
            self.entries[n].grid(row=n, column=1)
            # bind the entries return key pressed to an action
            self.entries[n].bind('<Return>', partial(self.action, n))
        # test, load one entry
        self.entries[0].insert('end', 'enter a word in an entry')
    def action(self, ix, event):
        '''this entry return key pressed'''
        text = self.entries[ix].get()
        info = "entry ix=%d text=%s" % (ix, text)
        # use first entry to show test results
        # clear old text
        self.entries[0].delete(0, 'end')
        # insert new text
        self.entries[0].insert('end', info)
    def run(self):
        self.mainloop()
# test the potential module
if __name__ == '__main__':
    Gui().run()