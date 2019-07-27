from flask_restful import Resource
from flask_restful import reqparse

from application.common.response import api_response
from application.common.token import (login_required, token_required,
                                      generate_auth_token)
from application.helper.generatehash import generate_hash
from application.model.models import User


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
    def get(self, email):
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
