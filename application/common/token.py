import functools
import logging
from base64 import b64decode

from flask import current_app
from flask_restful import reqparse
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, SignatureExpired, BadSignature)

from application.common.constants import APIMessages
from application.common.response import api_response
from application.common.utils import verify_hash
from application.model.models import User

logger = logging.getLogger(__name__)

token_parser = reqparse.RequestParser(bundle_errors=True)
token_parser.add_argument("Authorization", required=True, location='headers',
                          help="Please provide 'Authorization = Bearer token'")

login_parser = reqparse.RequestParser(bundle_errors=True)
login_parser.add_argument("Authorization", str, required=True,
                          location="headers")

from application.model.models import Session


def login_required(method):
    """Validate User Credential for given method and
    store user details in User Table if not exist

    Args:
        method: method object

    Returns: method(self, user_detail) or (return 401 for Flask)

    """

    @functools.wraps(method)
    def wrapper(self):
        login_parser_args = login_parser.parse_args()
        authorization_header = login_parser_args['Authorization']
        email, password = get_credentials(authorization_header)

        user_detail = User.query.filter_by(email=email).first()

        if not user_detail:
            return api_response(False, APIMessages.INVALID_EMAIL_PASSWORD, 401)

        if not user_detail.is_verified:
            return api_response(False, APIMessages.VERIFY_USER, 401)

        if user_detail.is_deleted:
            return api_response(False, APIMessages.DELETED_USER, 401)

        if not verify_hash(password, user_detail.password_hash):
            return api_response(False, APIMessages.INVALID_EMAIL_PASSWORD, 401)

        return method(self, user_detail)

    return wrapper


def get_credentials(authorization_header):
    """Get email and password from base64 encoded authorization_header

    Args:
        authorization_header (str): Base64 encoded email:password

    Returns: email, password as 2-tuple

    """
    email, password = "", ""
    try:
        encoded_header = authorization_header.split(' ', 1)[-1]
        decoded_header = b64decode(encoded_header).decode('ascii')
        email, password = decoded_header.split(':', 1)
        return email, password
    except ValueError as e:
        logger.error(str(e))

    return email, password


def token_required(method):
    """Validate Token for given method and

    return same method with session object and **kwargs

    Args:
        method (Obj): method object with **kwargs

    Returns: (return 401 for Flask) or method(self, session=session, **kwargs)

    """

    @functools.wraps(method)
    def wrapper(self, **kwargs):
        token_parser_args = token_parser.parse_args()
        authorization_header = token_parser_args['Authorization']

        token = get_token(authorization_header)
        if not token:
            data = {"status": False,
                    "message": "Unauthorised Access",
                    "data": {}
                    }
            return data, 401

        session = verify_auth_token(token)
        if not session:
            data = {"status": False,
                    "message": "Unauthorised Access",
                    "data": {}
                    }
            return data, 401
        return method(self, session=session, **kwargs)

    return wrapper


def get_token(authorization_header):
    """Fetch Token from Authorization Header

    Args:
        authorization_header (str): Bearer eyJhbGciOiJIUzUxMiIsImV4cCI6MTU1M...

    Returns: Token i.e. eyJhbGciOiJIUzUxMiIsImV4cCI6MTU1M...

    """

    header_split = authorization_header.split(' ')
    if len(header_split) == 1:
        return header_split[0]
    if len(header_split) == 2:
        return header_split[1]
    return None


def generate_auth_token(user_detail, expiration=None):
    """Generate Auth Token for given User & Store session in session table

    Args:
        expiration (int): Time for which token should be valid

    Returns (str): Newly generated Token for given user

    """
    if not expiration:
        expiration = current_app.config['JWT_SESSION_TIME']
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    session = Session(user_detail.user_id)
    session.save_to_db()
    return s.dumps({'session_id': session.session_id,
                    'user_id': session.user_id}).decode("utf-8")


def verify_auth_token(token):
    """Verify given token against JWT & Session Table

    Args:
        token (str): Token to validate

    Returns (obj): session object for given token

    """

    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None  # valid token, but expired
    except BadSignature:
        return None  # invalid token
    session = Session.query.filter_by(session_id=data['session_id'],
                                      user_id=data['user_id']).first()
    if not session:
        return None

    return session
