from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets
import settings_form
import funcs as f
import auth_form
import cloud_storage
import sys

class Settings(settings_form.Ui_MainWindow,QMainWindow):
    dirlist = f.get_val_in_local_storage('local_path')

    def __init__(self,parent=None):
        #super(Settings, self).__init__(self, parent)
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowModality(QtCore.Qt.WindowModal)
        #super(Settings, self).__init__(parent)
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
        try:
            self.dirlist = QFileDialog.getExistingDirectory(None, "Выбрать папку", ".") + '/'
            if self.dirlist!='/':
                self.path_txt.setText(self.dirlist)
            else:
                pass
        except Exception as ex:
            print('ниче не выбрано')
            print(ex)

    def confirm_settings(self):
        f.put_val_in_local_storage('local_path', self.dirlist)
        f.ShowMessageBox('Успешно', 'Локальный путь ' + self.dirlist + ' сохранен')

if __name__ == '__main__':
    app = QApplication([])
    sett = Settings()
    sett.show()
    app.exec_()