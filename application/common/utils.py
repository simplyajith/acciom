from passlib.hash import pbkdf2_sha256 as sha256

from application.common.constants import APIMessages
from application.model.models import DbConnection


def validate_empty_fields(data_json, list_of_args):
    """
    Validate the fields provided by user is empty or not on request payload.

    Args:
        data_json(dict): Dictionary of payload sent by user
        list_of_args(list): list of arguments that are expected by system

    Returns(str): Message in case of empty string
    """
    for each_arg in list_of_args:
        if not (data_json[each_arg]):
            # Checking if fields are empty
            return APIMessages.EMPTY_FIELD.format(each_arg)


def get_table_name(table_names):
    """
      To generate dictinory containing source and target table names.

    Args:
        table_names(dic):Dictinory with source table name as key and target
        table name as value.

    Returns:
          Returns a dictionary contains source table and target table names
          as values for the keys src_table and target_table.
    """
    table_names_dic = {}
    for key in table_names:
        table_names_dic['src_table'] = key
        table_names_dic['target_table'] = table_names[key]
    return table_names_dic


def db_details_without_password(db_connection_id):
    """
    To generate a dictionary for data base details.

    Args:
        db_connection_id(int):data base connection id.

    Returns:
         Returns a dictionary containing data base details for a particular
         data base connection id.
    """
    db_details_list = {}
    db_obj = DbConnection.query.filter_by(
        db_connection_id=db_connection_id).first()
    db_details_list['db_connection_id'] = db_obj.db_connection_id
    db_details_list['db_type'] = db_obj.db_type
    db_details_list['db_name'] = db_obj.db_name
    db_details_list['db_hostname'] = db_obj.db_hostname
    db_details_list['db_username'] = db_obj.db_username
    return db_details_list


def verify_hash(userpassword, password_in_db):
    """
       To verify whether the password entered by the user and password in db
       are matching or not.

    Args:
        userpassword(str): Old Password entered by the user.
        password_in_db(str): Password in db.

    Returns:
        It returns true if both the passwords matches.
    """
    return sha256.verify(userpassword, password_in_db)


def generate_hash(userpassword):
    """
     To generate hash password.

    Args:
        userpassword(str):New Password entered by the user.

    Returns:
        It returns hashed password for the new password enter by the user.
    """
    return sha256.hash(userpassword)
