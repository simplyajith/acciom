import ast

from application.common.constants import SupportedTestClass
from application.common.dbconnect import dbconnection
from application.helper.runnerclasshelpers import (db_details, split_table)
from application.model.models import TestCase


def calculate_dqi(execution_log, test_case_id):
    """
    To calculate DQI percentage for each test case

    Args:
        execution_log(dic):Contains a execution log of test cases
        test_case_id(int):test case id of a pariculat test

    Returns:
        Returns a DQI percentage of each test case

    """
    test_case_obj = TestCase.query.filter_by(
        test_case_id=test_case_id).first()
    if test_case_obj.test_case_class == SupportedTestClass(). \
            get_test_class_id_by_name("countcheck"):
        src_count = execution_log["source_execution_log"]
        target_count = execution_log["dest_execution_log"]
        dqi = ((min(src_count, target_count)) / (
            max(src_count, target_count))) * 100
        return dqi

    if test_case_obj.test_case_class == SupportedTestClass(). \
            get_test_class_id_by_name("duplicatecheck"):
        target_detail = db_details(
            test_case_obj.test_case_detail['target_db_id'])
        target_cursor = dbconnection(target_detail['db_name'],
                                     target_detail['db_type'],
                                     target_detail['db_hostname'].lower(),
                                     target_detail['db_username'],
                                     target_detail['db_password']).cursor()
        table_name = split_table(test_case_obj.test_case_detail)
        target_cursor.execute(
            'SELECT COUNT(1) FROM {}'.format(table_name['target_table']))
        for each_row in target_cursor:
            for target_count in each_row:
                pass
        dqi = ((target_count - execution_log[
            "Duplicate_count"]) / target_count) * 100
        return dqi

    if test_case_obj.test_case_class == SupportedTestClass(). \
            get_test_class_id_by_name("nullcheck"):
        target_detail = db_details(
            test_case_obj.test_case_detail['target_db_id'])
        target_cursor = dbconnection(target_detail['db_name'],
                                     target_detail['db_type'],
                                     target_detail['db_hostname'].lower(),
                                     target_detail['db_username'],
                                     target_detail['db_password']).cursor()
        table_name = split_table(test_case_obj.test_case_detail)
        target_cursor.execute(
            'SELECT COUNT(1) FROM {}'.format(table_name['target_table']))
        for each_row in target_cursor:
            for target_count in each_row:
                pass
        dqi = ((target_count - execution_log[
            "Null_count"]) / target_count) * 100
        return dqi

    if test_case_obj.test_case_class == SupportedTestClass(). \
            get_test_class_id_by_name("ddlcheck"):
        execution_log_list_src = ast.literal_eval(
            execution_log["source_execution_log"])
        execution_log_list_dist = ast.literal_eval(
            execution_log["dest_execution_log"])
        column_mismatch = len(execution_log_list_src) + len(
            execution_log_list_dist)
        src_detail = db_details(
            test_case_obj.test_case_detail['src_db_id'])
        target_detail = db_details(
            test_case_obj.test_case_detail['target_db_id'])
        source_cursor = dbconnection(src_detail['db_name'],
                                     src_detail['db_type'],
                                     src_detail['db_hostname'].lower(),
                                     src_detail['db_username'],
                                     src_detail['db_password']).cursor()
        target_cursor = dbconnection(target_detail['db_name'],
                                     target_detail['db_type'],
                                     target_detail['db_hostname'].lower(),
                                     target_detail['db_username'],
                                     target_detail['db_password']).cursor()

        table_name = split_table(test_case_obj.test_case_detail)
        source_cursor.execute(
            'SELECT COUNT(1) FROM {}'.format(table_name['src_table']))
        target_cursor.execute(
            'SELECT COUNT(1) FROM {}'.format(table_name['target_table']))
        for each_row in target_cursor:
            for target_count in each_row:
                pass
        for each_row in source_cursor:
            for source_count in each_row:
                pass
        total_no_of_records = source_count + target_count
        dqi = ((total_no_of_records - column_mismatch) /
               total_no_of_records) * 100
        return dqi

    if test_case_obj.test_case_class == SupportedTestClass(). \
            get_test_class_id_by_name("datavalidation"):
        total_no_records = execution_log["src_count"] + execution_log[
            "dest_count"]
        total_mismatch_found = execution_log["src_to_dest_count"] + \
                               execution_log["dest_to_src_count"]
        dqi = ((total_no_records - total_mismatch_found) /
               total_no_records) * 100
        return dqi
