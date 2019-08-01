from application.common.constants import APIMessages
from application.common.constants import SupportedDBType
from application.model.models import DbConnection, TestSuite, TestCase


def select_connection(case_data, user):
    """
    Method will select connection according to condition
    Args:
        data: parser data given by user

    Returns: select connection according to condition

    """
    if case_data['connection_reference'] == (APIMessages.SOURCE).lower():
        for each_case in list(case_data['case_id_list']):
            testcase_object = TestCase.query.filter_by(test_case_id=each_case,
                                                       owner_id=user).first()
            test_case_detail = testcase_object.test_case_detail
            test_case_detail['src_db_id'] = int(case_data["db_connection_id"])
            testcase_object.save_to_db()

    elif case_data['connection_reference'] == (
            APIMessages.DESTINATION).lower():
        for each_case in list(case_data['case_id_list']):
            testcase_object = TestCase.query.filter_by(test_case_id=each_case,
                                                       owner_id=user).first()
            test_case_detail = testcase_object.test_case_detail
            test_case_detail['target_db_id'] = int(
                case_data["db_connection_id"])
            testcase_object.save_to_db()

    testcase_object.test_case_detail = test_case_detail
    testcase_object.save_to_db()
    return True


def get_db_connection(project_id):
    db_obj = DbConnection.query.filter_by(project_id=project_id).all()
    all_connection = [
        {"db_connection_id": each_db_detail.db_connection_id,
         "db_connection_name": each_db_detail.db_connection_name}
        for
        each_db_detail in db_obj]
    payload = {"all_connections": all_connection}
    return payload


def get_case_detail(suite_id):
    suite_obj = TestSuite. \
        query.filter_by(test_suite_id=suite_id).first()
    all_case = [{"case_id": each_case.test_case_id,
                 "case_name": SupportedDBType().get_db_name_by_id(
                     each_case.test_case_class)}
                for each_case in suite_obj.test_case]
    payload = {"all_cases": all_case}
    print(payload)
    return payload
