import ast

from application.model.models import DbConnection, TestCase


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
    """
    Parse the query from excel
    Args:
        queries: query from Excel as Text

    Returns: Parsed queries

    """
    query = queries["query"]
    print(query)
    return query


def get_column(columns):
    """

    Args:
        columns: columns as Text from Excel

    Returns: list of columns

    """

    column = columns["column"]
    column = list(column.values())
    return column


def save_case_log_information(case_log, case_log_execution_status,
                              source_count, src_to_dest, src_log,
                              dest_count, dest_to_src, dest_log):
    """
    Save log information from spark to the TestCaseLog Table
    Args:
        case_log: caselog object
        source_count: source table count
        src_to_dest: source and target table diffrence
        src_log: source log
        dest_count: target table count
        dest_to_src: target and source table diffrence
        dest_log: target table log

    Returns: Submit the log to the TestCaseLog Table

    """
    print(case_log, type(source_count), src_to_dest, src_log,
          dest_count, dest_to_src, dest_log)
    case_log.execution_status = case_log_execution_status
    if src_log == '[]':
        src_log = 'none'
    elif dest_log == '[]':
        dest_log = 'none'
    spark_job_data = {"src_execution_log": src_log,
                      "dest_execution_log": dest_log,
                      "src_count": source_count,
                      "src_to_dest_count": src_to_dest,
                      "dest_count": dest_count,
                      "dest_to_src_count": dest_to_src}
    case_log.execution_log = spark_job_data
    case_log.save_to_db()


def save_case_log(case, case_status):
    """

    Args:
        case:

    Returns:

    """
    case = TestCase.query.filter_by(
        test_case_id=case_log.test_case_id).first()
    case.test_status = case_status
    case.save_to_db()


def args_as_list(list_args):
    """

    Args:
        list_args: accepts argument from parser

    Returns: a List

    """
    list_Arg = ast.literal_eval(list_args)
    if type(list_Arg) is not list:
        pass
    return list_Arg
