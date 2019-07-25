"""File to handle OraganizationAPI calls."""
from flask_restful import Resource, reqparse
from application.common.response import (STATUS_SERVER_ERROR, STATUS_CREATED,
                                         STATUS_OK)
from application.common.constants import APIMessages
from application.common.token import token_required
from application.model.models import Organization
from application.common.response import api_response


class OrganizationAPI(Resource):
    """Class to handle Organization related GET, POST and PUT API."""

    @token_required
    def post(self, session):
        """Post call to create Organization with name and organization Id."""
        create_org_parser = reqparse.RequestParser(bundle_errors=True)
        create_org_parser.add_argument(
            'org_name', help=APIMessages.PARSER_MESSAGE.format('org_name'),
            required=True, type=str)
        create_org_data = create_org_parser.parse_args()
        try:
            create_organization = Organization(
                org_name=create_org_data['org_name'], owner_id=session.user_id)
            create_organization.save_to_db()
            organization_data = {'org_id': create_organization.org_id,
                                 'org_name': create_organization.org_name}
            return api_response(
                True, APIMessages.CREATE_RESOURCE.format('Organization'),
                STATUS_CREATED, organization_data)
        except Exception as e:
            return api_response(
                False, APIMessages.INTERNAL_ERROR, STATUS_SERVER_ERROR,
                {'error_log': str(e)})

    @token_required
    def put(self, session):
        """PUT call to Update Organization name."""
        update_org_parser = reqparse.RequestParser(bundle_errors=True)
        update_org_parser.add_argument(
            'org_id', help=APIMessages.PARSER_MESSAGE.format('org_id'),
            required=True, type=int, location='args')
        update_org_parser.add_argument(
            'org_name', help=APIMessages.PARSER_MESSAGE.format('org_name'),
            required=True, type=str)
        update_org_data = update_org_parser.parse_args()
        try:
            current_org = Organization.query.filter_by(
                org_id=update_org_data['org_id']).first()
            current_org.org_name = update_org_data['org_name']
            current_org.save_to_db()
            return api_response(
                True, APIMessages.UPDATE_RESOURCE.format('Organization'),
                STATUS_OK)
        except Exception as e:
            return api_response(
                False, APIMessages.INTERNAL_ERROR, STATUS_SERVER_ERROR,
                {'error_log': str(e)})

    @token_required
    def get(self, session):
        """PUT call to Update Organization name."""
        try:
            # TODO: Currently, get call will give all
            #  organizations which are active
            # TODO: Implement a logic to return organizations that user is part
            # Storing all active projects in a list
            list_of_active_orgs = Organization.query.filter_by(
                is_deleted=False).all()
            # list of projects to be returned in the response
            org_details_to_return = list()
            for each_project in list_of_active_orgs:
                org_details_to_return.append(
                    {'org_id': each_project.org_id,
                     'org_name': each_project.org_name})
            return api_response(
                True, APIMessages.SUCCESS, STATUS_OK,
                {"organization_details_for_user": org_details_to_return})
        except Exception as e:
            return api_response(
                False, APIMessages.INTERNAL_ERROR, STATUS_SERVER_ERROR,
                {'error_log': str(e)})
