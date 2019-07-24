import cx_Oracle
import psycopg2
import pymysql
import pyodbc

from application.common.constants import SupportedDBType


def dbconnection(db, db_type, host, db_username, db_password):
    print(db_type)
    if db_type == SupportedDBType().get_db_id_by_name('mssql'):
        database = db
        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}'
                              ';SERVER=' + host + ';DATABASE=' + database +
                              ';UID=' + db_username +
                              ';PWD=' + 'Akhil@123')
        return cnxn
    elif db_type == SupportedDBType().get_db_id_by_name('mysql'):
        print("18")
        cnxn = pymysql.connect(host=host,
                               user=db_username,
                               password='acciom_password',
                               db=db)
        return cnxn
    elif db_type == SupportedDBType().get_db_id_by_name('postgresql'):
        cnxn = psycopg2.connect(host=host,
                                database=db, user=db_username,
                                password=db_password)
        return cnxn
    elif db_type == SupportedDBType().get_db_id_by_name('oracle'):
        con = cx_Oracle.connect(
            "{0}/{1}@{2}/{3}".format(db_username, db_password,
                                     host, db))
        return con

# def dest_db(target_db, dest_db_type, dest_host,
#             dest_db_username, dest_db_password):
#     if dest_db_type == 'sqlserver':
#         cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}'
#                               ';SERVER=' + dest_host +
#                               ';DATABASE=' + target_db +
#                               ';UID=' + dest_db_username +
#                               ';PWD=' + dest_db_password)
#         return cnxn
#     elif dest_db_type == 'mysql':
#         cnxn = pymysql.connect(host=dest_host,
#                                user=dest_db_username,
#                                password=dest_db_password,
#                                db=target_db)
#         return cnxn
#     elif dest_db_type == 'postgres':
#         cnxn = psycopg2.connect(host=dest_host,
#                                 database=target_db,
#                                 user=dest_db_username,
#                                 password=dest_db_password)
#         return cnxn
#
#     elif dest_db_type == 'oracle':
#         con = cx_Oracle.connect(
#             "{0}/{1}@{2}/{3}".format(dest_db_username, dest_db_password,
#                                      dest_host, target_db))
#         return con
