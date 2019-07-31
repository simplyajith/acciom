import secrets

from flask_restful import Resource
from flask_restful import reqparse

from application.common.constants import APIMessages
from application.common.response import (STATUS_CREATED, STATUS_SERVER_ERROR)
from application.common.response import api_response
from application.common.token import (login_required, token_required,
                                      generate_auth_token)
from application.helper.generatehash import generate_hash
from application.model.models import User, PersonalToken


class Login(Resource):
    @login_required
    def post(self, user_detail):
        token = generate_auth_token(user_detail)
        data = {"token": token}

        return api_response(True, "success", 200, data)


class LogOut(Resource):
    @token_required
    def post(self, session):
        delete_session = session.delete_user_session()
        if delete_session is not None:
            data = {"status": False,
                    "message": "Unable to logout",
                    "data": {"token": ""}
                    }
            return data, 500

        data = {"status": True,
                "message": "success",
                "data": {"token": ""}
                }
        return data, 200


class AddUser(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email',
                            help='This field cannot be blank',
                            required=True)
        parser.add_argument('first_name',
                            help='This field cannot be blank',
                            required=True)

        parser.add_argument('last_name',
                            help='This field cannot be blank',
                            required=True)
        parser.add_argument('password',
                            help='This field cannot be blank',
                            required=True)
        user_data = parser.parse_args()
        user = User(user_data['email'], user_data['first_name'],
                    user_data['last_name'],
                    generate_hash(user_data['password']),
                    True)
        user.save_to_db()
        data = {"status": True,
                "message": "success",
                "data": {"user_id": user.user_id}
                }
        return data, 200


class GetToken(Resource):
    """
     Class will be used to generate a unique token for the user to be used in
      jenkins and stored procedure related calls
    """

    @token_required
    def get(self, session):
        """
        Method will be a get call used to generate a token for the user and
        store that with the user reference in the PersonalToken page.

        Args:
            session (Obj): session Object will contain the user detail used to
            associate the user with the token.

        Returns: generate a token that will be associated to the user

        """
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('message',
                                help=APIMessages.PARSER_MESSAGE,
                                required=True)
            token_generation_data = parser.parse_args()
            token = secrets.token_hex()
            message = token_generation_data['message']
            user_id = session.user_id
            personal_token_obj = PersonalToken(user_id, token, message)
            personal_token_obj.save_to_db()
            payload = {"personal_access_token": token}
            return api_response(
                True, APIMessages.CREATE_RESOURCE.format('token'),
                STATUS_CREATED, payload)
        except Exception as e:
            return api_response(
                False, APIMessages.INTERNAL_ERROR, STATUS_SERVER_ERROR,
                {'error_log': str(e)})
