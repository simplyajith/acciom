from application.common.constants import APIMessages
from application.model.models import DbConnection, TestSuite, TestCase


def connection_details(current_user, suite_id):
    """
    Method will give all the connections associated with the
    suite_id of the user

    Args:
        current_user (Obj): user_id of the current user
        suite_id (int):suite_id of the TestSuite

    Returns:
    """
    db_obj = DbConnection.query.filter_by(owner_id=current_user).all()
    suite_obj = TestSuite. \
        query.filter_by(test_suite_id=suite_id).first()
    all_case = [{"case_id": each_case.test_case_id,
                 "case_name": each_case.test_case_class}
                for each_case in suite_obj.test_case]
    all_connection = [
        {"db_connection_id": each_db_detail.db_connection_id,
         "db_connection_name": each_db_detail.db_connection_name}
        for
        each_db_detail in db_obj]
    payload = {"all_connections": all_connection, "all_cases": all_case}
    return payload


def select_connection(data, user):
    """
    Method will select connection according to condition
    Args:
        data: parser data given by user

    Returns: select connection according to condition

    """
    if data['connection_type'] == (APIMessages.SOURCE).lower():
        for each_case in data['case_id']:
            testcase = TestCase.query.filter_by(test_case_id=each_case,
                                                owner_id=user).first()
            testcase.test_case_detail['src_db_id'] = int(data["db_id"])
            payload = {"src_db_id": int(data["db_id"])}
            testcase.test_case_detail.update(payload)
            testcase.save_to_db()

    elif data['connection_type'] == (APIMessages.DESTINATION).lower():
        for each_case in data['case_id']:
            testcase = TestCase.query.filter_by(test_case_id=each_case,
                                                owner_id=user).first()
            testcase.test_case_detail['target_db_id'] = data["db_id"]
            testcase.save_to_db()

    return True
