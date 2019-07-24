from application.common.constants import ExecutionStatus, SupportedTestClass
from application.common.dbconnect import dbconnection
from application.helper.countcheck import count_check
from application.helper.ddlcheck import ddl_check
from application.helper.duplicate import duplication
from application.helper.nullcheck import null_check
from application.helper.runnerclasshelpers import db_details, split_table, \
    get_query, get_column
from application.model.models import TestCaseLog, TestCase


def save_test_status(test_case_id, status):
    """
    This will save TestCase status to the table
    Args:
        test_case_id: test_case_id of the case
        status: latest_execution_status of the case

    Returns: Save status of the case to db.

    """
    test_case_id.latest_execution_status = status
    test_case_id.save_to_db()
    return True


def save_case_log(test_case_id, user_id, execution_log, execution_status):
    """

    Args:
        test_case_id: test_case_id associated with log
        user_id: user_id associated with log
        execution_log: execution_log
        execution_status: execution_status of the log

    Returns:

    """
    temp_log = TestCaseLog(test_case_id=test_case_id,
                           user_id=user_id,
                           execution_log=execution_log,
                           execution_status=execution_status)
    temp_log.save_to_db()
    return temp_log


def run_by_case_id(test_case_id, user_id):
    """
    This runs the case based on its test_case_id
       Args:
           test_case_id: test_case_id of the test case provided

       Returns: Executes the case, and returns result.

       """

    test_case = TestCase.query.filter_by(test_case_id=test_case_id).first()
    res = run_test(test_case, user_id)
    return {"status": True, "result": res}


def run_test(case_id, user_id):
    """
    This method implements the execution of job
    Args:
        case_id: test_case_id of the Case.

    Returns: Runs the job based on the testCaseClass

    """
    inprogress = ExecutionStatus().get_execution_status_id_by_name(
        'inprogress')
    save_test_status(case_id, inprogress)
    case_log = save_case_log(case_id.test_case_id, user_id, None, inprogress)
    if case_id.latest_execution_status == ExecutionStatus().get_execution_status_id_by_name(
            'inprogress'):

        if case_id.test_case_class == SupportedTestClass().get_test_class_id_by_name(
                'countcheck'):
            src_detail = db_details(case_id.test_case_detail['src_db_id'])
            target_detail = db_details(
                case_id.test_case_detail['target_db_id'])
            source_cursor = dbconnection(src_detail['db_name'],
                                         src_detail['db_type'],
                                         src_detail['db_hostname'].lower(),
                                         src_detail['db_username'],
                                         src_detail['db_password']).cursor()
            target_cursor = dbconnection(target_detail['db_name'],
                                         target_detail['db_type'],
                                         target_detail['db_hostname'].lower(),
                                         target_detail['db_username'],
                                         target_detail['db_password']).cursor()

            table_name = split_table(case_id.test_case_detail)
            query = get_query(case_id.test_case_detail)
            result = count_check(source_cursor,
                                 target_cursor,
                                 table_name['src_table'],
                                 table_name['target_table'],
                                 query)

        if case_id.test_case_class == SupportedTestClass().get_test_class_id_by_name(
                'nullcheck'):  # 2nd Test
            target_detail = db_details(
                case_id.test_case_detail['target_db_id'])
            target_cursor = dbconnection(target_detail['db_name'],
                                         target_detail['db_type'],
                                         target_detail['db_hostname'].lower(),
                                         target_detail['db_username'],
                                         target_detail[
                                             'db_password']).cursor()
            table_name = split_table(case_id.test_case_detail)
            query = get_query(case_id.test_case_detail)
            column = get_column(case_id.test_case_detail)
            print("@115")
            result = null_check(target_cursor, table_name['target_table'],
                                column, query, target_detail['db_type'])

        if case_id.test_case_class == SupportedTestClass().get_test_class_id_by_name(
                'duplicatecheck'):  # 3 Test
            target_detail = db_details(
                case_id.test_case_detail['target_db_id'])
            target_cursor = dbconnection(target_detail['db_name'],
                                         target_detail['db_type'],
                                         target_detail['db_hostname'].lower(),
                                         target_detail['db_username'],
                                         target_detail[
                                             'db_password']).cursor()
            table_name = split_table(case_id.test_case_detail)
            query = get_query(case_id.test_case_detail)
            column = get_column(case_id.test_case_detail)
            result = duplication(target_cursor,
                                 table_name['target_table'],
                                 column,
                                 query, target_detail['db_type'])

        if case_id.test_case_class == SupportedTestClass().get_test_class_id_by_name(
                'ddlcheck'):
            table_name = split_table(case_id.test_case_detail)
            src_detail = db_details(case_id.test_case_detail['src_db_id'])
            target_detail = db_details(
                case_id.test_case_detail['target_db_id'])
            source_cursor = dbconnection(src_detail['db_name'],
                                         src_detail['db_type'],
                                         src_detail['db_hostname'].lower(),
                                         src_detail['db_username'],
                                         src_detail['db_password']).cursor()
            target_cursor = dbconnection(target_detail['db_name'],
                                         target_detail['db_type'],
                                         target_detail['db_hostname'].lower(),
                                         target_detail['db_username'],
                                         target_detail[
                                             'db_password']).cursor()
            result = ddl_check(source_cursor,
                               target_cursor,
                               table_name['src_table'],
                               table_name['target_table'],
                               src_detail['db_type'],
                               target_detail['db_type'])

        if result['res'] == ExecutionStatus().get_execution_status_id_by_name(
                'pass'):
            save_test_status(case_id, 1)
            case_log.execution_status = 1
            data = {"src_execution_log": result['src_value'],
                    "dest_execution_log": result['des_value']}
            case_log.execution_log = data
            case_log.save_to_db()

        elif result[
            'res'] == ExecutionStatus().get_execution_status_id_by_name(
            'fail'):
            save_test_status(case_id, 2)
            case_log.execution_status = 2
            data = {"src_execution_log": result['src_value'],
                    "dest_execution_log": result['des_value']}
            case_log.execution_log = data
            case_log.save_to_db()

        elif result[
            'res'] == ExecutionStatus().get_execution_status_id_by_name(
            'error'):
            save_test_status(case_id, 3)
            case_log.execution_status = 3
            data = {"src_execution_log": result['src_value'],
                    "dest_execution_log": result['des_value']}
            case_log.execution_log = data
            case_log.save_to_db()

    return {"status": True, "test_case_log_id": case_log.test_case_log_id}
