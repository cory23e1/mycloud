from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import math
import mimetypes
import shelve

def get_mime(file): #Функция, определяющая MIME-тип файла, путь к которому указан в переменной file
    mimetypes.init()
    ext = u'.%s' % file.split('.')[-1]
    try:
        mime = mimetypes.types_map[ext]
    except:
        mime = False
    return mime

def get_mime_icon(mime, path):  # функция, назначающая иконку файлу. mime - MIME-тип, path - путь к файлу
   mimetype = str(mime)
   if mimetype == 'application/pdf':  # если тип PDF
      return '/.media/mime_icons/pdf.png'  # то возвращаем путь к соответствующей иконке
   elif mimetype.startswith('image'):
      return '/.media/mime_icons/image.png'
   elif mimetype.startswith('audio'):
      return '/.media/mime_icons/audio-x-generic.png'
   elif mimetype.find('application/x-font-ttf') != -1:
      return '/.media/mime_icons/font_truetype.png'
   else:
      return '/.media/mime_icons/unknown.png'

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0 Б"
   size_name = ("Б", "Кб", "Мб", "Гб", "Тб", "Пб", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])


def ShowMessageBox(title, message):
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()


def put_val_in_local_storage(key,value):
    try:
        db = shelve.open('values')
        db[key] = value
        db.close()
    except Exception:
        pass

def get_val_in_local_storage(key):
    try:
        db = shelve.open('values')
        temp = db[key]
        db.close()
        return temp
    except Exception:
        pass

def del_val_in_local_storage(key):
    db = shelve.open('values')
    del db[key]
    db.close()


