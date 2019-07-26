from flask_restful import Resource, reqparse
import datetime

from application.common.response import (api_response, STATUS_OK,
                                         STATUS_SERVER_ERROR, STATUS_NOT_FOUND)
from application.common.token import token_required
from application.common.constants import (APIMessages, SupportedTestClass)
from application.model.models import ( Organization, Project, TestSuite,
                                       TestCase, TestCaseLog)


class ProjectDQI(Resource):
    """
    URL: /api/project-data-quality-index
        Returns the Projects Data Quality Index for specified time range (OR)
        for all the test suites
    Actions:
        GET:
            - Returns Data Quality Index for given project id on a test case
            type level.
    """
    dqi_name_casting = {'correcteness':'datavalidation',
                        'consistency':'ddlcheck',
                        'duplicates':'duplicatecheck', 'Null':'nullcheck',
                        'completeness':'countcheck'}
    @token_required
    def get(self, session):
        project_dql_parser = reqparse.RequestParser()
        project_dql_parser.add_argument('project_id',
                                        help=APIMessages.PARSER_MESSAGE.format(
                                             'project_id'),required=True,
                                        type=int, location='args')
        project_dql_parser.add_argument("start_date",
                                        help=APIMessages.PARSER_MESSAGE.format(
                                            'start_date'),required=False,
                                        type=str,location='args')
        project_dql_parser.add_argument("end_date",
                                        help=APIMessages.PARSER_MESSAGE.format(
                                            'end_date'),required=False,
                                        type=str,location='args')
        project_dql_args = project_dql_parser.parse_args()
        try:
            project_obj = Project.query.filter_by(project_id=project_dql_args[
                "project_id"]).first()
            if not project_obj:
                    return api_response(False,APIMessages.INVALID_PROJECT_ID,
                                        STATUS_NOT_FOUND)
            project_dql_avg , dqi_values = get_project_dqi(
                project_dql_args['project_id'], project_dql_args['start_date'],
                project_dql_args['end_date'])
            dqi_list = list()
            for key in self.dqi_name_casting.keys():
                dqi_dict = dict()
                dqi_dict["name"] = self.dqi_name_casting[key]
                dqi_dict["value"] = dqi_values[self.dqi_name_casting[key]]
                dqi_list.append(dqi_dict)
            project_dql_data = dict()
            project_dql_data['project_name'] = project_obj.project_name
            project_dql_data['project_id'] = project_obj.project_id
            project_dql_data['project_dqi_percentage'] = project_dql_avg
            project_dql_data['project_dqi_detail'] = dqi_list
            project_dql_data['start_date'] = project_dql_args['start_date']
            project_dql_data['end_date'] = project_dql_args['end_date']
            return api_response(True, APIMessages.SUCCESS, STATUS_OK,
                                project_dql_data)
        except Exception as e:
            return api_response(
                False, APIMessages.INTERNAL_ERROR, STATUS_SERVER_ERROR,
                {'error_log': str(e)})


class OrganizationDQI(Resource):
    """
    URL: /api/project-data-quality-index
        Returns the Projects Data Quality Index for specified time range (OR)
        for all the test suites
    Actions:
        GET:
            - Returns Data Quality Index for given project id on a test case
            type level.
    """
    @token_required
    def get(self,session):
        org_dql_parser = reqparse.RequestParser()
        org_dql_parser.add_argument('org_id',
                                        help=APIMessages.PARSER_MESSAGE.format(
                                            'org_id'), required=True,
                                        type=int, location='args')
        org_dql_parser.add_argument("start_date",
                                        help=APIMessages.PARSER_MESSAGE.format(
                                            'start_date'), required=False,
                                        type=str, location='args')
        org_dql_parser.add_argument("end_date",
                                        help=APIMessages.PARSER_MESSAGE.format(
                                            'end_date'), required=False,
                                        type=str, location='args')
        org_dql_args = org_dql_parser.parse_args()
        try:
            org_obj = Organization.query.filter_by(org_id=org_dql_args[
                "org_id"]).first()
            if not org_obj:
                    return api_response(False,APIMessages.INVALID_ORG_ID,
                                        STATUS_NOT_FOUND)
            project_obj_list = Project.query.filter_by(
                org_id=org_obj.org_id).all()
            project_list = list()
            for project_obj in project_obj_list:
                project_dict = dict()
                project_dql_avg, dqi_values = get_project_dqi(
                    project_obj.project_id, org_dql_args['start_date'],
                    org_dql_args['end_date'])
                project_dict['project_id']= project_obj.project_id
                project_dict['project_name'] = project_obj.project_name
                project_dict['project_dqi_percentage'] = project_dql_avg

                project_list.append(project_dict)
            org_data = dict()
            org_data['org_name']=org_obj.org_name
            org_data['org_id'] = org_obj.org_id
            org_data['start_date'] = org_dql_args['start_date']
            org_data['end_date'] = org_dql_args['end_date']
            org_data['projects'] = project_list
            return api_response(True, APIMessages.SUCCESS, STATUS_OK, org_data)
        except Exception as e:
            return api_response(False, APIMessages.INTERNAL_ERROR,
                                STATUS_SERVER_ERROR, {'error_log': str(e)})


def get_project_dqi(project_id , start_date=None, end_date=None):
    """
    Calculates the Data Quality Index for each test case type for all the
    test cases under a given Project and for the given time fream if start date
    and end date is provided.
    Args:
        project_id (int): id of the project
        start_date (str) : start date for the query
        end_date (str) : end date for the query
    Return:
        project_dql_avg
        dqi_values
    """
    test_suite_obj_list = TestSuite.query.filter_by(
        project_id=project_id).all()
    test_suite_id_list = list()
    for test_suite_obj in test_suite_obj_list:
        test_suite_id_list.append(test_suite_obj.test_suite_id)
    test_case_obj_list = TestCase.query.filter(
        TestCase.test_suite_id.in_(test_suite_id_list)).all()
    dqi_values = dict()
    for values in SupportedTestClass.supported_test_class.values():
        dqi_values[values]= list()
    for test_case_obj in test_case_obj_list:
        if start_date and end_date:
            test_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            test_end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            test_end_date += datetime.timedelta(days=1)
            test_case_log_list = TestCaseLog.query.filter_by(
                test_case_id=test_case_obj.test_case_id).filter(
                TestCase.modified_at >= test_start_date).filter(
                TestCase.modified_at <= test_end_date).all()
        else:
            test_case_log_list = TestCaseLog.query.filter_by(
                test_case_id=test_case_obj.test_case_id).all()
        for test_case_log_obj in test_case_log_list:
            if test_case_log_obj.dqi_percentage:
                dqi_values[SupportedTestClass.supported_test_class[
                    test_case_obj.test_case_class]].append(
                    test_case_log_obj.dqi_percentage)
    for key in dqi_values.keys():
        if dqi_values[key]:
            dqi_values[key]= sum(dqi_values[key]) / len(dqi_values[key])
    project_dql_avg = 0
    for key, value in dqi_values.items():
        if value:
            project_dql_avg += value
        else :
            dqi_values[key] = 0
    project_dql_avg = project_dql_avg/len(dqi_values.values())

    return project_dql_avg,dqi_values


