from flask_restful import Resource, reqparse

from application.common.response import (api_response, STATUS_OK)
from application.common.token import token_required
from application.common.constants import APIMessages
from application.model.models import Organization


class SideBarMenu(Resource):
    """
    URL: /api/sidebar-menu
        Returns the list of allowed modules for the given user for the given
        Organisation
    Actions:
        GET:
            - Returns the List of allowed permissions for the user in the given
            Organization.
    """
    @token_required
    def get(self, session):
        sidebar_menu_parser = reqparse.RequestParser()
        sidebar_menu_parser.add_argument('org_id',
                                         help=APIMessages.PARSER_MESSAGE.format(
                                             'org_id'),required=True,
                                         type=int, location='args')
        sidebar_menu_args = sidebar_menu_parser.parse_args()
        org_obj = Organization.query.filter_by(
            org_id=sidebar_menu_args['org_id']).first ()
        print(org_obj.org_name)
        sidebar_menu = dict()
        sidebar_menu["org_name"]= org_obj.org_name
        sidebar_menu["org_id"]= org_obj.org_id
        sidebar_menu["allow_modules"]= [ "user-mgt", "project-mgt",
                                         "test-suite",
                                         "list of all the module to load"]
        return api_response(True, APIMessages.SUCCESS, STATUS_OK, sidebar_menu)
