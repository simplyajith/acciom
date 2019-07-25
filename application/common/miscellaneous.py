from application.common.constants import APIMessages


def validate_empty_fields(data_json, list_of_args):
    """
    Validate empty fields on request payload.

    Args:
        data_json(dict): Dictionary of payload sent by user
        list_of_args(list): list of arguments that are expected by system

    Returns(str): Message in case of empty string
    """
    for each_arg in list_of_args:
        if not (data_json[each_arg]):
            # Checking if fields are empty
            return APIMessages.EMPTY_FIELD.format(each_arg)
