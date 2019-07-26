from flask import current_app as app

from application.common.constants import ExecutionStatus, SupportedTestClass
from application.common.dbconnect import dbconnection
from application.helper.countcheck import count_check
from application.helper.datavalidation import datavalidation
from application.helper.ddlcheck import ddl_check
from application.helper.duplicate import duplication
from application.helper.nullcheck import null_check
from application.helper.runnerclasshelpers import (db_details, split_table,
                                                   get_query, get_column)
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


def save_job_status(test_suite_id, user_id):
    pass
    # return job_id


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
    # print(test_case.test_suite_id)
    # test_suite_id = test_case.test_suite_id
    res = run_test(test_case, user_id)
    # run_test(test_case,user_id,test_suite)
    return {"status": True, "result": res}


def run_test(case_id, user_id):
    # run_test(case_id, user_id, test_suite_id)
    """
    This method implements the execution of job

    Args:
        case_id: test_case_id of the Case.

    Returns: Runs the job based on the testCaseClass
    """
    inprogress = ExecutionStatus().get_execution_status_id_by_name(
        'inprogress')
    save_test_status(case_id, inprogress)
    # save_job_status(suite_id, user_id)
    # use job_id in save_case_log
    case_log = save_case_log(case_id.test_case_id, user_id, None, inprogress)
    # save JOB() HERE AND ADD JOB ID TO THE CASE_LOG FIELD.
    if case_id.latest_execution_status == ExecutionStatus(). \
            get_execution_status_id_by_name('inprogress'):

        if case_id.test_case_class == SupportedTestClass(). \
                get_test_class_id_by_name('countcheck'):
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

        if case_id.test_case_class == SupportedTestClass(). \
                get_test_class_id_by_name('nullcheck'):
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
            result = null_check(target_cursor, table_name['target_table'],
                                column, query, target_detail['db_type'])

        if case_id.test_case_class == SupportedTestClass(). \
                get_test_class_id_by_name('duplicatecheck'):
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

        if case_id.test_case_class == SupportedTestClass(). \
                get_test_class_id_by_name('ddlcheck'):
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
        if case_id.test_case_class == SupportedTestClass(). \
                get_test_class_id_by_name('datavalidation'):
            result = {'res': ExecutionStatus.get_execution_status_id_by_name(
                'inprogress'), "Execution_log": None}

        if result['res'] == ExecutionStatus().get_execution_status_id_by_name(
                'pass'):
            pass_status = ExecutionStatus().get_execution_status_id_by_name(
                'pass')
            save_test_status(case_id, pass_status)
            case_log.execution_status = pass_status
            data = result['Execution_log']
            case_log.execution_log = data
            case_log.save_to_db()
            # update job table too
            # job.execution_status

        elif result[
            'res'] == ExecutionStatus(). \
                get_execution_status_id_by_name('fail'):
            fail = ExecutionStatus().get_execution_status_id_by_name('fail')
            save_test_status(case_id, fail)
            case_log.execution_status = fail
            data = result['Execution_log']
            case_log.execution_log = data
            case_log.save_to_db()
            # update job table too
            # job.execution_status

        elif result[
            'res'] == ExecutionStatus(). \
                get_execution_status_id_by_name('error'):
            error = ExecutionStatus().get_execution_status_id_by_name(
                'error')
            save_test_status(case_id, error)
            case_log.execution_status = error
            case_log.execution_log = result['Execution_log']
            case_log.save_to_db()
            # update job table too
            # job.execution_status

        elif result[
            'res'] == ExecutionStatus(). \
                get_execution_status_id_by_name('inprogress'):
            save_test_status(case_id, inprogress)
            case_log.execution_status = inprogress
            case_log.save_to_db()
            if case_id.test_case_class == SupportedTestClass(). \
                    get_test_class_id_by_name('datavalidation'):
                src_detail = db_details(
                    case_id.test_case_detail['src_db_id'])
                target_detail = db_details(
                    case_id.test_case_detail['target_db_id'])
                query = get_query(case_id.test_case_detail)
                if query == {}:
                    src_qry = ""
                    target_qry = ""
                else:
                    src_qry = query[
                        'sourceqry'] if 'sourceqry' in query else ""
                    target_qry = query[
                        'targetqry'] if 'targetqry' in query else ""

                app.logger.debug(
                    "srcqry " + src_qry + "targetqry " + target_qry)

                table_name = split_table(case_id.test_case_detail)
                datavalidation(src_detail['db_name'],
                               table_name['src_table'],
                               src_detail['db_type'],
                               target_detail['db_name'],
                               table_name['target_table'],
                               target_detail['db_type'],
                               src_detail['db_username'],
                               src_detail['db_password'],
                               src_detail['db_hostname'],
                               target_detail['db_username'],
                               target_detail['db_password'],
                               target_detail['db_hostname'],
                               src_qry, target_qry, case_log)
    return {"status": True, "test_case_log_id": case_log.test_case_log_id}
