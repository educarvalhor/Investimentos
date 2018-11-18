from tela import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
from cal import Ui_Dialog

import sys
app = QtWidgets.QApplication(sys.argv)
Dialog = QtWidgets.QDialog()
ui = Ui_Dialog()
ui.setupUi(Dialog)
Dialog.show()
rsp = Dialog.exec_()
if rsp == 1:
    date = ui.envia_data()

print(date.toString("yyyy-MM-dd"))
print(date.getDate())
print(date.toPyDate())