from flask import current_app as app
from flask_restful import Resource, reqparse

from application.common.constants import APIMessages
from application.common.response import api_response
from application.common.token import (token_required)
# from application.common.run_by_suite_id import run_by_suite_id
from application.helper.runnerclass import (run_by_case_id)


class TestCaseJob(Resource):
    @token_required
    def post(self, session):
        """

        Returns: Suite_id or case_id of the job submitted succesfully.

        """
        try:
            user_id = session.user_id
            parser = reqparse.RequestParser()
            parser.add_argument('suite_id', type=int, required=False)
            parser.add_argument('case_id', type=int, required=False)
            data = parser.parse_args()

            if data['suite_id'] and not (data['case_id']):
                # run_by_suite_id(user_id,data['suite_id'])
                data = {"suite_id": data['suite_id']}
                return api_response(True, "success", 200, data)
            elif not (data['suite_id']) and data['case_id']:
                run_by_case_id(data['case_id'], user_id)
                data = {"case_id": data["case_id"]}
                return api_response(True, "success", 200, data)
            else:
                return api_response(False, APIMessages.INTERNAL_ERROR, 500)
        except Exception as e:
            app.logger.error(e)
            return api_response(False, APIMessages.INTERNAL_ERROR, 500)
