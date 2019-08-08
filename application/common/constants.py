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
    ADD_DATA = "Data Added"
    RETURN_SUCCESS = "success"
    PARSER_MESSAGE = "field is required"
    CREATE_RESOURCE = "{} is successfully created"
    UPDATE_RESOURCE = "{} is updated successfully"
    SUCCESS = "success"
    NO_RESOURCE = "{} is not available"
    DB_DETAILS_ADDED = "DbDetails added successfully"
    DATA_LOADED = "Data loaded successfully"
    DBID_NOT_IN_DB = "DB details for DB ID {},does not exist"
    DB_DETAILS_UPDATED = "DB details updated for connection id {} successfully"
    ABSENCE_OF_DBID = "Please pass DB Connection ID"
    CONNECTION_CREATE = "Connection can be created"
    CONNECTION_CANNOT_CREATE = "Connection could not be created"
    NO_DB_UNDER_PROJECT = "No db details exist under this project id"
    PASS_DBID_or_PROJECTID = "Please pass db id or project id"
    TEST_CASE_DELETED = "Test case with test case id {} deleted successfully"
    PASS_TESTCASEID = "Please pass test case id"
    TEST_CASE_NOT_IN_DB = "Test case details fot TestCase ID {},does not exist"
    TEST_CASE_DETAILS_UPDATED = "Test case details updated successfully"
    DB_TYPE_NAME = "DataBase Name is not valid. Supported Databases" \
                   " are postgresql, mysql, mssql, oracle, sqlite"
    INVALID_PROJECT_ID = " the given project does not exist"
    INVALID_ORG_ID = "the given Organization does not exist "
    RESOURCE_EXISTS = "{} already exists"
    NO_PERMISSION = "User does not have required permissions"
    SOURCE = "source"
    DESTINATION = "destination"
    EMAIL_NOT_CORRECT = "Your Email id is not correct"
    MAIL_SENT = "Mail sent your Email id"
    PAGE_TO_PASSWORD_RESET = "Page to password reset"
    TOKEN_MISMATCH = "Token Mismatch"
    PROJECT_NOT_EXIST = "Project does not exist"
    SUITE_NOT_EXIST = "suite does not exist"
    TESTCASELOGID_NOT_IN_DB = "testcase log id {} not present in db"
    ADD_ROLE = "Roles added Successfully"
    EMAIL_USER = "Either User Id or Email Id is mandatory"
    NO_NAME_DEFINE = "No name define"
    DEFAULT_DB_CONNECTION_PREFIX = "Connection"
    TESTSUITE_NOT_IN_DB = "test suite {} not present in db"


class GenericStrings:
    """Class to store generic strings that are referenced in code."""

    ORACLE_DRIVER = "{ODBC Driver 17 for SQL Server}"


class TimeOuts:
    """Timeouts to be referenced in the code."""

    TEN_DAYS_IN_HOURS = 240
    HUNDRED_DAYS = 100
    ONE_DAY_IN_SECONDS = 60 * 60 * 24


class SupportedDBType:
    """Class to return Name and Id of the DataBase."""

    supported_db_type = {1: "postgresql", 2: "mysql", 3: "mssql", 4: "oracle",
                         5: "sqlite"}

    def get_db_name_by_id(self, db_id):
        """
        Method to return database name by passing Id.

        Args:
            db_id: (int) Id of the DB

        Returns:(str) name of the database
        """
        # Returns None if Id does not exist
        return self.supported_db_type.get(db_id)

    def get_db_id_by_name(self, name):
        """
        Method to return database Id by passing name.

        Args:
            name: (str) name of the database
        Returns: (int) Id of the database
        """
        for key, value in self.supported_db_type.items():
            # Name will be converted to lower case and compared
            if value == name.lower():
                return key
            # Returns None if Name does not exist


class SupportedTestClass:
    """Class to return Test Class Name and Id."""

    supported_test_class = {1: "countcheck", 2: "nullcheck", 3: "ddlcheck",
                            4: "duplicatecheck", 5: "datavalidation"}

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

    execution_status = {0: "inprogress", 1: "pass", 2: "fail", 3: "error",
                        4: "new"}

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
