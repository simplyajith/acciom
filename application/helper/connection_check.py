import cx_Oracle
import psycopg2
import pymysql
import pyodbc
from sqlalchemy import exc

from application.common.constants import APIMessages, SupportedDBType, \
    GenericStrings
from application.common.response import api_response, STATUS_SERVER_ERROR


def connection_check(db_type_id, db_hostname, db_username, db_password,
                     db_name):
    """
    Helper method to check the database connectivity for the given database
    details.

    Args:
        db_type_id(int): type of the database
        db_hostname(str): database hostname
        db_username(str): database username
        db_password(str): database password
        db_name(str): database name
    Returns(str):
        Returns success only if connection can be establish
    """
    try:
        # cnxn is a connection object
        if db_type_id == SupportedDBType().get_db_id_by_name("mysql"):
            cnxn = pymysql.connect(host=db_hostname, user=db_username,
                                   password=db_password, db=db_name)
            cursor = cnxn.cursor()
            if cursor:
                return APIMessages.RETURN_SUCCESS
        elif db_type_id == SupportedDBType().get_db_id_by_name("mssql"):
            server = db_hostname
            database = db_name
            username = db_username
            password = db_password
            # This code can handle Oracle Driver 17
            # If other version 13 is given, code will fail
            # TODO: Need to implement an approach that takes driver version
            #  based on user input
            cnxn = pyodbc.connect(
                'DRIVER={0}'.format(GenericStrings.ORACLE_DRIVER) +
                ';SERVER=' + server +
                ';DATABASE=' + database +
                ';UID=' + username + ';PWD=' + password)
            cursor = cnxn.cursor()
            if cursor:
                return APIMessages.RETURN_SUCCESS
        elif db_type_id == SupportedDBType().get_db_id_by_name("postgresql"):
            cnxn = psycopg2.connect(host=db_hostname, database=db_name,
                                    user=db_username,
                                    password=db_password)
            cursor = cnxn.cursor()
            if cursor:
                return APIMessages.RETURN_SUCCESS
        elif db_type_id == SupportedDBType().get_db_id_by_name("oracle"):
            cnxn = cx_Oracle.connect(
                "{0}/{1}@{2}/{3}".format(db_username, db_password, db_hostname,
                                         db_name))
            cursor = cnxn.cursor()
            if cursor:
                return APIMessages.RETURN_SUCCESS
    except exc.DatabaseError as e:
        return api_response(False, APIMessages.INTERNAL_ERROR,
                            STATUS_SERVER_ERROR,
                            {'error_log': str(e)})
    except Exception as e:
        return api_response(False, APIMessages.INTERNAL_ERROR,
                            STATUS_SERVER_ERROR,
                            {'error_log': str(e)})
