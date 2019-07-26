import json
from collections import OrderedDict

from flask import current_app as app

from application.common.constants import SupportedDBType, ExecutionStatus


def ddl_check(source_cursor, target_cursor, source_table, target_table,
              src_db_type, target_db_type):
    try:
        source_schema = []
        target_schema = []
        temp_oracle_source_schema = []
        temp_oracle_target_schema = []

        if src_db_type == SupportedDBType().get_db_id_by_name("oracle"):
            src_cursor = source_cursor
            src_cursor.execute(
                "SELECT COLUMN_NAME,DATA_TYPE,NULLABLE FROM USER_TAB_COLUMNS "
                "WHERE TABLE_NAME = UPPER('{0}')".format(source_table))
            for schema in src_cursor:
                schema = [single_schema.lower() for single_schema in schema]
                temp_oracle_source_schema.append(schema)
            for temp_schema in temp_oracle_source_schema:
                if temp_schema[2] == "y":
                    temp_schema = (temp_schema[0], temp_schema[1], "YES")
                else:
                    temp_schema = (temp_schema[0], temp_schema[1], "NO")
                source_schema.append(temp_schema)
        else:
            src_cursor = source_cursor
            src_cursor.execute(
                "SELECT COLUMN_NAME, IS_NULLABLE,DATA_TYPE FROM information_"
                "schema.columns WHERE table_name = '{}'".format(source_table))
            for schema in src_cursor:
                source_schema.append(tuple(schema))

        if target_db_type == "oracle":
            dest_cursor = target_cursor
            dest_cursor.execute(
                "SELECT COLUMN_NAME,DATA_TYPE,NULLABLE FROM USER_TAB_COLUMNS"
                " WHERE TABLE_NAME = UPPER('{0}')".format(target_table))
            for schema in dest_cursor:
                schema = [single_schema.lower() for single_schema in schema]
                temp_oracle_target_schema.append(schema)
            for temp_schema in temp_oracle_target_schema:
                if temp_schema[2] == "y":
                    temp_schema = (temp_schema[0], temp_schema[1], "YES")
                else:
                    temp_schema = (temp_schema[0], temp_schema[1], "NO")
                target_schema.append(temp_schema)
        else:
            dest_cursor = target_cursor
            dest_cursor.execute(
                "SELECT COLUMN_NAME, IS_NULLABLE,DATA_TYPE FROM "
                "information_schema.columns WHERE table_name = '{}'".format(
                    target_table))
            for schema in dest_cursor:
                target_schema.append(tuple(schema))

        source_schema_set, target_schema_set = set(source_schema), set(
            target_schema)
        schema_list = list(source_schema_set & target_schema_set)
        for item in schema_list:
            source_schema.remove(item)
            target_schema.remove(item)

        source_schema_dict = OrderedDict(
            {column_name: (column_name, nullable, datatype) for
             column_name, nullable, datatype in source_schema})
        target_schema_dict = OrderedDict(
            {column_name: (column_name, nullable, datatype) for
             column_name, nullable, datatype in target_schema})

        all_keys = set(source_schema_dict) | set(target_schema_dict)

        source_schema_orderdict = OrderedDict(
            {key: source_schema_dict.get(key, ("missing",)) for key in
             all_keys})
        target_schema_orderdict = OrderedDict(
            {key: target_schema_dict.get(key, ("missing",)) for key in
             all_keys})

        source_schema_values = list(source_schema_orderdict.values())
        target_schema_values = list(target_schema_orderdict.values())

        source_schema_results = json.dumps(source_schema_values)
        target_schema_results = json.dumps(target_schema_values)

        if source_schema == [] and target_schema == []:
            return ({"res": ExecutionStatus().get_execution_status_id_by_name(
                'pass'),
                "Execution_log": {
                    "source_execution_log": source_schema_results,
                    "dest_execution_log": target_schema_results}})
        else:
            return ({"res": ExecutionStatus().get_execution_status_id_by_name(
                'fail'),
                "Execution_log": {"source_execution_log": None,
                                  "dest_execution_log": None}})
    except Exception as e:
        app.logger.error(e)
        return ({"res": ExecutionStatus().get_execution_status_id_by_name(
            'error'),
            "Execution_log": {"source_execution_log": None,
                              "dest_execution_log": None}})
