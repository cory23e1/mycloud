from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import auth_form
import register

class Auth(auth_form.Ui_MainWindow, QMainWindow):
    def __init__(self):
        super(Auth, self).__init__()
        self.setupUi(self)
        self.register_link.clicked.connect(self.open_register_form)

    def open_register_form(self):
        self.window = QMainWindow()
        self.ui = register.Register()
        self.ui.setupUi(self.window)
        self.window.show()

if __name__ == '__main__':
    app = QApplication([])
    auth = Auth()
    auth.show()
    app.exec_()