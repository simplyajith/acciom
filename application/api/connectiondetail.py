from flask_restful import Resource, reqparse

from application.common.constants import APIMessages
from application.common.response import (api_response, STATUS_SERVER_ERROR)
from application.common.token import (token_required)
from application.helper.connectiondetails import (connection_details,
                                                  select_connection)
from application.helper.runnerclasshelpers import args_as_list


class ConnectionDetails(Resource):
    """
    class to show all the connections associated with the suite_id
    """

    @token_required
    def get(self, session):
        try:
            get_connection_detail = reqparse.RequestParser()
            get_connection_detail.add_argument('suite_id', required=False,
                                               type=int,
                                               location='args')
            connection_detail = get_connection_detail.parse_args()
            current_user = session.user_id
            payload = connection_details(current_user,
                                         connection_detail['suite_id'])
            return api_response(True, "success", APIMessages.SUCCESS, payload)
        except Exception as e:
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR,
                                {'error_log': str(e)})


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
                                help=APIMessages.PARSER_MESSAGE,
                                required=True,
                                type=args_as_list, default=[])
            parser.add_argument('db_connection_id',
                                help=APIMessages.PARSER_MESSAGE,
                                required=True)
            data = parser.parse_args()
            user = session.user_id
            select_connection(data, user)

            return api_response("success", True, 200,
                                APIMessages.RETURN_SUCCESS)

        except Exception as e:
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR,
                                {'error_log': str(e)})
