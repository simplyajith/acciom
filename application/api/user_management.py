from flask_restful import reqparse, Resource

from application.common.constants import APIMessages
from application.common.response import api_response, STATUS_OK
from application.common.token import (token_required)
from application.model.models import (UserOrgRole, UserProjectRole, User)


class UserAPI(Resource):
    @token_required
    def get(self, session):
        """
        This api returns users present in given org
        Args:
            session (object): Seesion Object

        Returns: API response with Users in org

        """
        parser = reqparse.RequestParser()
        parser.add_argument('org_id',
                            help=APIMessages.PARSER_MESSAGE,
                            required=True, type=int, location='args')
        user_api_parser = parser.parse_args()

        user_project_role = UserProjectRole.query.filter(
            UserProjectRole.org_id == user_api_parser['org_id']).distinct(
            UserProjectRole.user_id).all()

        user_org_role = UserOrgRole.query.filter(
            UserOrgRole.org_id == user_api_parser['org_id']).distinct(
            UserOrgRole.user_id).all()

        user_id_list_in_project = [each_user.user_id for each_user in
                                   user_project_role]
        user_id_list_in_org = [each_user.user_id for each_user in
                               user_org_role]
        user_id_list = [user_id_list_in_org, user_id_list_in_project]
        unique_user_id_list = set().union(*user_id_list)

        all_user_details = User.query.filter(
            User.user_id.in_(unique_user_id_list)).all()

        final_data = []
        for each_user in all_user_details:
            temp_dict = {}
            temp_dict['user_id'] = each_user.user_id
            temp_dict['first_name'] = each_user.first_name
            temp_dict['last_name'] = each_user.last_name
            temp_dict['email'] = each_user.email

            final_data.append(temp_dict)

        data = {"org_id": user_api_parser['org_id'],
                "users": final_data}

        return api_response(True, APIMessages.SUCCESS, STATUS_OK, data)
