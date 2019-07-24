from io import BytesIO
from openpyxl import load_workbook
from flask import current_app

from application.common.constants import ExecutionStatus,SupportedTestClass
from application.common.createdbdetail import create_dbconnection
from application.common.splitdbdetails import split_db
from application.model.models import TestSuite, TestCase


def save_file_to_db(current_user, project_id, data, file):

    """

    Args:
        current_user:  user_id of current user
        project_id: project id passed associated with the user
        data:
        file:Excel file

    Returns: Parse Excel and save data to db.

    """
    temp_file = TestSuite(project_id=project_id, user_id=current_user,
                          excel_name=file.filename,
                          test_suite_name=data['suite_name'])
    temp_file.save_to_db()
    sheet = data['sheet_name']
    wb = load_workbook(filename=BytesIO(file.read()))
    sheet_index = wb.sheetnames.index(sheet)
    ws = wb.worksheets[sheet_index]
    temp_test1 = [str(i - 2) for i in range(2, ws.max_row)]
    temp_test1.append('-1')
    # row+1 to avoid index out of range error! Need to change.
    temp_test_dict = {}
    for i in range(0, ws.max_column):
        if ((ws[1][i].value) != 'None'):
            temp_test_dict.update({str(ws[1][i].value): [str(ws[x][i].value)
                                                         for x in range(2,
                                                                        ws.max_row)]})

    test_case_list = data['selected_case']
    for j in range(ws.max_row - 1):
        if int(temp_test1[j]) in test_case_list:
            test_case_list.remove(int(temp_test1[j]))
            db_list = split_db(
                temp_test_dict[current_app.config.get('DBDETAILS')][j])
            src_db_id = create_dbconnection(current_user,
                                            db_list['sourcedbType'].lower(),
                                            db_list['sourcedb'],
                                            db_list['sourceServer'].lower(),
                                            db_list['sourceuser'])
            target_db_id = create_dbconnection(current_user,
                                               db_list['targetdbType'].lower(),
                                               db_list['targetdb'],
                                               db_list['targetServer'].lower(),
                                               db_list['Targetuser'])
            columndata = temp_test_dict[current_app.config.get('COLUMNS')][j]
            column = {}
            if columndata == "None" or columndata.isspace():
                pass
            else:
                if ":" in columndata.strip():
                    remove_column_space = \
                        temp_test_dict[current_app.config.get('COLUMNS')][
                            j].replace(" ",
                                       "")
                    split_columns = remove_column_space.split(";")
                    for each_column in split_columns:
                        column_split = each_column.split(":")
                        for _ in column_split:
                            column[column_split[0]] = column_split[1]
                else:
                    remove_column_space = \
                        temp_test_dict[current_app.config.get('COLUMNS')][
                            j].replace(" ",
                                       "")
                    column_list = remove_column_space.split(";")
                    column = {}
                    for each_col in range(len(column_list)):
                        column[column_list[each_col]] = column_list[each_col]
            table_list = temp_test_dict[current_app.config.get('TABLES')][
                j].replace(" ", "").split(":")
            table = {}
            table[table_list[0]] = table_list[1]
            query = {}
            custom_queries = temp_test_dict['Custom queries'][j]
            if not (custom_queries == "None" or custom_queries.isspace()):
                if ";" in custom_queries:
                    query_split = custom_queries.split(";")
                    final = [a.split(":") for a in query_split]
                    query["sourceqry"] = final[0][1] if 'srcqry' in final[
                        0] else ""
                    query["targetqry"] = final[1][1] if 'targetqry' in final[
                        1] else ""
                else:
                    if "srcqry:" in custom_queries.lower():
                        q = custom_queries.strip("srcqry:")
                        query["sourceqry"] = q
                        query['targetqry'] = ""
                    elif "targetqry:" in custom_queries.lower():
                        q = custom_queries.strip("targetqry:")
                        query["targetqry"] = q
                        query['sourceqry'] = ""
                    else:
                        query["sourceqry"] = ""
                        query["targetqry"] = ""
            jsondict = {"column": column, "table": table, "query": query,
                        "src_db_id": src_db_id, "target_db_id": target_db_id}
            temp = TestCase(test_suite_id=temp_file.test_suite_id,
                            user_id=current_user,
                            test_case_class=SupportedTestClass().get_test_class_id_by_name(temp_test_dict[current_app.config.get('TESTCLASS')][j].lower()),
                            test_case_detail=jsondict)
            temp.save_to_db()
            data = {
                "status": True,
                "message": "success",
                "Suite": temp_file
            }
    return data
