from application.model.models import DbConnection


def db_details(db_id):
    """

    Args:
        db_id:  db_connection_id

    Returns: a list of db_Details associated with db_connection_id.

    """
    db_list = {}
    """
    :return: returns the db_type,db_name,db_username,
    db_hostname,db_password based on
    db_id (foreign Key)
    """
    db_obj = DbConnection.query.filter_by(db_connection_id=db_id).first()
    db_list['db_id'] = db_obj.db_connection_id
    db_list['db_type'] = db_obj.db_type
    db_list['db_name'] = db_obj.db_name
    db_list['db_hostname'] = db_obj.db_hostname
    db_list['db_username'] = db_obj.db_username
    db_list['db_password'] = db_obj.db_encrypted_password
    print(db_list)

    return db_list


def split_table(test_case_details):
    """

    Args:
        test_case_details: JSON from test_case table

    Returns: splited table names in dictionary

    """
    lst1 = {}
    tables = test_case_details["table"]
    for key in tables:
        lst1['src_table'] = key
        lst1['target_table'] = tables[key]
    return lst1


def get_query(queries):
    print("51", queries)
    query = queries["query"]
    print(query)
    return query


def get_column(columns):
    '''
    :param columns:
    :return: list of target columns only as a list used in case of nullcheck
    and duplicate check
    '''

    column = columns["column"]
    column = list(column.values())
    return column
