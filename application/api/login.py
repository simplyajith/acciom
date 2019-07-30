from flask_restful import Resource
from flask_restful import reqparse
from sqlalchemy.exc import SQLAlchemyError

from application.common.constants import APIMessages
from application.common.response import (api_response, STATUS_BAD_REQUEST,
                                         STATUS_SERVER_ERROR, STATUS_CREATED)
from application.common.token import (login_required, token_required,
                                      generate_auth_token)
from application.common.utils import (send_reset_email, verify_reset_token)
from application.helper.generatehash import generate_hash
from application.model.models import User
from index import db


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


class ForgotPassword(Resource):
    """ To handle POST API, to send Email for reseting password."""

    def post(self):
        """
        To send Email to the registered user to reset password.

        Returns:
            Standard API Response with message(returns message saying that
            Mail sent to your Email id) and http status code.
        """
        try:
            post_email_parser = reqparse.RequestParser(bundle_errors=True)
            post_email_parser.add_argument('email', required=True,
                                           type=str,
                                           help=APIMessages.PARSER_MESSAGE)
            email_data = post_email_parser.parse_args()
            user = User.query.filter_by(email=email_data['email']).first()
            if user is None:
                return api_response(False,
                                    APIMessages.EMAIL_NOT_CORRECT,
                                    STATUS_BAD_REQUEST)
            else:
                send_reset_email(user)
            return api_response(True, APIMessages.MAIL_SENT,
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


class ForgotPasswordVerifyToken(Resource):
    """To handle GET API, to verify the token provided by the user."""

    def get(self):
        """
        verify token given by the user and send user to Password Reset page.

        Returns:
            Standard API Response with message(returns message saying that
            Page to password reset) and http status code.
        """
        try:
            get_token_parser = reqparse.RequestParser()
            get_token_parser.add_argument('token', required=False,
                                          type=str,
                                          location='args')

            get_token = get_token_parser.parse_args()
            token = get_token.get("token")
            token_dic = {"token": token}
            user = verify_reset_token(token)
            if user is None:
                return api_response(False,
                                    APIMessages.INVALID_TOKEN,
                                    STATUS_BAD_REQUEST)
            else:
                return api_response(True, APIMessages.PAGE_TO_PASSWORD_RESET,
                                    STATUS_CREATED, token_dic)
        except SQLAlchemyError as e:
            db.session.rollback()
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR,
                                {'error_log': str(e)})
        except Exception as e:
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR,
                                {'error_log': str(e)})


class ResetPassword(Resource):
    """ To handle POST API,to Reset user Password."""

    def post(self):
        """
        To Reset the user password and update in database.

        Returns:
            Standard API Response with message(returns message saying that
            Password changed successfully) and http status code.
        """
        try:
            post_parser = reqparse.RequestParser(bundle_errors=True)
            post_parser.add_argument('password', required=True,
                                     type=str,
                                     help=APIMessages.PARSER_MESSAGE)
            post_parser.add_argument('confirm_password', required=True,
                                     type=str,
                                     help=APIMessages.PARSER_MESSAGE)
            post_parser.add_argument('token', required=True,
                                     type=str,
                                     help=APIMessages.PARSER_MESSAGE)
            email_data = post_parser.parse_args()
            user = verify_reset_token(email_data['token'])
            if user is None:
                return api_response(False,
                                    APIMessages.INVALID_TOKEN,
                                    STATUS_BAD_REQUEST)
            else:
                password = generate_hash(email_data['password'])
                user.password_hash = password
                user.save_to_db()
                return api_response(True, APIMessages.PASSWORD_CHANGE,
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
