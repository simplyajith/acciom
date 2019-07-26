import ast
import json
from tempfile import NamedTemporaryFile

from flask import Response
from openpyxl import Workbook

from application.model.models import TestCaseLog


def export_test_case_log(case_log_id):
    """
    Method will return an excel of the case_log.
    Args:
        case_log_id: case_log Id associated with log.

    Returns:  return an excel of the case_log.

    """
    export_response = []
    case_log = TestCaseLog.query.filter_by(
        test_case_log_id=case_log_id).first()
    test_case = case_log.test_cases

    if test_case.test_name == 'Datavalidation':
        source_data = case_log.execution_log["src_execution_log"]
        destination_data = case_log.execution_log["dest_execution_log"]

        if source_data["result"] != 'none':
            source_data
            export_response.append(['Source Table'])
            for each_row in source_data:
                dict_key = ast.literal_eval(each_row)
                key_list = [key for key in dict_key.keys()]
            export_response.append(key_list)
            for each_row in source_data:
                dict_key = ast.literal_eval(each_row)
                value_list = [val for val in dict_key.values()]
                export_response.append(value_list)

        if destination_data["result"] != 'none':
            destination_data
            export_response.append(['Target Table'])
            for each_row in destination_data:
                dict_key = ast.literal_eval(each_row)
                key_list = [key for key in dict_key.keys()]
            export_response.append(key_list)
            for each_row in destination_data:
                dict_key = ast.literal_eval(each_row)
                value_list = [val for val in dict_key.values()]
                export_response.append(value_list)

        response = json.dumps(export_response)
    elif test_case.test_name == 'CountCheck':
        src_response = case_log.execution_log["src_execution_log"]
        des_response = case_log.execution_log["dest_execution_log"]
        res = [['Source Count', 'destination Count']]
        res.append([src_response, des_response])
        response = json.dumps(res)

    elif test_case.test_name == 'DuplicateCheck' or 'NullCheck':
        response = case_log.execution_log["dest_Execution_log"]

    work_book = Workbook()
    work_sheet = work_book.active

    response = json.loads(response)
    for each in response:
        work_sheet.append(list(each))

    with NamedTemporaryFile(delete=False) as tmp_file:
        work_book.save(tmp_file.name)
        tmp_file.seek(0)
        stream = tmp_file.read()
    return Response(
        stream,
        mimetype="application/vnd.openxmlformats-officedocument."
                 "spreadsheetml.sheet",
        headers={"Content-disposition": "attachment; "
                                        "filename={}.xlsx".format(
            test_case.test_name)})
