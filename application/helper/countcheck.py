from flask import current_app as app

from application.common.constants import ExecutionStatus


def count_check(source_cursor, target_cursor, source_table,
                target_table, test_query):
    """

    Args:
        source_cursor: source_cursor object
        target_cursor: target cursor object
        source_table: source table
        target_table: target table
        test_query: Source and target query.

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
            qry_lst.append(src_query)
            qry_lst.append(target_query)
            source_cursor.execute(qry_lst[0])
            target_cursor.execute(qry_lst[1])
        for row in source_cursor:
            for src_count in row:
                pass
        for row in target_cursor:
            for target_count in row:
                pass
        if src_count == target_count:

            execution_result = ExecutionStatus().get_execution_status_id_by_name(
                'pass')
            payload = {"res": execution_result,
                       "Execution_log": {"src_log": src_count,
                                         "dest_log": target_count}}
            app.logger.info("count check sucess")
        else:
            execution_result = ExecutionStatus().get_execution_status_id_by_name(
                'fail')
            payload = {"res": execution_result,
                       "Execution_log": {"src_log": src_count,
                                         "dest_log": target_count}}
            app.logger.info("count check fail")
    except Exception as e:
        app.logger.error(e)
        return {
            "res": ExecutionStatus().get_execution_status_id_by_name('error'),
            "src_value": str(e), "des_value": str(e)}
    return payload
