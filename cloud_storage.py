from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets

import cloud_storage_form
from s3 import S3
import funcs as f
import os
import settings
import auth
import sys
import asyncio

class CloudStorage(cloud_storage_form.Ui_MainWindow,QMainWindow):
    current_path = ''
    current_key = ''
    selected_key = ''

    def __init__(self,parent=None):
        #super(CloudStorage, self).__init__()
        QtWidgets.QWidget.__init__(self, parent)
        #super.__init__(self)
        self.setupUi(self)
        self.fill_object_table('', '')
        #self.isLogged()
        self.set_current_user()
        self.tv_cloudStorage.doubleClicked.connect(self.open_folder_or_download_obj_by_dblclck)
        self.tv_cloudStorage.clicked.connect(self.select_table_row)
        self.btn_home.clicked.connect(self.go_home)
        self.btn_back.clicked.connect(self.go_back)
        self.btn_upload.clicked.connect(self.upload_files_to_cloud)
        self.btn_del.clicked.connect(self.del_file_from_cloud)
        self.btn_download.clicked.connect(self.download_file_from_cloud)
        self.OpenSettinsAction.triggered.connect(self.open_sett_win)
        self.change_curr_path_txt("")
        self.change_acc_btn.clicked.connect(self.logout)
        self.make_new_folder_btn.clicked.connect(self.show_new_folder_dialog)

    # def isLogged(self):
    #     login = f.get_val_in_local_storage('login')
    #     password = f.get_val_in_local_storage('password')
    #     if login == '' and password == '':
    #         self.close_window()
    #         auth_win = auth.Auth(self)
    #         auth_win.show_window()
    #     else:
    #         self.fill_object_table('', '')


    def show_new_folder_dialog(self):
        f.put_val_in_local_storage('curr_path',self.current_path)
        new_folder_dialog = ClssDialog()
        new_folder_dialog.window_closed.connect(self.refresh_object_table)
        new_folder_dialog.exec_()

    def refresh_object_table(self):
        self.fill_object_table(self.current_path,'')

    def set_current_user(self):
        try:
            current_user = f.get_val_in_local_storage('login')
            self.current_user_lbl.setText("Текущий пользователь: " + current_user)
        except Exception:
            pass

    #открыть настройки
    def open_sett_win(self):
        sett_win = settings.Settings(self)
        sett_win.show_window()

    def reset_auth(self):
        f.put_val_in_local_storage('service_acc_id', '')
        f.put_val_in_local_storage('static_key_id', '')
        f.put_val_in_local_storage('static_secret_key', '')
        #f.put_val_in_local_storage('login', '')
        #f.put_val_in_local_storage('password', '')

    #разлогиниться
    def logout(self):
        self.reset_auth()
        self.close_window()
        auth_win = auth.Auth(self)
        auth_win.show_window()

    #открытие cloud_storage
    def show_window(self):
        self.show()

    #закрытие cloud_storage
    def close_window(self):
        self.close()

    def change_curr_path_txt(self,path):
        self.curr_directory_txt.setText("ist-pnipu-bukcet/"+path)
        #pass

    # def getOpenFilesAndDirs(parent=None, caption='', directory='', filter='', initialFilter='', options=None):
    #     def updateText():
    #         # update the contents of the line edit widget with the selected files
    #         selected = []
    #         for index in view.selectionModel().selectedRows():
    #             selected.append('"{}"'.format(index.data()))
    #         lineEdit.setText(' '.join(selected))
    #
    #     dialog = QFileDialog(parent, windowTitle=caption)
    #     dialog.setFileMode(dialog.ExistingFiles)
    #     if options:
    #         dialog.setOptions(options)
    #     dialog.setOption(dialog.DontUseNativeDialog, True)
    #     if directory:
    #         dialog.setDirectory(directory)
    #     if filter:
    #         dialog.setNameFilter(filter)
    #         if initialFilter:
    #             dialog.selectNameFilter(initialFilter)
    #     dialog.accept = lambda: QDialog.accept(dialog)
    #     stackedWidget = dialog.findChild(QStackedWidget)
    #     view = stackedWidget.findChild(QListView)
    #     view.selectionModel().selectionChanged.connect(updateText)
    #     lineEdit = dialog.findChild(QLineEdit)
    #     dialog.directoryEntered.connect(lambda: lineEdit.setText(''))
    #     dialog.exec_()
    #     return dialog.selectedFiles()

    def upload_files_to_cloud(self):
        try:
            #открытие диалога выбора файлов
            filenames, ok = QFileDialog.getOpenFileNames(None,"Выберите несколько файлов",".","All Files(*.*)")
            #filenames = self.getOpenFilesAndDirs('', '', '', '')
            print(filenames)
            folder = os.path.dirname(filenames[0])
            print("folder =", folder)
            print("files =", filenames)
            #загрузка файлов в бакет
            S3.upload(None,'ist-pnipu-bucket', filenames,self.current_path)
            #обновление таблицы объектов
            self.fill_object_table(self.current_path, '')
            #вывод сообщения об успешной загрузке файлов
            f.ShowMessageBox('Успешно', 'Файлы ' + str(filenames) + ' были загружены')
        except IndexError as ex:
            pass
            #f.ShowMessageBox("Ошибка",str(ex))

    def download_file_from_cloud(self):
        # объявление пустого списка объектов
        file_names = []
        file_names_without_dir = []
        #print(file_names)
        # подсчет количества строк в таблице объектов
        row_count = self.tv_cloudStorage.model().rowCount()
        # проверка на отсутствие объектов в бакете
        if row_count != 0:
            for row in range(row_count):
                check = self.tv_cloudStorage.model().item(row, 0).checkState()
                # проверка состояния чекбокса выбора
                if check == 2:
                    file_names.append(self.current_path+self.tv_cloudStorage.model().index(row, 1).data())
                    file_names_without_dir.append(self.tv_cloudStorage.model().index(row, 1).data())
            # print(file_names)
            # print(file_names_without_dir)
            #S3.download('ist-pnipu-bucket', file_names, file_names_without_dir)
            # проверка если один из чекбоксов поменял состояние
            if not all(item == 0 for item in file_names):
                #print(file_names)
                # скачивание файлов из бакета
                #S3.download('ist-pnipu-bucket', file_names, self.current_path)
                S3.download('ist-pnipu-bucket', file_names)
                #обновление списка объектов
                self.fill_object_table(self.current_path, '')
                #вывод сообщения об успешном сохранении на локальный диск
                f.ShowMessageBox('Успешно','Файлы '+str(file_names)+' сохранены на локальный диск')
            elif self.selected_key != '':
                file_names.append(self.selected_key)
                S3.download('ist-pnipu-bucket', file_names)
                self.fill_object_table(self.current_path, '')
            else:
                f.ShowMessageBox('Сохранение','Не выбраны файлы для сохранения')
        else:
            f.ShowMessageBox('Сохранение','Нет файлов для сохранения')
        #print(file_names)

    def del_file_from_cloud(self):
        file_names = []
        row_count = self.tv_cloudStorage.model().rowCount()
        if row_count != 0:
            for row in range(row_count):
                check = self.tv_cloudStorage.model().item(row, 0).checkState()
                if check == 2:
                    file_names.append(self.tv_cloudStorage.model().index(row, 1).data())
            if not all(item == 0 for item in file_names):
                files_in_folders = []
                for file in file_names:
                    if '/' in file:
                        data = S3.get_object_list('ist-pnipu-bucket',self.current_path+file,'')
                        for item in data:
                            files_in_folders.append(item['Key'])
                        S3.delete('ist-pnipu-bucket',files_in_folders,'')
                        self.fill_object_table(self.current_path, '')
                        f.ShowMessageBox("Удаление", 'Файлы '+str(files_in_folders)+' , были удалены')
                    else:
                        S3.delete('ist-pnipu-bucket', file_names, self.current_path)
                        f.ShowMessageBox("Удаление", 'Файлы ' + str(file_names) + ' , были удалены')
                        self.fill_object_table(self.current_path, '')
                        break
            elif self.selected_key != '':
                file_names.append(self.selected_key)
                S3.delete('ist-pnipu-bucket', file_names, '')
                self.fill_object_table(self.current_path, '')
                f.ShowMessageBox("Удаление", 'Файл ' + str(file_names) + ' , был удален')
            else:
                f.ShowMessageBox("Удаление", 'не выбраны файлы')
        else:
            f.ShowMessageBox("Удаление", 'нет файлов для удаления')
            #print('нет файлов для удаления')

    def select_table_row(self):
        try:
            index = self.tv_cloudStorage.selectedIndexes()[1]
            object_name = index.model().itemFromIndex(index).text()
            print(object_name)
            self.selected_key = self.current_path+object_name
        except:
            pass

    def append_row_object_table(self, key, date, size):
        item0 = QStandardItem()
        item0.setCheckState(Qt.CheckState.Unchecked)
        item0.setCheckable(True)
        item1 = QStandardItem(key)
        item2 = QStandardItem(date)
        item3 = QStandardItem(size)
        #item4 = QStandardItem(status)
        self.tv_cloudStorage.model().appendRow([item0, item1, item2, item3])

    def fill_object_table(self, directory, delimiter):
        self.selected_key = ''
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Выбор", "Имя", "Дата", "Размер"])
        self.tv_cloudStorage.setModel(model)
        self.tv_cloudStorage.header().resizeSection(0, 80)
        self.tv_cloudStorage.header().resizeSection(1, 300)
        service_acc_id = f.get_val_in_local_storage('service_acc_id')
        current_login = f.get_val_in_local_storage('login')
        try:
            # получение объектов из бакета
            data = S3.get_object_list('ist-pnipu-bucket', directory, delimiter)
            for obj in data:
                key_name = obj['Key']
                object_owner = obj['Owner']['ID']
                if object_owner == service_acc_id or current_login=='admin':
                    # проверка есть ли сейчас что то в переменной текущего пути
                    if self.current_path == "":
                        # проверка является ли объект папкой
                        if '/' in key_name:
                            if key_name.count('/') >= 2 or str(key_name).split('/')[1] != '':
                                # отсеивание объектов типа folder/object.jpg и.т.д
                                pass
                            else:
                                #вставка строки с данными объекта
                                self.append_row_object_table(key_name,str(obj['LastModified'])[:19],f.convert_size(obj['Size']))
                        else:
                            self.append_row_object_table(key_name, str(obj['LastModified'])[:19], f.convert_size(obj['Size']))
                    else:
                        # удаление имени папки в наименовании объекта если пользователь находится в папке
                        elem_of_split_key_name = ''
                        replaced_key_name = key_name.replace(self.current_path, '')
                        split_key_name = str(replaced_key_name).split('/')
                        if len(split_key_name) > 1:
                            if split_key_name[1] != '':
                                elem_of_split_key_name = split_key_name[1]
                        if replaced_key_name == self.current_path or replaced_key_name == '' or elem_of_split_key_name != '':
                            pass
                        else:
                            self.append_row_object_table(replaced_key_name, str(obj['LastModified'])[:19], f.convert_size(obj['Size']))
                else:
                    pass
        except Exception as error:
            pass
            #print(error)


    def open_folder_or_download_obj_by_dblclck(self):
        index = self.tv_cloudStorage.selectedIndexes()[1]
        #print(index)
        object_name = index.model().itemFromIndex(index).text()
        if object_name[len(object_name)-1] == '/':
            self.current_key = object_name
            self.current_path += object_name
            self.change_curr_path_txt(self.current_path)
            print('==============================================')
            print('Текущий директория - ' + self.current_path)
            print('Текущий ключ - ' + self.current_key)
            self.fill_object_table(self.current_path, '')
        else:
            local_save_path = f.get_val_in_local_storage('local_path')
            cloud_obj_name = self.current_path+object_name
            cloud_obj_names = []
            cloud_obj_names.append(cloud_obj_name)
            print(cloud_obj_name)
            S3.download('ist-pnipu-bucket', cloud_obj_names)
            saved_file_path = local_save_path + self.current_path+object_name
            print('это из клауд сторадж '+saved_file_path)
            try:
                os.startfile(saved_file_path)
            except OSError:
                f.ShowMessageBox('Ошибка','Невозможно запустить файл')

    def go_home(self):
        self.current_key = ''
        self.current_path = ''
        self.change_curr_path_txt('')
        self.selected_key = ''
        self.fill_object_table('', '')

    def go_back(self):
        self.current_path = self.current_path.replace(self.current_key, '')
        self.change_curr_path_txt(self.current_path)
        self.current_key = self.current_path
        self.selected_key = ''
        print('==============================================')
        print('Текущий директория - ' + self.current_path)
        print('Текущий ключ - ' + self.current_key)
        self.fill_object_table(self.current_path, '')

refresh_table = CloudStorage.fill_object_table

class ClssDialog(QtWidgets.QDialog):
    window_closed = pyqtSignal()
    def __init__(self, parent=None):
        super(ClssDialog, self).__init__(parent)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.make_folder)
        self.line_edit = QtWidgets.QLineEdit(self)
        self.verticalLayout.addWidget(self.line_edit)
        self.verticalLayout.addWidget(self.pushButton)
        self.setWindowTitle("Создать папку")
        self.pushButton.setText("Создать")

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()

    def make_folder(self):
        curr_path = f.get_val_in_local_storage('curr_path')
        folder_name = self.line_edit.text()
        S3.put(None,'ist-pnipu-bucket', curr_path+folder_name+"/")
        self.close()
        cs = CloudStorage()
        cs.fill_object_table(curr_path,'')

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    cs = CloudStorage()
    cs.show()
    app.exec_()

if __name__ == '__main__':
    main()
