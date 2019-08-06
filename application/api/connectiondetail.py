from flask_restful import Resource, reqparse

from application.common.constants import APIMessages
from application.common.response import (api_response, STATUS_SERVER_ERROR,
                                         STATUS_CREATED)
from application.common.token import (token_required)
from application.helper.connectiondetails import (select_connection,
                                                  get_db_connection,
                                                  get_case_detail)
from application.model.models import Project, TestSuite


class SelectConnection(Resource):
    """
    class to select a connection
    """

    @token_required
    def post(self, session):
        """
        Method will allow user to select connection for particular user
        Args:
            session (Obj): gives user_id of the user

        Returns:will allow user to select connection for particular user
        """
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('connection_reference',
                                help=APIMessages.PARSER_MESSAGE,
                                required=True)
            parser.add_argument('case_id_list',
                                type=list, location="json",
                                help=APIMessages.PARSER_MESSAGE)
            parser.add_argument('db_connection_id',
                                help=APIMessages.PARSER_MESSAGE,
                                required=True)
            data = parser.parse_args()
            user = session.user_id
            select_connection(data, user)

            return api_response(True, APIMessages.RETURN_SUCCESS,
                                STATUS_CREATED)

        except Exception as e:
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR,
                                {'error_log': str(e)})


class DbConnection(Resource):
    """
    Class will be a get call to give all the db_connection_ids
     associated with the project_id
    """

    @token_required
    def get(self, session):
        """
        Method will give all the db_connection_ids associated with the
        project_id which we will pass in the argument

        Returns: give all the db_connection_ids associated with the
        project_id which we will pass in the argument
        """
        try:

            db_connection_detail = reqparse.RequestParser()
            db_connection_detail.add_argument('project_id', required=False,
                                              type=int,
                                              location='args')

            project_id = db_connection_detail.parse_args()
            project_obj = Project.query.filter_by(
                project_id=project_id['project_id']).first()
            if not project_obj:
                return api_response(False, APIMessages.PROJECT_NOT_EXIST,
                                    STATUS_SERVER_ERROR)
            else:
                payload = get_db_connection(project_id['project_id'])
                return api_response(True, APIMessages.SUCCESS,
                                    STATUS_CREATED, payload)
        except Exception as e:
            return api_response(False, APIMessages.PROJECT_NOT_EXIST,
                                STATUS_SERVER_ERROR)


class CaseDetails(Resource):
    """
    Class will take all the case_ids associated with a particular
    test_Suite_id
    """

    @token_required
    def get(self, session):
        """
        Method will return all the case_ids associated with
         the particular case_id provided in the args

        Returns:return all the case_ids associated with
         the particular case_id provided in the args
        """
        try:
            suite_detail = reqparse.RequestParser()
            suite_detail.add_argument('suite_id', required=False,
                                      type=int,
                                      location='args')

            suite_id = suite_detail.parse_args()
            suite_obj = TestSuite.query.filter_by(
                test_suite_id=suite_id['suite_id']).first()
            if not suite_obj:
                return api_response(False, APIMessages.SUITE_NOT_EXIST,
                                    STATUS_SERVER_ERROR)
            else:
                payload = get_case_detail(suite_id['suite_id'])
                return api_response(True, APIMessages.SUCCESS,
                                    STATUS_CREATED, payload)
        except Exception as e:
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR)
