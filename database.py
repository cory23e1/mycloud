import psycopg2

host = '127.0.0.1'
user = 'postgres'
password = '1'
db_name = 'storage'

conn = psycopg2.connect(host = host, user = user, password = password, database = db_name)
conn.autocommit = True

class SQL():
    def __init__(self):
        pass

    def insert(self,fields,values,table):
        with conn.cursor() as cursor:
            cursor.execute(
                #"""insert into accounts (login,password,role,fio,service_acc_id,service_acc_secret_key) values ('admin','admin',6,'админ','YCAJExzQwVpHD7IyZStjN3cWP','YCPXXmij23qCXKhC43odPBhdB5p_ylLRTVSvPn85')"""
                """insert into """+table+""" ("""+str(fields).replace('[','').replace(']','').replace("'","")+""") values ("""+str(values).replace('[','').replace(']','')+""")"""
            )
            #print(cursor.fetchone())

    def select(self,table,fields='',where='',where_val=''):
        with conn.cursor() as cursor:
            if where != '' and where_val != '' and fields =='':
                cursor.execute(
                    """select * from """ + table + """ where """+where+"""='"""+where_val+"""'"""
                )
                data = cursor.fetchall()
                formated_data = []
                for item in data:
                    formated_data.append(str(item).replace(',', '').replace("'", '').replace('(', '').replace(')', ''))
                return formated_data
            elif where != '' and where_val != '' and fields!= '':
                cursor.execute(
                    """select """+str(fields).replace('[','').replace(']','')+""" from """ + table + """ where """+where+"""='"""+where_val+"""'"""
                )
                data = cursor.fetchall()
                formated_data = []
                for item in data:
                    formated_data.append(str(item).replace(',', '').replace("'", '').replace('(', '').replace(')', ''))
                return formated_data
            elif where == '' and where_val == '' and fields != '':
                cursor.execute(
                    """select """+str(fields).replace('[','').replace(']','')+""" from """ + table + """"""
                )
                data = item=cursor.fetchall()
                formated_data = []
                for item in data:
                    formated_data.append(str(item).replace(',', '').replace("'", '').replace('(', '').replace(')', ''))
                return formated_data
            else:
                cursor.execute(
                    """select * from """ + table + """"""
                )
                data = cursor.fetchall()
                return list(data)
            #cursor.fetchall()
            #return cursor.fetchall()

    #l = select('','accounts','service_acc_secret_key','id','2')
    # l = select(None,'roles','name')
    # print(l)


    #print(select('', 'roles'))

sel_from_bd = SQL.select



