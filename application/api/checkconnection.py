"""File to check Database connection."""
from flask_restful import Resource, reqparse
from sqlalchemy.exc import SQLAlchemyError

from application.common.constants import APIMessages, SupportedDBType
from application.common.response import (api_response, STATUS_BAD_REQUEST,
                                         STATUS_SERVER_ERROR, STATUS_CREATED)
from application.common.token import token_required
from application.common.utils import validate_empty_fields
from application.helper.connection_check import connection_check
from index import db


class CheckConnection(Resource):
    """To handle POST method,to check the database connectivity."""

    @token_required
    def post(self, session):
        """
          Method to check database connectivity for the given database.

        Args:
            session (object):By using this object we can get the user_id.

        Returns:
             Standard API Response with message,data( it returns proper message
             either it success or false) and http status code.

        """
        check_connection_parser = reqparse.RequestParser()
        check_connection_parser.add_argument('db_type_name', required=True,
                                             type=str,
                                             help=APIMessages.PARSER_MESSAGE)
        check_connection_parser.add_argument('db_hostname', required=True,
                                             type=str,
                                             help=APIMessages.PARSER_MESSAGE)
        check_connection_parser.add_argument('db_username', required=True,
                                             type=str,
                                             help=APIMessages.PARSER_MESSAGE)
        check_connection_parser.add_argument('db_password', required=True,
                                             type=str,
                                             help=APIMessages.PARSER_MESSAGE)
        check_connection_parser.add_argument('db_name', required=True,
                                             type=str,
                                             help=APIMessages.PARSER_MESSAGE)
        try:
            db_data = check_connection_parser.parse_args()
            list_of_args = [arg.name for arg in check_connection_parser.args]
            # Checking if fields are empty
            request_data_validation = validate_empty_fields(db_data,
                                                            list_of_args)
            if request_data_validation:
                return api_response(success=False,
                                    message=request_data_validation,
                                    http_status_code=STATUS_BAD_REQUEST,
                                    data={})
            if SupportedDBType().get_db_id_by_name(
                    db_data['db_type_name']) is None:
                return api_response(success=False,
                                    message=APIMessages.DB_TYPE_NAME,
                                    http_status_code=STATUS_BAD_REQUEST,
                                    data={})
            result = connection_check(
                SupportedDBType().get_db_id_by_name(db_data['db_type_name']),
                db_data['db_hostname'],
                db_data['db_username'],
                db_data['db_password'],
                db_data['db_name'])
            if result == APIMessages.RETURN_SUCCESS:
                return api_response(True, APIMessages.CONNECTION_CREATE,
                                    STATUS_CREATED)
            else:
                return api_response(False,
                                    APIMessages.CONNECTION_CANNOT_CREATE,
                                    STATUS_CREATED)
        except SQLAlchemyError as e:
            db.session.rollback()
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR,
                                {'error_log': str(e)})
        except Exception as e:
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR,
                                {'error_log': str(e)})
