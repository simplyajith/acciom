import ast
import json

from flask import current_app as app
from flask import request
from flask_restful import Resource, reqparse

from application.common.constants import APIMessages, ExecutionStatus
from application.common.response import (STATUS_CREATED, STATUS_SERVER_ERROR)
from application.common.response import api_response
from application.common.runbysuiteid import run_by_suite_id
from application.common.token import (token_required)
from application.helper.runnerclass import (run_by_case_id)
from application.helper.runnerclasshelpers import save_case_log_information, \
    save_case_log
from application.model.models import TestCaseLog, TestCase


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
                                help=APIMessages.PARSER_MESSAGE.format(
                                    'suite_id'))
            parser.add_argument('case_id', type=int, required=False,
                                help=APIMessages.PARSER_MESSAGE.format(
                                    'case_id'))
            execution_data = parser.parse_args()

            if execution_data['suite_id'] and not (execution_data['case_id']):
                run_by_suite_id(user_id, execution_data['suite_id'])
                suite_data = {"suite_id": execution_data['suite_id']}
                return api_response(True, APIMessages.RETURN_SUCCESS,
                                    STATUS_CREATED,
                                    suite_data)

            elif not (execution_data['suite_id']) \
                    and execution_data['case_id']:
                print(execution_data["case_id"])
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
                                          (target_count), None)
                save_case_log(case_log, case_log_execution_status)

            elif result_count != 0:
                case_log_execution_status = ExecutionStatus(). \
                    get_execution_status_id_by_name('fail')
                save_case_log_information(case_log, case_log_execution_status,
                                          parsed_log['src_count'],
                                          src_count, result_src,
                                          parsed_log['dest_count'],
                                          target_count,
                                          result_des)

                save_case_log(case_log, case_log_execution_status)
