"""File to handle Group API Operations."""
from flask_restful import Resource, reqparse
from application.common.response import (STATUS_SERVER_ERROR, STATUS_CREATED,
                                         STATUS_OK, STATUS_NOT_FOUND,
                                         STATUS_BAD_REQUEST)
from application.common.constants import APIMessages
from application.common.token import token_required
from application.model.models import (Project, Group, Permission,
                                      GroupPermission)
from application.common.response import api_response
from sqlalchemy import and_


class GroupAPI(Resource):
    """Class to handle Group related GET, POST and PUT APIs."""

    @token_required
    def post(self, session):
        """
        POST call to Create a  group.

        Args:
            session (object): User session

        Returns: Standard API Response with HTTP status code

        """
        create_group_parser = reqparse.RequestParser()
        create_group_parser.add_argument(
            'group_name', help=APIMessages.PARSER_MESSAGE, required=True,
            type=str, location='json')
        create_group_parser.add_argument(
            'org_id', help=APIMessages.PARSER_MESSAGE, required=True,
            type=int, location='json')
        create_group_parser.add_argument(
            'permission_id_list', help=APIMessages.PARSER_MESSAGE,
            required=True, type=list, location='json')
        create_group_data = create_group_parser.parse_args()
        try:
            permission_id_given_by_user = set(
                create_group_data['permission_id_list'])
            # checking if permissions are valid
            valid_permissions = check_permission_exists(
                permission_id_given_by_user)
            if isinstance(valid_permissions, tuple):
                return api_response(
                    False, APIMessages.NO_RESOURCE.format('Permission'),
                    STATUS_BAD_REQUEST,
                    {'invalid_permissions': list(valid_permissions[0])})
            # TODO: Check if org_id is valid
            # checking if group_name already exists with given org
            get_group_details = Group.query.filter(and_(
                Group.name.ilike(create_group_data['group_name']),
                Group.org_id == create_group_data['org_id'])).first()
            if get_group_details:
                return api_response(
                    False, APIMessages.RESOURCE_EXISTS.format('Group'),
                    STATUS_BAD_REQUEST)
            new_group = Group(
                name=create_group_data['group_name'],
                org_id=create_group_data['org_id'], owner_id=session.user_id)
            new_group.save_to_db()
            # add permission to group
            for each_permission in create_group_data['permission_id_list']:
                add_adroup_permission = GroupPermission(
                    org_id=create_group_data['org_id'],
                    group_id=new_group.group_id, permission_id=each_permission,
                    owner_id=session.user_id)
                add_adroup_permission.save_to_db()

            payload = {'group_name': new_group.name,
                       'group_id': new_group.group_id,
                       'permissions_granted': valid_permissions}
            return api_response(
                True, APIMessages.CREATE_RESOURCE.format('Group'),
                STATUS_CREATED, payload)
        except Exception as e:
            return api_response(
                False, APIMessages.INTERNAL_ERROR,
                STATUS_SERVER_ERROR, {'error_log': str(e)})

    @token_required
    def get(self, session):
        """
        GET call to retrieve group information.

        Args:
            session (object): User session

        Returns: Standard API Response with HTTP status code

        """
        get_group_parser = reqparse.RequestParser()
        get_group_parser.add_argument(
            'org_id', help=APIMessages.PARSER_MESSAGE,
            type=str, location='args')
        get_group_parser.add_argument(
            'project_id', help=APIMessages.PARSER_MESSAGE,
            type=str, location='args')
        get_group_data = get_group_parser.parse_args()
        payload = None
        try:
            if get_group_data['org_id'] and not get_group_data['project_id']:
                # get all groups based on org_id
                # TODO: Returns groups with permission not exceeding the User's
                #  permissions
                payload = retrieve_groups_under_org(get_group_data['org_id'])
            if get_group_data['project_id'] and not get_group_data['org_id']:
                get_project = Project.query.filter_by(
                    project_id=get_group_data['project_id']).first()
                payload = retrieve_groups_under_org(get_project.org_id)
            if payload:
                return api_response(True, APIMessages.SUCCESS, STATUS_OK,
                                    {'groups': payload})
            else:
                return api_response(
                    False, APIMessages.NO_RESOURCE.format('Group'),
                    STATUS_NOT_FOUND)
        except Exception as e:
            return api_response(
                False, APIMessages.INTERNAL_ERROR,
                STATUS_SERVER_ERROR, {'error_log': str(e)})


def retrieve_groups_under_org(org_id):
    """
    Retrieve Groups for given org Id.

    Args:
        org_id (int): Id of the organization

    Returns: list of groups with Id, Name and permission names

    """
    groups_to_send = []
    get_group = Group.query.filter_by(org_id=org_id).all()
    for each_group in get_group:
        groups_to_send.append({'group_id': each_group.group_id,
                               'name': each_group.name,
                               'permissions': []})
    for group in groups_to_send:
        get_group_permission = GroupPermission.query.filter_by(
            org_id=org_id, group_id=group['group_id']).all()
        for each_group_permission in get_group_permission:
            group['permissions'].append(
                {'permission_id': each_group_permission.permission.
                    permission_id,
                 'permission_name': each_group_permission.permission.name})
    return groups_to_send


def check_permission_exists(permission_id_given_by_user):
    """
    Check if permission Id exists in DB.

    Args:
        permission_id_given_by_user (list): List of permission Ids

    Returns: list of permission name if provided permission Ids are valid
    Tuple of invalid peermission and permission name in case on invalid
    permission Ids
    """
    # checking if permissions are valid
    check_permission = Permission.query.filter(
        Permission.permission_id.in_(list(permission_id_given_by_user))).all()
    valid_permission_list = \
        [permission.permission_id for permission in check_permission]
    permission_names_list = \
        [permission.name for permission in check_permission]
    if len(valid_permission_list) != len(permission_id_given_by_user):
        invalid_permissions = set(permission_id_given_by_user).difference(
            valid_permission_list)
        return invalid_permissions, permission_names_list
    return permission_names_list
