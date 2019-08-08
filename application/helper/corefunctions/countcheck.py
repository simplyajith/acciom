from flask import current_app as app

from application.common.constants import ExecutionStatus


def count_check(source_cursor, target_cursor, source_table,
                target_table, test_query):
    """
    Method will perform countcheck on data
    Args:
        source_cursor(object): source_cursor object
        target_cursor(object): target cursor object
        source_table(str): source table
        target_table(str): target table
        test_query(str): Source and target query.

    Returns: Result (pass,fail ) on the particular details.

    """
    payload = {"res": None, "src_value": None,
               "des_value": None}
    try:
        qry_lst = []
        app.logger.debug(qry_lst)
        if test_query == {}:
            source_cursor.execute(
                'SELECT COUNT(1) FROM {}'.format(source_table))
            target_cursor.execute(
                'SELECT COUNT(1) FROM {}'.format(target_table))
        else:
            src_query = test_query["sourceqry"]
            target_query = test_query["targetqry"]
            source_cursor.execute(src_query)
            target_cursor.execute(target_query)
        for each_row in source_cursor:
            for src_count in each_row:
                pass
        for each_row in target_cursor:
            for target_count in each_row:
                pass
        if src_count == target_count:
            execution_result = ExecutionStatus(). \
                get_execution_status_id_by_name('pass')
            payload = {"res": execution_result,
                       "Execution_log": {"source_execution_log": src_count,
                                         "dest_execution_log": target_count}}
        else:
            execution_result = ExecutionStatus(). \
                get_execution_status_id_by_name('fail')
            payload = {"res": execution_result,
                       "Execution_log": {"source_execution_log": src_count,
                                         "dest_execution_log": target_count}}
            app.logger.info("count check fail")
    except Exception as e:
        app.logger.error(e)
        payload = {"res": ExecutionStatus().get_execution_status_id_by_name(
            'error'),
            "Execution_log": {"error_log": e}}

    return payload
