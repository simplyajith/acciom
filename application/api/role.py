"""File to handle Role API Operations."""
from flask_restful import Resource, reqparse
from sqlalchemy import and_

from application.common.constants import APIMessages
from application.common.response import (STATUS_SERVER_ERROR, STATUS_CREATED,
                                         STATUS_OK, STATUS_NOT_FOUND,
                                         STATUS_BAD_REQUEST)
from application.common.response import api_response
from application.common.token import token_required
from application.model.models import (Project, Role, Permission,
                                      RolePermission)


class RoleAPI(Resource):
    """Class to handle Role related GET, POST and PUT APIs."""

    @token_required
    def post(self, session):
        """
        POST call to Create a  role.

        Args:
            session (object): User session

        Returns: Standard API Response with HTTP status code

        """
        create_role_parser = reqparse.RequestParser()
        create_role_parser.add_argument(
            'role_name', help=APIMessages.PARSER_MESSAGE, required=True,
            type=str, location='json')
        create_role_parser.add_argument(
            'org_id', help=APIMessages.PARSER_MESSAGE, required=True,
            type=int, location='json')
        create_role_parser.add_argument(
            'permission_id_list', help=APIMessages.PARSER_MESSAGE,
            required=True, type=list, location='json')
        create_role_data = create_role_parser.parse_args()
        try:
            permission_id_given_by_user = set(
                create_role_data['permission_id_list'])
            # checking if permissions are valid
            valid_permissions = check_permission_exists(
                permission_id_given_by_user)
            if isinstance(valid_permissions, tuple):
                return api_response(
                    False, APIMessages.NO_RESOURCE.format('Permission'),
                    STATUS_BAD_REQUEST,
                    {'invalid_permissions': list(valid_permissions[0])})
            # TODO: Check if org_id is valid
            # checking if role_name already exists with given org
            get_role_details = Role.query.filter(and_(
                Role.name.ilike(create_role_data['role_name']),
                Role.org_id == create_role_data['org_id'])).first()
            if get_role_details:
                return api_response(
                    False, APIMessages.RESOURCE_EXISTS.format('Role'),
                    STATUS_BAD_REQUEST)
            new_role = Role(
                name=create_role_data['role_name'],
                org_id=create_role_data['org_id'],
                owner_id=session.user_id)
            new_role.save_to_db()
            # add permission to role
            for each_permission in create_role_data['permission_id_list']:
                add_role_permission = RolePermission(
                    org_id=create_role_data['org_id'],
                    role_id=new_role.role_id, permission_id=each_permission,
                    owner_id=session.user_id)
                add_role_permission.save_to_db()
            payload = {'role_name': new_role.name,
                       'role_id': new_role.role_id,
                       'permissions_granted': valid_permissions}
            return api_response(
                True, APIMessages.CREATE_RESOURCE.format('Role'),
                STATUS_CREATED, payload)
        except Exception as e:
            return api_response(
                False, APIMessages.INTERNAL_ERROR,
                STATUS_SERVER_ERROR, {'error_log': str(e)})

    @token_required
    def get(self, session):
        """
        GET call to retrieve role information.

        Args:
            session (object): User session

        Returns: Standard API Response with HTTP status code

        """
        get_role_parser = reqparse.RequestParser()
        get_role_parser.add_argument(
            'org_id', help=APIMessages.PARSER_MESSAGE,
            type=str, location='args')
        get_role_parser.add_argument(
            'project_id', help=APIMessages.PARSER_MESSAGE,
            type=str, location='args')
        get_role_data = get_role_parser.parse_args()
        payload = None
        try:
            if get_role_data['org_id'] and not get_role_data['project_id']:
                # get all roles based on org_id
                # TODO: Returns roles with permission not exceeding the User's
                #  permissions
                payload = retrieve_roles_under_org(get_role_data['org_id'])
            if get_role_data['project_id'] and not get_role_data['org_id']:
                get_project = Project.query.filter_by(
                    project_id=get_role_data['project_id']).first()
                payload = retrieve_roles_under_org(get_project.org_id)
            if payload:
                return api_response(True, APIMessages.SUCCESS, STATUS_OK,
                                    {'roles': payload})
            else:
                return api_response(
                    False, APIMessages.NO_RESOURCE.format('Role'),
                    STATUS_NOT_FOUND)
        except Exception as e:
            return api_response(
                False, APIMessages.INTERNAL_ERROR,
                STATUS_SERVER_ERROR, {'error_log': str(e)})


def retrieve_roles_under_org(org_id):
    """
    Retrieve Roles for given org Id.

    Args:
        org_id (int): Id of the organization

    Returns: list of roles with Id, Name and permission names

    """
    roles_to_send = []
    get_role = Role.query.filter_by(org_id=org_id).all()
    for each_role in get_role:
        roles_to_send.append({'role_id': each_role.role_id,
                              'name': each_role.name,
                              'permissions': []})
    for role in roles_to_send:
        get_role_permission = RolePermission.query.filter_by(
            org_id=org_id, role_id=role['role_id']).all()
        for each_role_permission in get_role_permission:
            role['permissions'].append(
                {'permission_id': each_role_permission.permission.
                    permission_id,
                 'permission_name': each_role_permission.permission.name})
    return roles_to_send


def check_permission_exists(permission_id_given_by_user):
    """
    Check if permission Id exists in DB.

    Args:
        permission_id_given_by_user (set): Set of permission Ids

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
