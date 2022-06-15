from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from cloud_storage import CloudStorage

cs = CloudStorage()

def append_row_object_table(self, key, date, size, status):
    item0 = QStandardItem()
    item0.setCheckState(Qt.CheckState.Unchecked)
    item0.setCheckable(True)
    item1 = QStandardItem(key)
    item2 = QStandardItem(date)
    item3 = QStandardItem(size)
    item4 = QStandardItem(status)
    cs.tv_cloudStorage.model().appendRow([item0, item1, item2, item3, item4])

