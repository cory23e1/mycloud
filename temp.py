from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMenu, QTreeView
from PyQt6.QtGui import QFileSystemModel, QStandardItemModel, QStandardItem
import s3
import os
import funcs
import design

#Запуск окна

Form, Window = uic.loadUiType("win.ui")
app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)
window.show()



#tree = QTreeView.mousePressEvent()
model = QFileSystemModel()
model.setRootPath("E:/storage")
win.Ui_MainWindow().tv_localStorage.setModel(model)
win.Ui_MainWindow().tv_localStorage.setRootIndex(model.setRootPath("E:/storage"))

model2 = QStandardItemModel()
model2.setHorizontalHeaderLabels(["","Имя","Дата","Размер","Состояние"])

raw_data = s3.get_object_list('ist-pnipu-bucket')
#print(raw_data)

#добавление объектов в qtreeview
for object in raw_data:
    item0 = QStandardItem()
    item0.setCheckState(Qt.CheckState.Unchecked)
    item0.setCheckable(bool('false'))
    item1 = QStandardItem(object['Key'])
    item2 = QStandardItem(str(object['LastModified']))
    item3 = QStandardItem(funcs.convert_size(object['Size']))
    item4 = QStandardItem('облако')
    model2.appendRow([item0, item1, item2, item3, item4])

form.tv_cloudStorage.setModel(model2)

def tv_cloud_double_clicked():
    index = form.tv_cloudStorage.selectedIndexes()[1]
    object_name = index.model().itemFromIndex(index).text()
    s3.download('ist-pnipu-bucket',object_name)
    print(object_name)

cloud_tree =form.tv_cloudStorage

def tv_cloud_right_clicked(cloud_tree, e):
    contextMenu = QMenu(cloud_tree)
    openAction = contextMenu.addAction("Открыть")
    downloadAction = contextMenu.addAction("Скачать")
    deleteAction = contextMenu.addAction("Удалить")
    contextMenu.exec(e.globalPos())
    if cloud_tree.button() == Qt.MouseButton.RightButton:
        print('жопа')

form.tv_cloudStorage.doubleClicked.connect(tv_cloud_double_clicked)
#form.tv_cloudStorage.rightClicked.connect(tv_cloud_right_clicked)
#form.tv_cloudStorage.mousePressEvent(tv_cloud_right_clicked)

app.exec()




