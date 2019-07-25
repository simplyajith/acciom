from application.common.constants import ExecutionStatus
from application.model.models import TestCaseLog


def return_all_log(case_log_id):
    """
    Method to return Case_log of a case_log_id

    Args:
        case_log_id(int): Accepts test_Case_log_id as argument

    Returns: return Case_log
    """

    def test_case_log_json(case_log):
        payload = {
            "test_case_log_ID": case_log.test_case_log_id,
            "test_case_ID": case_log.test_case_id,
            "Execution_status": ExecutionStatus().get_execution_status_by_id(
                case_log.execution_status),
            "Execution_log": case_log.execution_log
        }
        return payload

    return {"log_data": test_case_log_json(TestCaseLog.query.filter_by(
        test_case_log_id=case_log_id
    ).first())}
