"""File to handle User Management related APIs."""
from flask_restful import reqparse, Resource
from application.common.constants import APIMessages
from application.common.response import (api_response, STATUS_OK,
                                         STATUS_CREATED, STATUS_SERVER_ERROR,
                                         STATUS_BAD_REQUEST)
from application.common.token import (token_required)
from application.model.models import (UserOrgRole, UserProjectRole, User,
                                      Organization)
from application.common.utils import generate_hash


class UserAPI(Resource):
    """API to handle User related calls."""

    @token_required
    def get(self, session):
        """
        API returns users present in given org.

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


class UserRoleAPI(Resource):
    """Class to handle POST user role API."""

    @token_required
    def post(self, session):
        """
        Post to create UserProjectRole and UserOrgRole records.

        Args:
            session (object):

        Returns: Standard API Response with HTTP status code
        """
        parser = reqparse.RequestParser()
        parser.add_argument('org_id',
                            help=APIMessages.PARSER_MESSAGE,
                            required=True, type=int, location='json')
        parser.add_argument('user_id',
                            help=APIMessages.PARSER_MESSAGE,
                            required=False, type=int, location='json')
        parser.add_argument('email_id',
                            help=APIMessages.PARSER_MESSAGE,
                            required=False, type=str, location='json')
        parser.add_argument('project_role_list',
                            help=APIMessages.PARSER_MESSAGE,
                            required=True, type=list, location='json')
        parser.add_argument('org_allowed_role_list',
                            help=APIMessages.PARSER_MESSAGE,
                            required=True, type=list, location='json')
        create_role_api_parser = parser.parse_args()
        try:
            # check if email is passed in request
            if create_role_api_parser['email_id'] and \
                    not create_role_api_parser['user_id']:
                # get user_id based on email_id
                get_user_record = User.query.filter(
                    User.email.ilike(
                        create_role_api_parser['email_id'])).first()
                if get_user_record:
                    # User record is present with given email id
                    user_id = get_user_record.user_id
                else:
                    # User record is not present for given email id.
                    # Create a new user
                    create_user_args = \
                        {'first_name': create_role_api_parser['email_id'],
                         'last_name': create_role_api_parser['email_id'],
                         'password': create_role_api_parser['email_id'],
                         'is_verified': True}
                    user_id = create_new_user(
                        create_role_api_parser['email_id'], **create_user_args)
            if create_role_api_parser['user_id'] and \
                    not create_role_api_parser['email_id']:
                user_id = create_role_api_parser['user_id']
            # Deleting all UserProjectRole records with given User and Org Id
            UserProjectRole.query.filter_by(
                org_id=create_role_api_parser['org_id'],
                user_id=user_id).delete()
            UserOrgRole.query.filter_by(
                org_id=create_role_api_parser['org_id'],
                user_id=user_id).delete()
            # add project roles
            if create_role_api_parser['project_role_list']:
                for each_project_role in \
                        create_role_api_parser['project_role_list']:
                    for each_roles_given in \
                            set(each_project_role['allowed_role_list']):
                        add_user_project_role = UserProjectRole(
                            user_id=user_id,
                            org_id=create_role_api_parser['org_id'],
                            project_id=each_project_role['project_id'],
                            role_id=each_roles_given, owner_id=session.user_id)
                        add_user_project_role.save_to_db()
            # Add Org Roles
            if create_role_api_parser['org_allowed_role_list']:
                for each_org_role in \
                        set(create_role_api_parser['org_allowed_role_list']):
                    new_user_org_role = UserOrgRole(
                        user_id=user_id,
                        org_id=create_role_api_parser['org_id'],
                        role_id=each_org_role, owner_id=session.user_id)
                    new_user_org_role.save_to_db()
            return api_response(True, APIMessages.ADD_ROLE, STATUS_CREATED)
        except Exception as e:
            return api_response(
                False, APIMessages.INTERNAL_ERROR,
                STATUS_SERVER_ERROR, {'error_log': str(e)})

    @token_required
    def get(self, session):
        """
        GET call to retrieve UserProjectRole and UserOrgRole records.

        Args:
            session (object): User Session

        Returns: Standard API Response with HTTP status code
        """
        parser = reqparse.RequestParser()
        parser.add_argument('org_id',
                            help=APIMessages.PARSER_MESSAGE,
                            required=True, type=int, location='args')
        parser.add_argument('user_id',
                            help=APIMessages.PARSER_MESSAGE,
                            required=False, type=int, location='args')
        parser.add_argument('email_id',
                            help=APIMessages.PARSER_MESSAGE,
                            required=False, type=str, location='args')
        get_role_api_parser = parser.parse_args()
        try:
            result_dict = {}
            # Checking if User Id or Email Id is mandatorily passed
            if not get_role_api_parser['user_id'] and \
                    not get_role_api_parser['email_id']:
                return api_response(False, APIMessages.EMAIL_USER,
                                    STATUS_BAD_REQUEST)
            # Checking if org id is valid
            org_validation = Organization.query.filter_by(
                org_id=get_role_api_parser['org_id'], is_deleted=False).first()
            if not org_validation:
                return api_response(
                    False, APIMessages.NO_RESOURCE.format('Organization'),
                    STATUS_BAD_REQUEST)
            # Storing user id if user id is passed
            user_id = get_role_api_parser['user_id'] \
                if get_role_api_parser['user_id'] else None
            # checking if User Id is valid
            if get_role_api_parser['user_id']:
                user_validity = User.query.filter_by(user_id=user_id,
                                                     is_deleted=False).first()
                if not user_validity:
                    return api_response(
                        False, APIMessages.NO_RESOURCE.format('User'),
                        STATUS_BAD_REQUEST)
            # Get user Id based on email Id passed
            if get_role_api_parser['email_id'] and \
                    not get_role_api_parser['user_id']:
                user_record = User.query.filter(
                    User.email.ilike(get_role_api_parser['email_id'])).first()
                if not user_record:
                    return api_response(
                        False, APIMessages.NO_RESOURCE.format('User'),
                        STATUS_BAD_REQUEST)
                user_id = user_record.user_id
                result_dict['email_id'] = user_record.email
            if get_role_api_parser['org_id'] and user_id:
                # Get Project Role list
                project_role_list = list()
                temp_dict = {}
                user_project_roles = UserProjectRole.query.filter_by(
                    org_id=get_role_api_parser['org_id'],
                    user_id=user_id).all()
                for each_project_role in user_project_roles:
                    if each_project_role.project_id not in temp_dict.keys():
                        # Add a key with value as role_id
                        temp_dict[each_project_role.project_id] = \
                            [each_project_role.role_id]
                    else:
                        temp_dict[each_project_role.project_id].append(
                            each_project_role.role_id)
                for key, value in temp_dict.items():
                    project_role_list.append({'project_id': key,
                                              'allowed_role_list': value})
                result_dict['project_role_list'] = project_role_list
                # Get Org Roles
                user_org_roles = UserOrgRole.query.filter_by(
                    org_id=get_role_api_parser['org_id'],
                    user_id=user_id).all()
                result_dict['is_org_user'] = True if user_org_roles else False
                result_dict['org_allowed_role_list'] = []
                if user_org_roles:
                    for each_user_org_role in user_org_roles:
                        result_dict['org_allowed_role_list'].append(
                            each_user_org_role.role_id)
                # Get User email
                if get_role_api_parser['user_id'] and \
                        not get_role_api_parser['email_id']:
                    user_detail = User.query.filter_by(
                        user_id=get_role_api_parser['user_id']).first()
                    result_dict['email_id'] = user_detail.email
                result_dict['org_id'] = get_role_api_parser['org_id']
                return api_response(True, APIMessages.SUCCESS, STATUS_OK,
                                    result_dict)
        except Exception as e:
            return api_response(
                False, APIMessages.INTERNAL_ERROR, STATUS_SERVER_ERROR,
                {'error_log': str(e)})


def create_new_user(email_id, **kwargs):
    """
    Method to create New User based on email_id and other args.

    Args:
        email_id (str): email Id
        **kwargs (dict): pass required arguments for User table

    Returns: User Id created from User Table
    """
    new_user_record = User(
        email=email_id.lower(), first_name=kwargs['first_name'],
        last_name=kwargs['last_name'],
        password_hash=generate_hash(kwargs['password']),
        is_verified=kwargs['is_verified'])
    new_user_record.save_to_db()
    return new_user_record.user_id
