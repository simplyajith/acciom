import ast


def split_table(table_name):
    """
    Method to convert data from excel to src,target tables

    Args:
        table_name(str): Table name as argument in Text Format

    Returns: src,target tables

    """
    table_names = ast.literal_eval(table_name)
    table_list = {}
    tables = table_names["table"]
    for each_table in tables:
        table_list['src_table'] = each_table
        table_list['target_table'] = tables[each_table]
    return table_list


def split_db(test_db_detail):
    """
    Args:
        test_db_detail: Contains a String consist
         of DBDetails fetched from Excel

    Returns: A dictionary consist
     of keys(source_db,targetdb,sourcedbType,sourceServer
    targetServer,sourceuser,Targetuser)

    """
    temp_dblist = []
    db_detail = {}
    strip_db_detail = test_db_detail.split(";")
    for i in range(len(strip_db_detail)):
        temp_dblist.append(strip_db_detail[i].split(':', 1))
    db_detail.update({"sourcedb": temp_dblist[2][1]})
    db_detail.update({"targetdb": temp_dblist[5][1]})
    db_detail.update({"sourcedbType": temp_dblist[0][1]})
    db_detail.update({"targetdbType": temp_dblist[4][1]})
    db_detail.update({"sourceServer": temp_dblist[1][1]})
    db_detail.update({"targetServer": temp_dblist[6][1]})
    db_detail.update({"sourceuser": temp_dblist[3][1]})
    db_detail.update({"Targetuser": temp_dblist[7][1]})
    return db_detail
