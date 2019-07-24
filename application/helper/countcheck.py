from flask import current_app as app

from application.common.constants import ExecutionStatus

# from application.helper.runner_class import split_query

arr = []


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
    print("22", source_cursor, target_cursor, source_table,
          target_table, test_query)
    payload = {"res": None, "src_value": None,
               "des_value": None}
    try:
        newlst = []

        app.logger.debug(newlst)
        # newlst = split_query(test_query)
        if test_query == {}:
            source_cursor.execute(
                'SELECT COUNT(1) FROM {}'.format(source_table))
            target_cursor.execute(
                'SELECT COUNT(1) FROM {}'.format(target_table))
        else:
            src_query = test_query["sourceqry"]
            target_query = test_query["targetqry"]
            newlst.append(src_query)
            newlst.append(target_query)
            source_cursor.execute(newlst[0])
            target_cursor.execute(newlst[1])
        for row in source_cursor:
            for src_count in row:
                pass
        for row in target_cursor:
            for target_count in row:
                pass
        if src_count == target_count:

            payload["res"] = ExecutionStatus().get_execution_status_id_by_name(
                'pass')
            payload["src_value"] = src_count
            payload["des_value"] = target_count  # pass.
            app.logger.info("count check sucess")
        else:
            payload["res"] = ExecutionStatus().get_execution_status_id_by_name(
                'fail')
            payload["src_value"] = src_count
            payload["des_value"] = target_count
            app.logger.info("count check fail")
    except Exception as e:
        app.logger.error("65", e)
        return {
            "res": ExecutionStatus().get_execution_status_id_by_name('error'),
            "src_value": str(e), "des_value": str(e)}
    return payload
