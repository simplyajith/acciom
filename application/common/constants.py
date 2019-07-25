"""File to store all constants."""


class APIMessages:
    """Messages to be sent in API Responses."""

    EMPTY_FIELD = "{} field cannot be blank"
    USER_EXISTS = "User with email as {} already exists"
    VERIFY_EMAIL = "Please verify your email address"
    USER_CREATED = "User with email as {} was created"
    INTERNAL_ERROR = "An Internal Server Error has occurred"
    USER_NOT_EXIST = "User with email as {} does not exist"
    INVALID_UID_PWD = "Please enter valid Username and Password"
    VERIFY_USER = "User verification is pending. Please verify through email"
    USER_LOGIN = "Logged in as {}"
    RESET_REQUEST = "Password Reset Request"
    RESET_EMAIL = "Reset Email was sent to your email"
    INVALID_TOKEN = "Invalid Token"
    RESET_PAGE = "Page for Password Reset"
    PASSWORD_CHANGE = "Password was successfully changed"
    USER_VERIFIED = "User Verification is completed"
    INVALID_PASSWORD = "The Old password you have entered is Invalid"
    NEW_TOKEN = "Access Token is generated"
    INVALID_EMAIL_PASSWORD = "Email or Password Password."
    DELETED_USER = "Please contact Admin, your account is not active."
    CREATE_RESOURCE = "{} is successfully created"
    PARSER_MESSAGE = "{} field is required"
    UPDATE_RESOURCE = "{} is updated successfully"
    SUCCESS = "success"


class TimeOuts:
    """Timeouts to be referenced in the code."""

    TEN_DAYS_IN_HOURS = 240
    HUNDRED_DAYS = 100
    ONE_DAY_IN_SECONDS = 60 * 60 * 24


class SupportedDBType:
    """Class to return Name and Id of the DataBase."""

    supported_db_type = {1: "postgresql", 2: "mysql", 3: "mssql", 4: "oracle", 5: "sqlite"}

    def get_db_name_by_id(self, db_id):
        """
        Method to return database name by passing Id.

        Args:
            db_id: (int) Id of the DB

        Returns:(str) name of the database

        """
        return self.supported_db_type.get(db_id)  # Returns None if Id does not exist

    def get_db_id_by_name(self, name):
        """
        Method to return database Id by passing name.

        Args:
            name: (str) name of the database

        Returns: (int) Id of the database
        """
        for key, value in self.supported_db_type.items():
            if value == name.lower():  # Name will be converted to lower case and compared
                return key
            # Returns None if Name does not exist


class SupportedTestClass:
    """Class to return Test Class Name and Id."""

    supported_test_class = {1: "countcheck", 2: "nullcheck", 3: "ddlcheck", 4: "duplicatecheck", 5: "datavalidation"}

    def get_test_class_name_by_id(self, test_class_id):
        """
        Method to return test class name by passing Id.

        Args:
            test_class_id: (int) Id of the test class

        Returns: (str) name of the test class
        """
        return self.supported_test_class.get(test_class_id)

    def get_test_class_id_by_name(self, name):
        """
        Method to return test class Id by passing name.

        Args:
            name: (str) name of the test class

        Returns: (int) Id of the test class
        """
        for key, value in self.supported_test_class.items():
            if value == name.lower():
                return key


class ExecutionStatus:
    """Class to return Name and Id of the DataBase."""

    execution_status = {0: "inprogress", 1: "pass", 2: "fail", 3: "error", 4: "new"}

    def get_execution_status_by_id(self, execution_id):
        """
        Method to return execution status by passing Id.

        Args:
            execution_id: (int) Id of the status

        Returns:(str) Execution status

        """
        return self.execution_status.get(execution_id)

    def get_execution_status_id_by_name(self, name):
        """
        Method to return execution status Id by passing status.

        Args:
            name: (str) execution status

        Returns: (int) Id of the status

        """
        for key, value in self.execution_status.items():
            if value == name.lower():
                return key
