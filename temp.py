# from PyQt6 import uic
# from PyQt6.QtCore import Qt
# from PyQt6.QtWidgets import QApplication, QMenu, QTreeView
# from PyQt6.QtGui import QFileSystemModel, QStandardItemModel, QStandardItem
# import s3
# import os
# import funcs
# import design
#
# #Запуск окна
#
# Form, Window = uic.loadUiType("win.ui")
# app = QApplication([])
# window = Window()
# form = Form()
# form.setupUi(window)
# window.show()
#
#
#
# #tree = QTreeView.mousePressEvent()
# model = QFileSystemModel()
# model.setRootPath("E:/storage")
# win.Ui_MainWindow().tv_localStorage.setModel(model)
# win.Ui_MainWindow().tv_localStorage.setRootIndex(model.setRootPath("E:/storage"))
#
# model2 = QStandardItemModel()
# model2.setHorizontalHeaderLabels(["","Имя","Дата","Размер","Состояние"])
#
# raw_data = s3.get_object_list('ist-pnipu-bucket')
# #print(raw_data)
#
# #добавление объектов в qtreeview
# for object in raw_data:
#     item0 = QStandardItem()
#     item0.setCheckState(Qt.CheckState.Unchecked)
#     item0.setCheckable(bool('false'))
#     item1 = QStandardItem(object['Key'])
#     item2 = QStandardItem(str(object['LastModified']))
#     item3 = QStandardItem(funcs.convert_size(object['Size']))
#     item4 = QStandardItem('облако')
#     model2.appendRow([item0, item1, item2, item3, item4])
#
# form.tv_cloudStorage.setModel(model2)
#
# def tv_cloud_double_clicked():
#     index = form.tv_cloudStorage.selectedIndexes()[1]
#     object_name = index.model().itemFromIndex(index).text()
#     s3.download('ist-pnipu-bucket',object_name)
#     print(object_name)
#
# cloud_tree =form.tv_cloudStorage
#
# def tv_cloud_right_clicked(cloud_tree, e):
#     contextMenu = QMenu(cloud_tree)
#     openAction = contextMenu.addAction("Открыть")
#     downloadAction = contextMenu.addAction("Скачать")
#     deleteAction = contextMenu.addAction("Удалить")
#     contextMenu.exec(e.globalPos())
#     if cloud_tree.button() == Qt.MouseButton.RightButton:
#         print('жопа')
#
# form.tv_cloudStorage.doubleClicked.connect(tv_cloud_double_clicked)
# #form.tv_cloudStorage.rightClicked.connect(tv_cloud_right_clicked)
# #form.tv_cloudStorage.mousePressEvent(tv_cloud_right_clicked)
#
# app.exec()
#
import sys
from PyQt5.QtWidgets import *

opened_windows = set()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.create_actions()
        opened_windows.add(self)

    def closeEvent(self, ev):
        if QMessageBox.question(self, 'Closing', 'Really close?') == QMessageBox.Yes:
            ev.accept()
            opened_windows.remove(self)
        else:
            ev.ignore()

    def create_action(self, action_callback, menu, action_name):
        action = QAction(action_name, self)
        action.triggered.connect(action_callback)
        menu.addAction(action)

    def create_actions(self):
        _file_menu = self.menuBar().addMenu('&File')
        self.create_action(self.on_new, _file_menu, '&New')
        _file_menu.addSeparator()
        self.create_action(self.on_close, _file_menu, '&Close')
        self.create_action(self.on_quit, _file_menu, '&Quit')
        self.create_action(self.on_exit, _file_menu, '&Exit')

    def on_new(self):
        win = MainWindow()
        win.show()

    def on_close(self):
        self.close()

    def on_quit(self):
        qApp.quit()

    def on_exit(self):
        qApp.exit(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    status = app.exec()
    print(len(opened_windows), ' window(s) opened')
    print('status = ', status)
    sys.exit(status)


