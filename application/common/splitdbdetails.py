import ast


def split_table(table_name):
    # """
    # :param table_name: gets table_src_target value stored in TestSuite table
    # :return: returns a list consist of source and destination db.
    # """
    """

    Args:
        table_name: gets table_src_target from Excel

    Returns:returns a list consist of source and destination db.

    """

    table_names = ast.literal_eval(table_name)
    lst1 = {}
    tables = table_names["table"]
    for key in tables:
        lst1['src_table'] = key
        lst1['target_table'] = tables[key]
    return lst1


def split_db(test_db_detail):
    """

    Args:
        test_db_detail: Contains a String consist of DBDetails fetched from Excel

    Returns: A dictionary consist of keys(source_db,targetdb,sourcedbType,sourceServer
    # ,targetServer,sourceuser,Targetuser)

    """

    lst1 = []
    lst2 = {}
    strip_db_detail = test_db_detail.split(";")
    for i in range(len(strip_db_detail)):
        lst1.append(strip_db_detail[i].split(':', 1))
    lst2.update({"sourcedb": lst1[2][1]})
    lst2.update({"targetdb": lst1[5][1]})
    lst2.update({"sourcedbType": lst1[0][1]})
    lst2.update({"targetdbType": lst1[4][1]})
    lst2.update({"sourceServer": lst1[1][1]})
    lst2.update({"targetServer": lst1[6][1]})
    lst2.update({"sourceuser": lst1[3][1]})
    lst2.update({"Targetuser": lst1[7][1]})
    return lst2
