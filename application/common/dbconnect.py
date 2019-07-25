import cx_Oracle
import psycopg2
import pymysql
import pyodbc

from application.common.constants import SupportedDBType


def dbconnection(db_name, db_type, host_name, db_username, db_password):
    """
    Method will return a db curor
    Args:
        db_name: database name
        db_type: database type
        host_name:db host name
        db_username: db username
        db_password: db password

    Returns: db Cursor

    """
    if db_type == SupportedDBType().get_db_id_by_name('mssql'):
        database = db_name
        connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}'
                                    ';SERVER=' + host_name +
                                    ';DATABASE=' + database +
                                    ';UID=' + db_username +
                                    ';PWD=' + db_password)
        return connection
    elif db_type == SupportedDBType().get_db_id_by_name('mysql'):
        connection = pymysql.connect(host=host_name,
                                     user=db_username,
                                     password=db_password,
                                     db=db_name)
        return connection
    elif db_type == SupportedDBType().get_db_id_by_name('postgresql'):
        connection = psycopg2.connect(host=host_name,
                                      database=db_name, user=db_username,
                                      password=db_password)
        return connection
    elif db_type == SupportedDBType().get_db_id_by_name('oracle'):
        connection = cx_Oracle.connect(
            "{0}/{1}@{2}/{3}".format(db_username, db_password,
                                     host_name, db_name))
        return connection
