from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
#import design
from s3 import S3
import funcs as f
import os
import settings_form
import cloud_storage_form

class CloudStorage(cloud_storage_form.Ui_MainWindow, QMainWindow):
    current_path = ''
    current_key = ''
    selected_key = ''

    def __init__(self):
        super(CloudStorage, self).__init__()
        self.fill_object_table('', '')
        self.tv_cloudStorage.doubleClicked.connect(self.open_folder_or_download_obj_by_dblclck)
        self.tv_cloudStorage.clicked.connect(self.select_table_row)
        self.btn_home.clicked.connect(self.go_home)
        self.btn_back.clicked.connect(self.go_back)
        self.btn_upload.clicked.connect(self.upload_files_to_cloud)
        self.btn_del.clicked.connect(self.del_file_from_cloud)
        self.btn_download.clicked.connect(self.download_file_from_cloud)
        self.OpenSettinsAction.triggered.connect(self.open_settings_form)
        self.change_curr_path_txt("")

    def change_curr_path_txt(self,path):
        self.curr_directory_txt.setText("ist-pnipu-bukcet/"+path)
        #pass

    def open_settings_form(self):
        self.window = QMainWindow()
        self.ui = settings_form.Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.window.show()

    def getOpenFilesAndDirs(parent=None, caption='', directory='', filter='', initialFilter='', options=None):
        def updateText():
            # update the contents of the line edit widget with the selected files
            selected = []
            for index in view.selectionModel().selectedRows():
                selected.append('"{}"'.format(index.data()))
            lineEdit.setText(' '.join(selected))

        dialog = QFileDialog(parent, windowTitle=caption)
        dialog.setFileMode(dialog.ExistingFiles)
        if options:
            dialog.setOptions(options)
        dialog.setOption(dialog.DontUseNativeDialog, True)
        if directory:
            dialog.setDirectory(directory)
        if filter:
            dialog.setNameFilter(filter)
            if initialFilter:
                dialog.selectNameFilter(initialFilter)

        # by default, if a directory is opened in file listing mode,
        # QFileDialog.accept() shows the contents of that directory, but we
        # need to be able to "open" directories as we can do with files, so we
        # just override accept() with the default QDialog implementation which
        # will just return exec_()
        dialog.accept = lambda: QDialog.accept(dialog)

        # there are many item views in a non-native dialog, but the ones displaying
        # the actual contents are created inside a QStackedWidget; they are a
        # QTreeView and a QListView, and the tree is only used when the
        # viewMode is set to QFileDialog.Details, which is not this case
        stackedWidget = dialog.findChild(QStackedWidget)
        view = stackedWidget.findChild(QListView)
        view.selectionModel().selectionChanged.connect(updateText)
        lineEdit = dialog.findChild(QLineEdit)
        # clear the line edit contents whenever the current directory changes
        dialog.directoryEntered.connect(lambda: lineEdit.setText(''))
        dialog.exec_()
        return dialog.selectedFiles()

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
            S3.upload(None,'ist-pnipu-bucket', filenames)
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
        # подсчет количества строк в таблице объектов
        row_count = self.tv_cloudStorage.model().rowCount()
        # проверка на отсутствие объектов в бакете
        if row_count != 0:
            for row in range(row_count):
                check = self.tv_cloudStorage.model().item(row, 0).checkState()
                # проверка состояния чекбокса выбора
                if check == 2:
                    file_names.append(self.tv_cloudStorage.model().index(row, 1).data())
            # проверка если один из чекбоксов поменял состояние
            if not all(item == 0 for item in file_names):
                # скачивание файлов из бакета
                S3.download('ist-pnipu-bucket', file_names, self.current_path)
                #обновление списка объектов
                self.fill_object_table(self.current_path, '')
                #вывод сообщения об успешном сохранении на локальный диск
                f.ShowMessageBox('Успешно','Файлы '+str(file_names)+' сохранены на локальный диск')
            elif self.selected_key != '':
                file_names.append(self.selected_key)
                S3.download('ist-pnipu-bucket', file_names, self.selected_key)
                self.fill_object_table(self.current_path, '')
            else:
                f.ShowMessageBox('Сохранение','Не выбраны файлы для сохранения')
        else:
            f.ShowMessageBox('Сохранение','Нет файлов для сохранения')

    def del_file_from_cloud(self):
        file_names = []
        row_count = self.tv_cloudStorage.model().rowCount()
        if row_count != 0:
            for row in range(row_count):
                check = self.tv_cloudStorage.model().item(row, 0).checkState()
                if check == 2:
                    file_names.append(self.tv_cloudStorage.model().index(row, 1).data())
            if not all(item == 0 for item in file_names):
                S3.delete('ist-pnipu-bucket', file_names, self.current_path)
                self.fill_object_table(self.current_path, '')
                f.ShowMessageBox("Удаление", 'Файлы '+str(file_names)+' , были удалены')
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

    def append_row_object_table(self, key, date, size, status):
        item0 = QStandardItem()
        item0.setCheckState(Qt.CheckState.Unchecked)
        item0.setCheckable(True)
        item1 = QStandardItem(key)
        item2 = QStandardItem(date)
        item3 = QStandardItem(size)
        item4 = QStandardItem(status)
        self.tv_cloudStorage.model().appendRow([item0, item1, item2, item3, item4])

    def fill_object_table(self, directory, delimiter):
        self.selected_key = ''
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Выбор", "Имя", "Дата", "Размер", "Состояние"])
        self.tv_cloudStorage.setModel(model)
        self.tv_cloudStorage.header().resizeSection(0, 50)
        self.tv_cloudStorage.header().resizeSection(1, 300)
        service_acc_id = f.get_val_in_local_storage('service_acc_id')
        try:
            # получение объектов из бакета
            data = S3.get_object_list('ist-pnipu-bucket', directory, delimiter)
            print("это из лок.хран - "+service_acc_id)
            for obj in data:
                key_name = obj['Key']
                object_owner = obj['Owner']['ID']
                print("это из с3 облака - "+object_owner)
                if object_owner == service_acc_id:
                    # проверка есть ли сейчас что то в переменной текущего пути
                    if self.current_path == "":
                        # проверка является ли объект папкой
                        if '/' in key_name:
                            if key_name.count('/') >= 2 or str(key_name).split('/')[1] != '':
                                # отсеивание объектов типа folder/object.jpg и.т.д
                                pass
                            else:
                                #вставка строки с данными объекта
                                self.append_row_object_table(key_name,str(obj['LastModified']),f.convert_size(obj['Size']),'облако')
                        else:
                            self.append_row_object_table(key_name, str(obj['LastModified']), f.convert_size(obj['Size']),'облако')
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
                            self.append_row_object_table(replaced_key_name, str(obj['LastModified']), f.convert_size(obj['Size']),'облако')
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
            file_names = []
            file_names.append(self.current_path+object_name)
            S3.download('ist-pnipu-bucket', file_names, object_name)
            #saved_file_path = "C:/storage/"+self.current_path+object_name
            saved_file_path = f.get_val_in_local_storage('local_path') + self.current_path + object_name
            os.startfile(saved_file_path)

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

if __name__ == '__main__':
    app = QApplication([])
    cs = CloudStorage()
    cs.show()
    app.exec_()