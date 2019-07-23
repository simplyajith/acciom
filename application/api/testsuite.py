import ast

from flask import request
from flask_restful import reqparse, Resource

from application.common.constants import APIMessages
from application.common.response import api_response
from application.common.token import (token_required)
from application.helper.uploadfiledb import save_file_to_db


def args_as_list(s):
    v = ast.literal_eval(s)
    if type(v) is not list:
        pass
    return v


class AddTestSuite(Resource):
    @token_required
    def post(self, session):
        """

        Args:
            session: contains User_id.

        Returns: Add suite to Database

        """
        parser = reqparse.RequestParser()
        parser.add_argument('sheet_name',
                            help='This field cannot be blank',
                            required=True, type=str)
        parser.add_argument('selected_case',
                            help='this field is required',
                            required=True, type=args_as_list, default=[]
                            )
        parser.add_argument('suite_name',
                            help='this field is required',
                            required=True,
                            type=str
                            )
        parser.add_argument('execute',
                            help='this field is required',
                            required=True)
        parser.add_argument('project_id',
                            help="this filed is required",
                            required=True)
        data = parser.parse_args()
        current_user = session.user_id
        file = request.files['inputFile']
        result = save_file_to_db(current_user, data['project_id'], data,
                                 file)
        # TODO:
        # need to use result variable to execute test (Upload and Execute)

        # if int(data['exvalue']) == 1:
        #     pass
        #     #run_by_suite_id( result['suite_name'].test_suite_id) # send current user as 1st arg
        return api_response(True, APIMessages.ADD_DATA, 200)
