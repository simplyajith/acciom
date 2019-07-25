from application.common.constants import SupportedDBType
from application.model.models import DbConnection


def create_dbconnection(current_user, db_type, db_name, hostname,
                        username, project_id):
    """
    Method will either create a NewDBCOnenction or give the dbconecction id

    Args:
        current_user(Object):  user_id of the current user
        db_type(Int): db_type (mysql,mssql,postgres,oracle)
        db_name(str): db name
        hostname(str): server name
        username(str): user name

    Returns:return either a db_connection_id map to
     the arguments or create a new db_connection with the given arguments
    """
    temp_connection = DbConnection.query.filter_by(user_id=current_user,
                                                   db_type=SupportedDBType().
                                                   get_db_id_by_name(db_type),
                                                   db_name=db_name,
                                                   db_hostname=hostname,
                                                   db_username=username).first()
    if temp_connection:
        return temp_connection.db_connection_id
    else:
        temp_connection = DbConnection(
            project_id=project_id,
            user_id=current_user,
            db_connection_name=None,
            db_type=SupportedDBType().get_db_id_by_name(db_type),
            db_name=db_name,
            db_hostname=hostname,
            db_username=username,
            db_encrypted_password='None',
        )
        temp_connection.save_to_db()
        return temp_connection.db_connection_id
