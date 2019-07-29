from application.common.constants import ExecutionStatus
from application.common.constants import SupportedTestClass
from application.model.models import TestSuite


def return_all_suites(user_id):
    """
    Method that returns all the suite, case details associated with the user.
    Args:
        user_id: user_id of the api caller

    Returns: returns suite details and test_case details of the user

    """

    def test_log_to_json(case_log_id):
        return {
            'test_case_log_id': case_log_id.test_case_log_id,
            'test_execution_status': case_log_id.execution_status,
            'executed_at': str(case_log_id.modified_at)[0:19]
        }

    def test_case_to_json(case_id):
        """
        Method will provide testcase table details as json for
         particular case id
        Args:
            case_id (int): case_id associated with the suite

        Returns:will provide testcase table details as json for
         particular case id

        """
        return {
            'test_case_id': case_id.test_case_id,
            'test_class_name': SupportedTestClass().get_test_class_name_by_id(
                case_id.test_case_class),
            'test_class_id': case_id.test_case_class,
            'test_status': ExecutionStatus().get_execution_status_by_id(
                case_id.latest_execution_status),
            'test_case_log_list': list(map(lambda each_case:
                                           test_log_to_json(each_case),
                                           case_id.test_case_log))
        }

    def test_suite_to_json(suite_id):
        """
        Method will provide testsuite table details as json for
        particular suite id
        Args:
            suite_id: suite id associated with user.

        Returns: returns suite_detials associated with user

        """
        return {
            'test_suite_id': suite_id.test_suite_id,
            'excel_name': suite_id.excel_name,
            'test_suite_name': suite_id.test_suite_name,
            'created_at': str(suite_id.created_at)[0:19],
            'test_case_list': list(map(lambda each_case:
                                       test_case_to_json(each_case),
                                       suite_id.test_case))
        }

    return {'test_suite_details_list': list(
        map(lambda suite_id: test_suite_to_json(suite_id),
            TestSuite.query.filter_by(
                owner_id=user_id)))}
