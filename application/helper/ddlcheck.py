from flask import current_app as app

from application.common.constants import ExecutionStatus


def ddl_check(source_cursor, target_cursor, source_table, target_table,
              src_db_type, target_db_type):
    """

    Args:
        source_cursor:
        target_cursor:
        source_table:
        target_table:
        src_db_type:
        target_db_type:

    Returns:

    """
    print(source_cursor, target_cursor, source_table, target_table,
          src_db_type, target_db_type)
    try:
        data1 = []
        data2 = []
        data3 = []
        data4 = []
        if src_db_type == "oracle":
            cursor = source_cursor
            cursor.execute(
                "SELECT COLUMN_NAME,DATA_TYPE,NULLABLE FROM USER_TAB_COLUMNS WHERE TABLE_NAME = UPPER('{0}')".format(
                    source_table)
            )

            for row in cursor:
                row = [x.lower() for x in row]
                data3.append(row)
            for i in data3:
                if i[2] == "y":
                    i = (i[0], i[1], "YES")
                else:
                    i = (i[0], i[1], "NO")
                data1.append(i)
        else:
            cursor = source_cursor
            cursor.execute(
                "SELECT COLUMN_NAME, IS_NULLABLE,DATA_TYPE FROM information_schema.columns WHERE table_name = '{}'".format(
                    source_table)
            )

            for row in cursor:
                data1.append(tuple(row))

        if target_db_type == "oracle":

            cursor1 = target_cursor
            cursor1.execute(
                "SELECT COLUMN_NAME,DATA_TYPE,NULLABLE FROM USER_TAB_COLUMNS WHERE TABLE_NAME = UPPER('{0}')".format(
                    target_table))

            for row in cursor1:
                row = [x.lower() for x in row]
                data4.append(row)
            for i in data4:
                if i[2] == "y":
                    i = (i[0], i[1], "YES")
                else:
                    i = (i[0], i[1], "NO")
                data2.append(i)
        else:

            cursor1 = target_cursor
            cursor1.execute(
                "SELECT COLUMN_NAME, IS_NULLABLE,DATA_TYPE FROM information_schema.columns WHERE table_name = '{}'".format(
                    target_table))

            for row in cursor1:
                data2.append(tuple(row))
        set_1, set_2 = set(data1), set(data2)
        a = list(set_1 & set_2)
        for item in a:
            data1.remove(item)
            data2.remove(item)

        from collections import OrderedDict

        d1 = OrderedDict({a: (a, b, c) for a, b, c in data1})
        d2 = OrderedDict({a: (a, b, c) for a, b, c in data2})

        all_keys = set(d1) | set(d2)

        x = OrderedDict({k: d1.get(k, ("missing",)) for k in all_keys})
        y = OrderedDict({k: d2.get(k, ("missing",)) for k in all_keys})

        src_result = list(x.values())
        dest_result = list(y.values())

        if data1 == [] and data2 == []:
            return ({"res": ExecutionStatus().get_execution_status_id_by_name(
                'pass'),
                "Execution_log": {"src_log": src_result,
                                  "dest_log": dest_result}})
        else:
            return ({"res": ExecutionStatus().get_execution_status_id_by_name(
                'fail'),
                "Execution_log": {"src_log": None,
                                  "dest_log": None}})

    except Exception as e:
        app.logger.error(e)
        return ({"res": ExecutionStatus().get_execution_status_id_by_name(
            'error'),
            "Execution_log": {"src_log": None,
                              "dest_log": None}})
