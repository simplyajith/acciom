"""File to handle Project API Operations."""
from flask_restful import Resource, reqparse
from application.common.response import (STATUS_SERVER_ERROR, STATUS_CREATED,
                                         STATUS_OK)
from application.common.constants import APIMessages
from application.common.token import token_required
from application.model.models import Project
from application.common.response import api_response


class ProjectAPI(Resource):
    """Class to handle Project related GET, POST and PUT API."""

    @token_required
    def post(self, session):
        """Post call to create Project with name and organization Id."""
        create_project_parser = reqparse.RequestParser(bundle_errors=True)
        create_project_parser.add_argument(
            'project_name',
            help=APIMessages.PARSER_MESSAGE.format('project_name'),
            required=True, type=str)
        create_project_parser.add_argument(
            'organization_id',
            help=APIMessages.PARSER_MESSAGE.format('project_name'),
            required=True, type=str)
        create_project_data = create_project_parser.parse_args()
        try:
            new_project = Project(create_project_data['project_name'],
                                  create_project_data['organization_id'],
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
        """PUT call to update project name."""
        update_project_parser = reqparse.RequestParser(bundle_errors=True)
        update_project_parser.add_argument(
            'project_id', help=APIMessages.PARSER_MESSAGE.format('project_id'),
            required=True, type=int, location='args')
        update_project_parser.add_argument(
            'project_name',
            help=APIMessages.PARSER_MESSAGE.format('project_name'),
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
        """GET call to retrieve project details."""
        get_project_parser = reqparse.RequestParser()
        get_project_parser.add_argument(
            'org_id', help=APIMessages.PARSER_MESSAGE.format('org_id'),
            required=True, type=int, location='args')
        get_project_data = get_project_parser.parse_args()
        try:
            # Storing all active projects in a listr
            list_of_active_project = Project.query.filter_by(
                org_id=get_project_data['org_id'], is_deleted=False).all()
            # list of projects to be returned in the response
            projects_to_return = list()
            for each_project in list_of_active_project:
                projects_to_return.append(
                    {'project_id': each_project.project_id,
                     'project_name': each_project.project_name,
                     'org_id': each_project.org_id})
            return api_response(
                True, APIMessages.SUCCESS, STATUS_OK,
                {"projects_under_organization": projects_to_return})
        except Exception as e:
            return api_response(
                False, APIMessages.INTERNAL_ERROR,
                STATUS_SERVER_ERROR, {'error_log': str(e)})
