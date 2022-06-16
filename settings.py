from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets
import settings_form
import funcs as f
import auth_form
import cloud_storage
import sys

class Settings(QMainWindow, settings_form.Ui_MainWindow):
    dirlist = f.get_val_in_local_storage('local_path')

    def __init__(self,parent=None):
        #super(Settings, self).__init__(self, parent)
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        #self.change_user_btn.clicked.connect(self.logout)
        #self.change_user_btn.clicked.connect(self.close)
        self.browseLocalPath_btn.clicked.connect(self.set_local_directory)
        self.load_local_directory()
        self.saveSettings_btn.clicked.connect(self.confirm_settings)

    def close_cloud_storage(self):
        cs = cloud_storage.CloudStorage(self)
        cs.close_window()

    def show_window(self):
        self.show()

    def close_window(self):
        self.close()

    def load_local_directory(self):
        local_path = f.get_val_in_local_storage('local_path')
        self.path_txt.setText(local_path)

    def set_local_directory(self):
        self.dirlist = QFileDialog.getExistingDirectory(None, "Выбрать папку", ".") + '/'
        self.path_txt.setText(self.dirlist)

    def confirm_settings(self):
        f.put_val_in_local_storage('local_path', self.dirlist)
        f.ShowMessageBox('Успешно', 'Локальный путь ' + self.dirlist + ' сохранен')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    sett = Settings()
    sett.show()
    app.exec_()