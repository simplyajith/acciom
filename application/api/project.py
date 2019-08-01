"""File to handle Project API Operations."""
from flask_restful import Resource, reqparse

from application.common.constants import APIMessages
from application.common.response import (STATUS_SERVER_ERROR, STATUS_CREATED,
                                         STATUS_OK, STATUS_UNAUTHORIZED)
from application.common.response import api_response
from application.common.token import token_required
from application.model.models import Project, UserOrgRole


class ProjectAPI(Resource):
    """Class to handle Project related GET, POST and PUT API."""

    @token_required
    def post(self, session):
        """
        Post call to create Project with name and organization Id.

        Args:
            session(object): User session

        Returns: Standard API Response with HTTP status code

        """
        create_project_parser = reqparse.RequestParser(bundle_errors=True)
        create_project_parser.add_argument(
            'project_name',
            help=APIMessages.PARSER_MESSAGE,
            required=True, type=str)
        create_project_parser.add_argument(
            'org_id',
            help=APIMessages.PARSER_MESSAGE,
            required=True, type=int)
        create_project_data = create_project_parser.parse_args()
        try:
            new_project = Project(create_project_data['project_name'],
                                  create_project_data['org_id'],
                                  session.user_id)
            new_project.save_to_db()
            project_payload = {'project_name': new_project.project_name,
                               'project_id': new_project.project_id,
                               'org_id': new_project.org_id}
            return api_response(True,
                                APIMessages.CREATE_RESOURCE.format('Project'),
                                STATUS_CREATED, project_payload)
        except Exception as e:
            return api_response(
                False, APIMessages.INTERNAL_ERROR, STATUS_SERVER_ERROR,
                {'error_log': str(e)})

    @token_required
    def put(self, session):
        """
        PUT call to update project name.

        Args:
            session(object): User session

        Returns: Standard API Response with HTTP status code

        """
        update_project_parser = reqparse.RequestParser(bundle_errors=True)
        update_project_parser.add_argument(
            'project_id', help=APIMessages.PARSER_MESSAGE,
            required=True, type=int)
        update_project_parser.add_argument(
            'project_name',
            help=APIMessages.PARSER_MESSAGE,
            required=True, type=str)
        update_project_data = update_project_parser.parse_args()
        try:

            current_project = Project.query.filter_by(
                project_id=update_project_data['project_id']).first()
            current_project.project_name = update_project_data['project_name']
            current_project.save_to_db()
            return api_response(True,
                                APIMessages.UPDATE_RESOURCE.format('Project'),
                                STATUS_OK)
        except Exception as e:
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR, {'error_log': str(e)})

    @token_required
    def get(self, session):
        """
        GET call to retrieve project details.

        Args:
            session(object): User session

        Returns: Standard API Response with HTTP status code

        """
        get_project_parser = reqparse.RequestParser()
        get_project_parser.add_argument(
            'org_id', help=APIMessages.PARSER_MESSAGE,
            required=True, type=int, location='args')
        get_project_data = get_project_parser.parse_args()
        try:
            # TODO: Check if organization is active and called has access
            # Storing all active projects in a list
            list_of_active_project = Project.query.filter_by(
                org_id=get_project_data['org_id'], is_deleted=False).all()
            if not list_of_active_project:
                return api_response(False,
                                    APIMessages.NO_RESOURCE.format('Project'),
                                    STATUS_UNAUTHORIZED)
            # dict of org and list of projects to be returned in the response
            projects_to_return = dict()
            # list of projects to be sent in response
            project_details_list = list()
            organization_id_in_database = None
            # check if user has all org level permissions
            user_roles = UserOrgRole.query.filter_by(
                user_id=session.user_id,
                org_id=get_project_data['org_id']).first()
            for each_project in list_of_active_project:
                # Store each project details in a list
                project_details_list.append(
                    {'project_id': each_project.project_id,
                     'project_name': each_project.project_name})
                # Store Organization Id
                organization_id_in_database = each_project.org_id
            projects_to_return.update(
                {'org_id': organization_id_in_database,
                 'is_org_user': True if user_roles else False,
                 'project_details': project_details_list})
            return api_response(
                True, APIMessages.SUCCESS, STATUS_OK,
                {"projects_under_organization": projects_to_return})
        except Exception as e:
            return api_response(
                False, APIMessages.INTERNAL_ERROR,
                STATUS_SERVER_ERROR, {'error_log': str(e)})
