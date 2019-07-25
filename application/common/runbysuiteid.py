from application.helper.runnerclass import run_by_case_id
from application.model.models import TestSuite


def run_by_suite_id(current_user, suite_id):
    """
    Args:
        current_user: user object
        suite_id: suite_id of the suite.

    Returns: Runs each job in the test suite

    """
    test_suite = TestSuite.query.filter_by(
        test_suite_id=suite_id).first()
    for each_test in test_suite.test_case:
        print(current_user, each_test.test_case_id)
        run_by_case_id(each_test.test_case_id, current_user)
    return True
