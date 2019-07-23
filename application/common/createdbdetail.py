from application.common.constants import SupportedDBType
from application.model.models import DbConnection


def create_dbconnection(current_user, db_type, db, hostname, username):
    """

    Args:
        current_user:  user_id of the current user
        db_type: db_type (mysql,mssql,postgres,oracle)
        db: db name
        hostname: servername
        username: user name

    Returns:return either a db_connection_id map to the arguments or create a
    # new db_connection with the given arguments

    """
    temp = DbConnection.query.filter_by(user_id=current_user,
                                        db_type=SupportedDBType().get_db_id_by_name(
                                            db_type),
                                        db_name=db,
                                        db_hostname=hostname,
                                        db_username=username).first()
    if (temp):
        return temp.db_connection_id
    else:
        temp = DbConnection(
            project_id=1,
            user_id=current_user,
            db_connection_name=None,
            db_type=SupportedDBType().get_db_id_by_name(db_type),
            db_name=db,
            db_hostname=hostname,
            db_username=username,
            db_encrypted_password='None',
        )
        temp.save_to_db()
        return temp.db_connection_id
