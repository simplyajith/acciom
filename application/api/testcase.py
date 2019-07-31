import ast
import json

from flask import current_app as app
from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.exc import SQLAlchemyError

from application.common.constants import (APIMessages, ExecutionStatus,
                                          SupportedTestClass, SupportedDBType)
from application.common.response import (STATUS_CREATED, STATUS_SERVER_ERROR,
                                         STATUS_BAD_REQUEST)
from application.common.response import api_response
from application.common.runbysuiteid import run_by_suite_id
from application.common.token import (token_required)
from application.common.utils import (get_table_name,
                                      db_details_without_password)
from application.helper.runnerclass import (run_by_case_id,
                                            save_case_log_information)
from application.helper.runnerclasshelpers import (
    save_case_log,
    save_job_status)
from application.model.models import TestCaseLog, TestCase, DbConnection
from index import db


class TestCaseJob(Resource):
    """
    TestCaseJob Executes either particular suite or a case, based on the either
    test_case_id or suite_id and
    """

    @token_required
    def post(self, session):
        """
        Executes either particular suite or a case either by suite_id
        or case_id, returns Success reponse on Execution or error log
        in case of a error

        Args:
            session(Object): session gives user ID of the owner
            who is execution the job

        Returns: Return api response ,either successful job run or error.
        """
        try:
            user_id = session.user_id
            parser = reqparse.RequestParser()
            parser.add_argument('suite_id', type=int, required=False,
                                help=APIMessages.PARSER_MESSAGE)
            parser.add_argument('case_id', type=int, required=False,
                                help=APIMessages.PARSER_MESSAGE)
            execution_data = parser.parse_args()

            if execution_data['suite_id'] and not (execution_data['case_id']):
                run_by_suite_id(user_id, execution_data['suite_id'])
                suite_data = {"suite_id": execution_data['suite_id']}
                return api_response(True, APIMessages.RETURN_SUCCESS,
                                    STATUS_CREATED,
                                    suite_data)

            elif not (execution_data['suite_id']) \
                    and execution_data['case_id']:
                run_by_case_id(execution_data['case_id'], user_id)
                case_data = {"case_id": execution_data["case_id"]}
                return api_response(True, APIMessages.RETURN_SUCCESS,
                                    STATUS_CREATED,
                                    case_data)

            else:
                return api_response(False, APIMessages.INTERNAL_ERROR,
                                    STATUS_SERVER_ERROR)

        except Exception as e:
            app.logger.error(e)
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR)


class TestCaseSparkJob(Resource):
    """
    TestCaseSparkJob class Store log generated from sparkJob , it will reflect
    test_case ,testcaselog table
    """

    def post(self, test_case_log_id):
        """
        Accepts result from spark execution and stores result in table

        Args:
            test_case_log_id (Int): test_case_log_id of the job being executed

        Returns: Stores result in the db given by the spark job.
        """
        case_log = TestCaseLog.query.filter_by(
            test_case_log_id=test_case_log_id).first()
        case = TestCase.query.filter_by(
            test_case_id=case_log.test_case_id).first()

        spark_log_dict = request.data.decode('utf-8', 'ignore')
        parsed_log = ast.literal_eval(spark_log_dict)

        if parsed_log['result'] == 'error':
            case_log.error_log = parsed_log['exception']
            case_log.execution_status = ExecutionStatus(). \
                get_execution_status_id_by_name('error')
            case_log.save_to_db()
            case_test_status = case_log.execution_status = ExecutionStatus(). \
                get_execution_status_id_by_name('error')
            save_case_log(case_log, case_test_status)

        else:
            result_src = json.dumps(parsed_log['result']['src_to_dest'])
            result_des = json.dumps(parsed_log['result']['dest_to_src'])
            src_count = parsed_log['src_result_count']
            target_count = parsed_log["target_result_count"]
            result_count = parsed_log['result_count']

            if result_count == 0:
                case_log_execution_status = ExecutionStatus(). \
                    get_execution_status_id_by_name('pass')
                save_case_log_information(case_log, case_log_execution_status,
                                          parsed_log['src_count'][0],
                                          (src_count), None,
                                          parsed_log['dest_count'][0],
                                          (target_count), None,
                                          case_log.test_case_id)
                save_case_log(case_log, case_log_execution_status)
                save_job_status(case_log, case_log_execution_status)

            elif result_count != 0:
                case_log_execution_status = ExecutionStatus(). \
                    get_execution_status_id_by_name('fail')
                save_case_log_information(case_log, case_log_execution_status,
                                          parsed_log['src_count'][0],
                                          src_count, result_src,
                                          parsed_log['dest_count'][0],
                                          target_count,
                                          result_des, case_log.test_case_id)

                save_case_log(case_log, case_log_execution_status)
                save_job_status(case_log, case_log_execution_status)


class EditTestCase(Resource):
    """ To handle GET,PUT APIs for getting and updating tese case details """

    @token_required
    def get(self, session):
        """
        To get test case details from the data base for the user provided
        test case id.

        Args:
            session (object):By using this object we can get the user_id.

        Returns:
            Standard API Response with message(returns message saying
            that data loaded successfully) and data,http status code.
        """
        get_testcase_parser = reqparse.RequestParser()
        get_testcase_parser.add_argument('test_case_id', required=True,
                                         type=int,
                                         location='args')
        testcase_id = get_testcase_parser.parse_args()
        try:
            if testcase_id:
                test_case_id = testcase_id.get("test_case_id")
                db_obj = TestCase.query.filter_by(
                    test_case_id=test_case_id).one()
                if db_obj:
                    test_case_detail = db_obj.test_case_detail
                    source_db_id = test_case_detail["src_db_id"]
                    target_db_id = test_case_detail["target_db_id"]
                    table_names_dic = get_table_name(test_case_detail["table"])
                    DbConnection_object_src = DbConnection.query.filter_by(
                        db_connection_id=source_db_id).first()
                    DbConnection_object_target = DbConnection.query.filter_by(
                        db_connection_id=target_db_id).first()
                    DbConnection_detail_src = db_details_without_password(
                        DbConnection_object_src.db_connection_id)
                    DbConnection_detail_target = db_details_without_password(
                        DbConnection_object_target.db_connection_id)
                    if test_case_detail["column"] == {}:
                        column = ''
                    else:
                        column = test_case_detail["column"]
                    test_case_class = SupportedTestClass(). \
                        get_test_class_name_by_id(
                        db_obj.test_case_class)
                    queries = test_case_detail["query"]

                    if test_case_detail["query"] == {}:
                        src_qry = ''
                        target_qry = ''
                    else:
                        query_list = []
                        if test_case_class == "countcheck" or \
                                test_case_class == "datavalidation":
                            src_query = queries["sourceqry"]
                            target_query = queries["targetqry"]
                            query_list.append(src_query)
                            query_list.append(target_query)
                            src_qry = query_list[0]
                            target_qry = query_list[1]
                        else:
                            src_qry = 'None'
                            target_qry = queries["targetqry"]
                    payload = {"test_case_id": db_obj.test_case_id,
                               "test_case_class": test_case_class,
                               "test_status": ExecutionStatus().
                                   get_execution_status_by_id(
                                   db_obj.latest_execution_status),
                               "src_table": table_names_dic["src_table"],
                               "target_table": table_names_dic["target_table"],
                               "src_db_id": source_db_id,
                               "target_db_id": target_db_id,
                               "src_db_name": DbConnection_detail_src[
                                   "db_name"],
                               "des_db_name": DbConnection_detail_target[
                                   "db_name"],
                               "src_db_type": SupportedDBType().
                                   get_db_name_by_id(
                                   DbConnection_detail_src["db_type"]),
                               "des_db_type": SupportedDBType().
                                   get_db_name_by_id(
                                   DbConnection_detail_target["db_type"]),
                               "column": column,
                               "test_queries": test_case_detail["query"],
                               "src_qry": src_qry,
                               "des_qry": target_qry
                               }
                    return api_response(True, APIMessages.DATA_LOADED,
                                        STATUS_CREATED,
                                        payload)
                else:
                    return api_response(False,
                                        APIMessages.TEST_CASE_NOT_IN_DB.format(
                                            test_case_id),
                                        STATUS_BAD_REQUEST)
            else:
                return api_response(False,
                                    APIMessages.PASS_TESTCASEID,
                                    STATUS_BAD_REQUEST)
        except SQLAlchemyError as e:
            db.session.rollback()
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR,
                                {'error_log': str(e)})
        except Exception as e:
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR,
                                {'error_log': str(e)})

    @token_required
    def put(self, session):
        """
        To update the test case details in the database for the user provided
        test case id.

        Args:
            session (object):By using this object we can get the user_id.

        Returns:
             Standard API Response with message(returns message saying
            that test case details updated successfully) and http status code.
        """
        # TODO: Need to use save to db only at the last(after all the fileds)
        put_testcase_parser = reqparse.RequestParser(bundle_errors=True)
        put_testcase_parser.add_argument('test_case_id', required=True,
                                         type=int)
        put_testcase_parser.add_argument('src_table', type=str)
        put_testcase_parser.add_argument('target_table', type=str)
        put_testcase_parser.add_argument('src_qry', type=str)
        put_testcase_parser.add_argument('target_qry', type=str)
        put_testcase_parser.add_argument('column', type=str)
        put_testcase_parser.add_argument('src_db_id', type=int)
        put_testcase_parser.add_argument('target_db_id', type=int)
        user_test_case_detail = put_testcase_parser.parse_args()
        test_case_id = user_test_case_detail["test_case_id"]
        try:
            if test_case_id:
                db_obj = TestCase.query.filter_by(
                    test_case_id=test_case_id).first()
                del user_test_case_detail["test_case_id"]
                if db_obj:
                    testcasedetail = db_obj.test_case_detail
                    for key, value in user_test_case_detail.items():
                        if value and str(value).strip():
                            if key == 'src_db_id':
                                testcasedetail["src_db_id"] = \
                                    user_test_case_detail["src_db_id"]
                                db_obj.save_to_db()
                            if key == 'target_db_id':
                                testcasedetail["target_db_id"] = \
                                    user_test_case_detail["target_db_id"]
                                db_obj.save_to_db()
                            if key == 'src_table':
                                table = testcasedetail["table"]
                                for key in table:
                                    target_table = table[key]
                                table[user_test_case_detail['src_table']] = key
                                del table[key]
                                table[
                                    user_test_case_detail[
                                        'src_table']] = target_table
                                db_obj.save_to_db()
                            if key == "target_table":
                                table = testcasedetail["table"]
                                for key in table:
                                    table[key] = user_test_case_detail[
                                        "target_table"]
                                db_obj.save_to_db()
                            if key == "src_qry":
                                queries = testcasedetail["query"]
                                queries["sourceqry"] = user_test_case_detail[
                                    "src_qry"]
                                db_obj.save_to_db()
                            if key == "target_qry":
                                queries = testcasedetail["query"]
                                queries["targetqry"] = user_test_case_detail[
                                    "target_qry"]
                                db_obj.save_to_db()
                            if key == "column":
                                column = testcasedetail["column"]
                                if ";" and ":" in user_test_case_detail[
                                    "column"]:
                                    column = {}

                                    user_columns = user_test_case_detail[
                                        "column"].split(
                                        ";")
                                    for columnpair in user_columns:
                                        if ":" in columnpair:
                                            singlecolumn = columnpair.split(
                                                ":")
                                            column[singlecolumn[0]] = \
                                                singlecolumn[1]
                                        else:
                                            column[columnpair] = columnpair
                                    testcasedetail["column"] = column
                                elif ";" in user_test_case_detail["column"]:
                                    column = {}
                                    columns = user_test_case_detail[
                                        "column"].split(";")
                                    for singlecolumn in columns:
                                        column[singlecolumn] = singlecolumn
                                    testcasedetail["column"] = column
                                else:
                                    column = {}
                                    column[user_test_case_detail["column"]] = \
                                        user_test_case_detail["column"]
                                    testcasedetail["column"] = column
                                db_obj.save_to_db()

                    db_obj.test_case_detail = testcasedetail
                    db_obj.save_to_db()
                    return api_response(
                        True, APIMessages.TEST_CASE_DETAILS_UPDATED.format(
                            test_case_id), STATUS_CREATED)
                else:
                    return api_response(False,
                                        APIMessages.TEST_CASE_NOT_IN_DB.format(
                                            test_case_id),
                                        STATUS_BAD_REQUEST)
            else:
                return api_response(False, APIMessages.PASS_TESTCASEID,
                                    STATUS_BAD_REQUEST)

        except SQLAlchemyError as e:
            db.session.rollback()
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR,
                                {'error_log': str(e)})
        except Exception as e:
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR,
                                {'error_log': str(e)})
