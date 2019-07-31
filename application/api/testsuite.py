from flask import current_app as app
from flask import request
from flask_restful import reqparse, Resource

from application.common.constants import APIMessages
from application.common.response import (STATUS_CREATED, STATUS_SERVER_ERROR)
from application.common.response import api_response
from application.common.returnlog import return_all_log
from application.common.runbysuiteid import run_by_suite_id
from application.common.token import (token_required)
from application.helper.exportTestcaselog import export_test_case_log
from application.helper.returnallsuites import return_all_suites
from application.helper.runnerclasshelpers import args_as_list
from application.helper.uploadfiledb import save_file_to_db
from application.model.models import Project


class AddTestSuite(Resource):
    """
    AddTestSuite Uploads the suite
    """

    @token_required
    def post(self, session):
        """
        Method will add a suite to database

        Args:
            session(Object): contains User_id.

        Returns: Add suite to Database
        """
        parser = reqparse.RequestParser()
        parser.add_argument('sheet_name',
                            help=APIMessages.PARSER_MESSAGE,
                            required=True, type=str)
        parser.add_argument('case_id_list',
                            help=APIMessages.PARSER_MESSAGE,
                            required=True, type=args_as_list, default=[])
        parser.add_argument('suite_name',
                            help=APIMessages.PARSER_MESSAGE,
                            required=True, type=str)
        parser.add_argument('upload_and_execute',
                            help=APIMessages.PARSER_MESSAGE,
                            required=True)
        parser.add_argument('project_id',
                            help=APIMessages.PARSER_MESSAGE,
                            required=True)
        test_suite_data = parser.parse_args()
        current_user = session.user_id
        file = request.files['inputFile']
        suite_result = save_file_to_db(current_user,
                                       test_suite_data['project_id'],
                                       test_suite_data, file)
        if int(test_suite_data['upload_and_execute']) == 1:
            run_by_suite_id(current_user,
                            suite_result['suite_name'].test_suite_id)
        return api_response(True, APIMessages.ADD_DATA, STATUS_CREATED)

    @token_required
    def get(self, session):
        """
        Method will give suite details, case details  of the user based on the
        token of the user

        Args:
            session(Object): session contains user_id

        Returns: returns suite level details of associated user
        """
        try:
            get_project_id_parser = reqparse.RequestParser()
            get_project_id_parser.add_argument('project_id', required=False,
                                               type=int,
                                               location='args')
            project_id = get_project_id_parser.parse_args()
            print(project_id)
            project_obj = Project.query.filter_by(
                project_id=project_id['project_id']).first()
            if not project_obj:
                return api_response(True, APIMessages.PROJECT_NOT_EXIST,
                                    STATUS_SERVER_ERROR)
            else:
                data = {"suites": return_all_suites(project_id['project_id'])}
                return api_response(True, APIMessages.RETURN_SUCCESS,
                                    STATUS_CREATED, data)
        except Exception as e:
            app.logger.debug(str(e))
            return api_response(True, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR)


class TestCaseLogDetail(Resource):
    def get(self, test_case_log_id):
        """
        Method call will return the log of the Executed case based on its
        test_case_log_id

        Args:
            test_case_log_id(Int): test_Case_log_id of the case

        Returns: return the log of the case_log_id
        """
        try:
            log_data = {"test_case_log": return_all_log(test_case_log_id),
                        "success": True}
            return api_response(True, APIMessages.RETURN_SUCCESS,
                                STATUS_CREATED, log_data)
        except Exception as e:
            return api_response(True, APIMessages.INTERNAL_ERROR, str(e))


class ExportTestLog(Resource):
    """
    Class to Export log to Excel of the executed case based on the
     test_case_log_id
    """

    def get(self, case_log_id):
        """
        Method will Export log to Excel based on the test_case_log_id of the
        executed job

        Args:
            case_log_id:Export log to Excel based on the case_log_id

        Returns:
        """
        return export_test_case_log(case_log_id)
