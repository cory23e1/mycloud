from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import requests
import register_form
import database
import funcs as f
import auth_form


class Register(register_form.Ui_MainWindow, QMainWindow):
    IAM_TOKEN = ''
    folder_id = ''

    def __init__(self):
        super(Register, self).__init__()
        self.setupUi(self)
        self.register_btn.clicked.connect(self.add_acc_to_bd)
        self.load_roles_from_bd()

    def open_auth_form(self):
        self.window = QMainWindow()
        self.ui = auth_form.Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.window.show()

    def load_roles_from_bd(self):
        db = database
        select = db.sel_from_bd
        roles = select(None,'roles','name')
        #print(roles)
        self.role_cmb.addItems(roles)

    def add_acc_to_bd(self):
        try:
            iam = Register.get_ouath_token('')
            service_acc_name = self.login_txt.text()
            password = self.password_txt.text()
            role = self.role_cmb.currentIndex()+1
            fio = self.fio_txt.text()
            created_acc = self.create_new_service_acc(iam, service_acc_name, '')
            service_acc_id = created_acc['accessKey']['serviceAccountId']
            static_key_id = created_acc['accessKey']['keyId']
            static_secret_key = created_acc['secret']
            #print(service_acc_id)
            fields = ['login', 'password', 'role', 'fio', 'service_acc_id','static_key_id', 'static_secret_key']
            values = [service_acc_name,password,role,fio,service_acc_id,static_key_id,static_secret_key]
            database.SQL.insert('',fields,values,'accounts')
            f.ShowMessageBox('Успешно','Пользователь '+service_acc_name+' успешно зарегистрирован')
            self.open_auth_form()
            self.close()
        except Exception as error:
            f.ShowMessageBox('Ошибка',str(error))
        #db.dat = database

        #print(db.dat.SQL.select('','accounts'))

    def get_ouath_token(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = '{"yandexPassportOauthToken":"AQAAAABgj_I9AATuwUjVfFUeS0sZpzmfLz7UmPI"}'
        response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', headers=headers, data=data)
        IAM_TOKEN = response.json()['iamToken']
        return IAM_TOKEN

   #{"name": "ggfgu", "description": "uioyh8uoyhu", "folderId": "b1g26uu7lpnb4jo3ph8v",
   # "rolesFolderId": "b1g26uu7lpnb4jo3ph8v", "roles": ["storage.uploader", "storage.viewer"]}

    def create_new_service_acc(self,iam_token,login,description):
        headers = {'Authorization': f'Bearer {iam_token}'}
        #cоздание сервисного аккаунта
        create_acc_json = {
            'folderId': 'b1g26uu7lpnb4jo3ph8v',
            'name': login,  # Имя нового сервис.акка
            'description': description,  # комментарий
            'roleId': 'storage-viewer'
        }
        create_acc_response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/serviceAccounts', headers=headers,json=create_acc_json)
        service_acc_id = create_acc_response.json()['response']['id']
        # присвоение роли сервисному аккаунту
        set_role_json = {
            "accessBindingDeltas": [{
                "action": "ADD",
                "accessBinding": {
                    "roleId": 'storage.editor',
                    "subject": {
                        "id": service_acc_id,
                        "type": "serviceAccount"
                        }
                    }
                }
            ]
        }
        set_role_response = requests.post('https://resource-manager.api.cloud.yandex.net/resource-manager/v1/folders/b1g26uu7lpnb4jo3ph8v:updateAccessBindings', headers=headers, json=set_role_json)
        #создание статического ключа доступа
        get_static_key_json = {
            "serviceAccountId": service_acc_id,
            "description": "this key is for my bucket"
        }
        get_static_key_response = requests.post('https://iam.api.cloud.yandex.net/iam/aws-compatibility/v1/accessKeys', headers=headers,json=get_static_key_json)
        return get_static_key_response.json()

if __name__ == '__main__':
    app = QApplication([])
    reg = Register()
    reg.show()
    app.exec_()


