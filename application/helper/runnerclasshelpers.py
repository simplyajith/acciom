import ast

from application.helper.encrypt import decrypt
from application.model.models import DbConnection, TestCase, Job


def db_details(db_id):
    """
    Return db_Details as a list of the particular db_connection_id asked.
    Args:
        db_id(Int):  db_connection_id

    Returns: a list of db_Details associated with db_connection_id.

    """
    db_list = {}
    db_obj = DbConnection.query.filter_by(db_connection_id=db_id).first()
    encrypted_password = db_obj.db_encrypted_password.encode()
    decrypted = decrypt(encrypted_password)
    decrypted_password = bytes.decode(decrypted)
    db_list['db_id'] = db_obj.db_connection_id
    db_list['db_type'] = db_obj.db_type
    db_list['db_name'] = db_obj.db_name
    db_list['db_hostname'] = db_obj.db_hostname
    db_list['db_username'] = db_obj.db_username
    db_list['db_password'] = decrypted_password
    return db_list


def split_table(test_case_details):
    """
    Method to split tables from the Json stored in the test_case table.
    Args:
        test_case_details(Json): JSON from test_case table

    Returns: splited table names in dictionary

    """
    table_dict = {}
    tables = test_case_details["table"]
    for each_table in tables:
        table_dict['src_table'] = each_table
        table_dict['target_table'] = tables[each_table]
    return table_dict


def get_query(queries):
    """
    Parse the query from stored in the Json format in the case_detail of the
    test_case table
    Args:
        queries: query from Excel as Text

    Returns: Parsed queries

    """
    query = queries["query"]
    return query


def get_column(columns):
    """
    Method to retrieve columns from the Json stored in the case_details table
    of the test_case table
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
    case_log.execution_status = case_log_execution_status
    if src_log == '[]':
        src_log = None
    elif dest_log == '[]':
        dest_log = None
    spark_job_data = {"source_execution_log": src_log,
                      "dest_execution_log": dest_log,
                      "src_count": source_count,
                      "src_to_dest_count": src_to_dest,
                      "dest_count": dest_count,
                      "dest_to_src_count": dest_to_src}
    case_log.execution_log = spark_job_data
    case_log.save_to_db()


def save_case_log(case_log, case_log_execution_status):
    """
    Methods to store case_log execution details in testcase table
    Args:
        case_log(int): test_case_log_id of the test_case_log table
        case_log_execution_status(int): Execution status

    Returns: save case details to the db

    """
    case = TestCase.query.filter_by(
        test_case_id=case_log.test_case_id).first()
    case.test_status = case_log_execution_status
    case.save_to_db()


def save_job_status(case_log, case_log_execution_status):
    """
    Method will save job_status in Jobs table of the db ,it accepts case_log_id
    and case_log_Execution_Status
    Args:
        case_log(obj): case_log object of the case_log table
        case_log_execution_status(int): case_log_Execution status of the table
        in int

    Returns:

    """
    Job_obj = Job.query.filter_by(job_id=case_log.job_id).first()
    Job_obj.execution_status = case_log_execution_status
    Job_obj.save_to_db()


def args_as_list(list_args):
    """
    Method will return the list out of the arguments passed
    Args:
        list_args: accepts argument from parser

    Returns: a List

    """
    list_arg = ast.literal_eval(list_args)
    if type(list_arg) is not list:
        pass
    return list_arg
