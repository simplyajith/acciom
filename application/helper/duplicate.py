import functools

from flask import current_app as app

from application.common.constants import SupportedDBType, ExecutionStatus


def qry_generator(columns, target_table):
    """

    Args:
        columns: Columns provided from test_Case
        target_table: table associated with the test_case.

    Returns: custom query generated.

    """

    sub_startquery = ""
    sub_endquery = ""
    for each_col in range(len(columns)):
        if sub_startquery == "":
            sub_startquery = "{0}".format(columns[each_col])
            sub_endquery = "{0}".format(columns[each_col])
        else:
            sub_startquery = sub_startquery \
                             + ",{0}".format(columns[each_col])
            if len(columns) - 1 == each_col:
                sub_endquery = sub_endquery \
                               + ",{0}".format(columns[each_col])
            else:
                sub_endquery = sub_endquery \
                               + ",{0}".format(columns[each_col])
    custom_query = "SELECT " + sub_startquery + \
                   ",COUNT(*) " \
                   "FROM {0} ".format(target_table) + \
                   "GROUP BY " + sub_endquery + " HAVING COUNT(*) >1"
    print(custom_query)
    return custom_query


def duplication(target_cursor, target_table, column_name, test_queries,
                db_type):
    col_list = []
    newlst = []
    try:
        if db_type == SupportedDBType().get_db_id_by_name('oracle'):
            target_cursor.execute("SELECT column_name FROM "
                                  "user_tab_cols"
                                  " WHERE table_name=UPPER('{0}')".format(
                target_table))
        else:
            target_cursor.execute(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS"
                " WHERE table_name='{0}'".format(
                    target_table))
        for col in target_cursor:
            for each_col in col:
                col_list.append(each_col)

        if (test_queries == {} or test_queries['targetqry'].isspace() or
                test_queries['targetqry'] == ""):
            if column_name == []:
                custom_query = qry_generator(col_list, target_table)
            else:
                custom_query = qry_generator(column_name, target_table)
                # if column give in excel
        else:
            target_query = test_queries["targetqry"]
            newlst.append(target_query)
            custom_query = newlst[0]
        target_cursor.execute(custom_query)

        all_results = []

        for row in target_cursor:
            all_results.append(list(map(str, row)))
        if all_results:
            if (test_queries == {} or test_queries['targetqry'].isspace() or
                    test_queries['targetqry'] == ""):
                if column_name == []:
                    col_list.append("Duplicate Occurance")
                    for each_row in all_results:
                        for each_val in range(0, len(each_row)):
                            if each_row[each_val] == "None":
                                each_row[each_val] = "Null"

                    all_results.insert(0, col_list)
                else:
                    column_name.append("Duplicate Occurance")
                    for each_row in all_results:
                        for each_val in range(0, len(each_row)):
                            if each_row[each_val] == "None":
                                each_row[each_val] = "Null"
                    all_results.insert(0, column_name)
            else:
                if "select * from" in (test_queries["targetqry"].lower()):
                    col_list.append("Duplicate Occurance")
                    for each_row in all_results:
                        for each_val in range(0, len(each_row)):
                            if each_row[each_val] == "None":
                                each_row[each_val] = "Null"
                    all_results.insert(0, col_list)
                else:
                    qry = (test_queries["targetqry"]).lower()
                    start = "by"
                    end = "having"
                    columns = qry[
                              qry.index(start) + len(start):
                              qry.index(end)]
                    if "," in columns:
                        column = columns.split(",")
                        column.append("Duplicate Occurance")
                        for each_row in all_results:
                            for each_val in range(0, len(each_row)):
                                if each_row[each_val] == "None":
                                    each_row[each_val] = "Null"
                        all_results.insert(0, column)

                    else:
                        col_list_custom = []
                        col_list_custom.append(columns)
                        col_list_custom.append("Duplicate Occurance")
                        for each_row in all_results:
                            for each_val in range(0, len(each_row)):
                                if each_row[each_val] == "None":
                                    each_row[each_val] = "Null"
                        all_results.insert(0, col_list_custom)
            sum_of_duplicate_records = functools.reduce(
                lambda record_one, record_two: record_one + record_two,
                [int(each_row[-1]) for each_row in
                 all_results[1:]])
            return ({"res": ExecutionStatus().get_execution_status_id_by_name(
                'fail'),
                "Execution_log": {"Duplicate_count": sum_of_duplicate_records,
                                  "source_execution_log": None,
                                  "dest_execution_log": all_results[
                                                        :app.config.get(
                                                            'DUPLICATE_CHECK_MAX_RECORDS')]}})
        else:
            return ({"res": ExecutionStatus().get_execution_status_id_by_name(
                'pass'),
                "Execution_log": {"source_execution_log": None,
                                  "dest_execution_log": None}})

    except Exception as e:
        app.logger.error(e)
        return ({"res": ExecutionStatus().get_execution_status_id_by_name(
            'error'),
            "Execution_log": {"error_log": e}})
