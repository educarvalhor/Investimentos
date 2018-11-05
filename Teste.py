''' tk_entry_loop2.py
exploring Tkinter multiple labeled entry widgets
and using a for loop to create the widgets
'''
from tkinter import *


class AutoScrollbar(Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)
#
# create scrolled canvas

root = Tk()

vscrollbar = AutoScrollbar(root)
vscrollbar.grid(row=0, column=1, sticky=N + S)
hscrollbar = AutoScrollbar(root, orient=HORIZONTAL)
hscrollbar.grid(row=1, column=0, sticky=E + W)

canvas = Canvas(root,
                yscrollcommand=vscrollbar.set,
                xscrollcommand=hscrollbar.set)
canvas.grid(row=0, column=0, sticky=N + S + E + W)

vscrollbar.config(command=canvas.yview)
hscrollbar.config(command=canvas.xview)

# make the canvas expandable
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

#
# create canvas contents

frame = Frame(canvas)
frame.rowconfigure(1, weight=1)
frame.columnconfigure(1, weight=1)

rows = 5
for i in range(1, rows):
    for j in range(1, 10):
        button = Button(frame, padx=7, pady=7, text="[%d,%d]" % (i, j))
        button.grid(row=i, column=j, sticky='news')

canvas.create_window(0, 0, anchor=NW, window=frame)

frame.update_idletasks()

canvas.config(scrollregion=canvas.bbox("all"))

root.mainloop()