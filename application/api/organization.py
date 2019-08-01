"""File to handle Organization API calls."""
from datetime import date
from datetime import datetime
from datetime import timedelta

from flask_restful import Resource, reqparse
from sqlalchemy.exc import SQLAlchemyError

from application.common.constants import APIMessages
from application.common.response import (STATUS_SERVER_ERROR, STATUS_CREATED,
                                         STATUS_OK, STATUS_UNAUTHORIZED)
from application.common.response import api_response
from application.common.token import token_required
from application.model.models import Organization, Job, UserGroup, TestSuite, \
    Project
from index import db


class OrganizationAPI(Resource):
    """Class to handle Organization related GET, POST and PUT API."""

    @token_required
    def post(self, session):
        """
        Post call to create Organization with name.

        Args:
            session(object): User session

        Returns: Standard API Response with HTTP status code

        """
        create_org_parser = reqparse.RequestParser(bundle_errors=True)
        create_org_parser.add_argument(
            'org_name', help=APIMessages.PARSER_MESSAGE,
            required=True, type=str)
        create_org_data = create_org_parser.parse_args()
        try:
            create_organization = Organization(create_org_data['org_name'],
                                               session.user_id)
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
        """
        PUT call to Update Organization name.

        Args:
            session(object): User session

        Returns: Standard API Response with HTTP status code

        """
        update_org_parser = reqparse.RequestParser(bundle_errors=True)
        update_org_parser.add_argument(
            'org_id', help=APIMessages.PARSER_MESSAGE,
            required=True, type=int)
        update_org_parser.add_argument(
            'org_name', help=APIMessages.PARSER_MESSAGE,
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
        """
        GET call to retrieve all Organizations.

        Args:
            session(object): User session

        Returns: Standard API Response with HTTP status code
        """
        try:
            # TODO: Currently, get call will give all
            #  organizations which are active
            # TODO: Implement a logic to return organizations that user is part
            # Storing all active projects in a list
            list_of_active_orgs = Organization.query.filter_by(
                is_deleted=False).all()
            if not list_of_active_orgs:
                return api_response(
                    False, APIMessages.NO_RESOURCE.format('Organization'),
                    STATUS_OK, STATUS_UNAUTHORIZED)
            # list of projects to be returned in the response
            org_details_to_return = list()
            for each_project in list_of_active_orgs:
                org_details_to_return.append(
                    {'org_id': each_project.org_id,
                     'org_name': each_project.org_name})
            return api_response(
                True, APIMessages.SUCCESS, STATUS_OK,
                {"organization_details": org_details_to_return})
        except Exception as e:
            return api_response(
                False, APIMessages.INTERNAL_ERROR, STATUS_SERVER_ERROR,
                {'error_log': str(e)})


class DashBoardStatus(Resource):
    """ To handle GET API,to get count of active projects,users,jobs."""

    def get(self):
        """
        To get active projects,users and jobs for a particular org id.

        Returns:
            Standard API Response with message, data(count of active projects,
            users and jobs) and http status code.
        """
        try:
            get_org_parser = reqparse.RequestParser()
            get_org_parser.add_argument('org_id', required=True,
                                        type=int,
                                        location='args')
            get_org_parser.add_argument('start_time', required=False,
                                        type=str,
                                        location='args')
            get_org_parser.add_argument('end_time', required=False,
                                        type=str,
                                        location='args')
            org_detail = get_org_parser.parse_args()
            result_dic = {}

            org_obj = Organization.query.filter_by(
                org_id=org_detail["org_id"]).one()
            result_dic["org_id"] = org_obj.org_id
            result_dic["org_name"] = org_obj.org_name

            project_obj = Project.query.filter_by(
                org_id=org_detail["org_id"]).all()
            list_project_id = [each_user_grp.project_id for each_user_grp in
                               project_obj]
            active_projects = len(project_obj)
            result_dic["active_projects"] = active_projects

            user_group_obj = UserGroup.query.filter(
                UserGroup.org_id == org_detail['org_id']).distinct(
                UserGroup.user_id).all()
            list_user_id = [each_user_grp.user_id for each_user_grp in
                            user_group_obj]
            result_dic["active_users"] = len(list_user_id)

            all_project_test_suite_id_list = []
            for project_id in list_project_id:
                test_suite_object = TestSuite.query.filter_by(
                    project_id=project_id).all()
                list_test_suite_id = [each_user_grp.test_suite_id for
                                      each_user_grp
                                      in
                                      test_suite_object]

                all_project_test_suite_id_list.extend(list_test_suite_id)

            if (org_detail["start_time"] and org_detail["end_time"]):
                datetime_object_start = datetime.strptime(
                    org_detail["start_time"],
                    "%Y-%m-%d")
                datetime_object_end = datetime.strptime(
                    org_detail["end_time"],
                    "%Y-%m-%d")

                all_jobs = Job.query.filter(
                    Job.test_suite_id.in_(all_project_test_suite_id_list),
                    Job.modified_at >= datetime_object_start,
                    Job.modified_at < datetime_object_end).all()
                result_dic["active_jobs"] = len(all_jobs)
                result_dic["start_time"] = str(datetime_object_start)
                result_dic["end_time"] = str(datetime_object_end)
            else:
                current_day = date.today()
                currentday = datetime.strptime(
                    str(current_day), "%Y-%m-%d")
                current_month_first_day = date.today().replace(day=1)
                datetime_object_start = datetime.strptime(
                    str(current_month_first_day), "%Y-%m-%d")
                end_date_obj = datetime.now() + timedelta(days=1)
                all_jobs = Job.query.filter(
                    Job.test_suite_id.in_(all_project_test_suite_id_list),
                    Job.modified_at >= datetime_object_start,
                    Job.modified_at < end_date_obj).all()
                result_dic["active_jobs"] = len(all_jobs)
                result_dic["start_time"] = str(datetime_object_start)
                result_dic["end_time"] = str(currentday)

            return api_response(
                True, APIMessages.DATA_LOADED, STATUS_CREATED,
                result_dic)


        except SQLAlchemyError as e:
            db.session.rollback()
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR,
                                {'error_log': str(e)})
        except Exception as e:
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR,
                                {'error_log': str(e)})
