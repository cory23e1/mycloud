from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import auth_form
import funcs as f
import database
import register
import sys

class Auth(QMainWindow,auth_form.Ui_MainWindow):
    def __init__(self,parent=None):
        QWidget.__init__(self, parent)
        #super(Auth, self).__init__()
        self.setupUi(self)

        self.register_link.clicked.connect(self.open_reg)
        self.login_btn.clicked.connect(self.login)
        self.load_log_n_pass()

    def open_reg(self):
        reg = register.Register(self)
        reg.show_window()

    def show_window(self):
        self.show()

    def close_window(self):
        self.close()

    def load_log_n_pass(self):
        login = f.get_val_in_local_storage('login')
        password = f.get_val_in_local_storage('password')
        self.login_txt.setText(login)
        self.pass_txt.setText(password)
        print(login)
        print(password)

    def login(self):
        try:
            login = self.login_txt.text()
            password = self.pass_txt.text()
            if login!='' and password!='':
                db = database
                raw_id = db.SQL.select(None,'accounts','id','login',str(login))
                formated_id = str(" ".join(raw_id))
                print(formated_id)
                if formated_id != '':
                    raw_password = db.SQL.select(None,'accounts','password','id',formated_id)
                    formated_password = str(" ".join(raw_password))
                    if formated_password == password:
                        raw_login = db.SQL.select(None, 'accounts', 'login', 'id', formated_id)
                        raw_service_acc_id = db.SQL.select(None, 'accounts', 'service_acc_id', 'id', formated_id)
                        raw_static_key_id = db.SQL.select(None, 'accounts', 'static_key_id', 'id', formated_id)
                        raw_static_secret_key =  db.SQL.select(None, 'accounts', 'static_secret_key', 'id', formated_id)

                        formated_login = str(" ".join(raw_login))
                        formated_service_acc_id = str(" ".join(raw_service_acc_id))
                        formated_static_key_id = str(" ".join(raw_static_key_id))
                        formated_static_secret_key = str(" ".join(raw_static_secret_key))
                        print(formated_login)
                        print(formated_service_acc_id)

                        f.put_val_in_local_storage('service_acc_id',formated_service_acc_id)
                        f.put_val_in_local_storage('static_key_id', formated_static_key_id)
                        f.put_val_in_local_storage('static_secret_key', formated_static_secret_key)
                        f.put_val_in_local_storage('login',formated_login)
                        f.put_val_in_local_storage('password',formated_password)
                        print('успешно')
                        self.open_cloud_storage_form()
                        #sys.exit()
                    else:
                        f.ShowMessageBox('Ошибка', 'Пароль неверный')
                else:
                    f.ShowMessageBox('Ошибка', 'Такой пользователь не зарегистрирован')
            else:
                f.ShowMessageBox('Ошибка','Не все поля заполнены')
        except Exception as error:
            print(str(error))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    auth = Auth()
    auth.show()
    app.exec_()