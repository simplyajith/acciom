"""File to store response codes and common methods."""
STATUS_OK = 200
STATUS_BAD_REQUEST = 400
STATUS_UNAUTHORIZED = 401
STATUS_NOT_FOUND = 404
STATUS_SERVER_ERROR = 500
STATUS_CREATED = 201
STATUS_FORBIDDEN = 403
STATUS_RESOURCE_ALREADY_PRESENT = 409


def api_response(success, message, http_status_code, data={}):
    """API Response common method.
    Args:
        success (bool): API status
        message (str): Message to display
        http_status_code (str or int): HTTP Response type. i.e. 200 or STATUS_OK
        data (dict): Data to be sent in api Response

    Returns:

    """
    payload = {"success": success,
               "message": message,
               "data": data if isinstance(data, dict) else {}}
    return payload, http_status_code
