from flask import current_app as app
from flask import request
from flask_restful import reqparse, Resource

from application.common.constants import APIMessages
from application.common.response import api_response
from application.common.returnlog import return_all_log
from application.common.runbysuiteid import run_by_suite_id
from application.common.token import (token_required)
from application.helper.exportTestcaselog import export_test_case_log
from application.helper.returnallsuites import return_all_suites
from application.helper.runnerclasshelpers import args_as_list
from application.helper.uploadfiledb import save_file_to_db


class AddTestSuite(Resource):
    """
    AddTestSuite Uploads the suite
    """

    @token_required
    def post(self, session):
        """
        Args:
            session: contains User_id.

        Returns: Add suite to Database

        """
        parser = reqparse.RequestParser()
        parser.add_argument('sheet_name',
                            help=APIMessages.PARSER_MESSAGE.format(
                                'sheet_name'),
                            required=True, type=str)
        parser.add_argument('selected_case',
                            help=APIMessages.PARSER_MESSAGE.format(
                                'selected_case'),
                            required=True, type=args_as_list, default=[])
        parser.add_argument('suite_name',
                            help=APIMessages.PARSER_MESSAGE.format(
                                'suite_name'),
                            required=True, type=str)
        parser.add_argument('execute',
                            help=APIMessages.PARSER_MESSAGE.format('execute'),
                            required=True)
        parser.add_argument('project_id',
                            help=APIMessages.PARSER_MESSAGE.format(
                                "project_id"),
                            required=True)
        test_suite_data = parser.parse_args()
        current_user = session.user_id
        file = request.files['inputFile']
        suite_result = save_file_to_db(current_user,
                                       test_suite_data['project_id'],
                                       test_suite_data, file)
        if int(test_suite_data['execute']) == 1:
            run_by_suite_id(current_user,
                            suite_result['suite_name'].test_suite_id)
        return api_response(True, APIMessages.ADD_DATA, 201)

    @token_required
    def get(self, session):
        """

        Args:
            session: session contains user_id

        Returns: returns suite level details of associated user

        """
        try:
            uid = session.user_id
            data = {"suites": return_all_suites(uid)}
            return api_response(True, "success", 200, data)

        except Exception as e:
            app.logger.debug(str(e))
            api_response(True, APIMessages.INTERNAL_ERROR, 200)


class TestCaseLogDetail(Resource):
    def get(self, test_case_log_id):
        """
        get call will return the log of the case_log_id.
        Args:
            test_case_log_id: test_Case_log_id of the case

        Returns: return the log of the case_log_id

        """
        return {"test_case_log": return_all_log(test_case_log_id),
                "success": True}


class ExportTestLog(Resource):
    """
    Class to Export log to Excel
    """

    def get(self, case_log_id):
        """

        Args:
            case_log_id:Export log to Excel based on the case_log_id

        Returns:

        """
        return export_test_case_log(case_log_id)
