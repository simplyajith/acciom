"""File to handle API routes."""
import os

from flask import send_from_directory

from application.api.checkconnection import CheckConnection
from application.api.connectiondetail import (SelectConnection, DbConnection,
                                              CaseDetails)
from application.api.dashboard import SideBarMenu
from application.api.data_quality_index import (ProjectDQI, OrganizationDQI)
from application.api.dbdetail import DbDetails
from application.api.login import (Login, LogOut, AddUser, ForgotPassword,
                                   ForgotPasswordVerifyToken, ResetPassword,
                                   GetToken, ChangePassword)
from application.api.organization import (OrganizationAPI, DashBoardStatus)
from application.api.project import ProjectAPI
from application.api.role import RoleAPI
from application.api.testcase import (TestCaseJob, TestCaseSparkJob,
                                      EditTestCase, TestCaseJobExternal)
from application.api.testsuite import (TestSuiteAPI, TestCaseLogDetail,
                                       ExportTestLog, TestCaseLogAPI)
from application.api.user_management import UserAPI, UserRoleAPI
from application.model.models import db
from index import (app, api, static_folder)

db


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """
    Serve HTML/React Static content i.e. HTML, CSS, JS, image, font files.

    Args:
        path(str): path for static folder or resource in case of backend api

    Returns: return HTML/React Static content i.e. HTML, CSS, JS file

    """
    if path != "" and os.path.exists(
            static_folder + path):  # for UI path ex: /login, /register
        return send_from_directory(static_folder, path)
    elif not (os.path.exists(static_folder + path) or (
            str(path).startswith(
                "api/"))):  # for Backend Path ex: /api/register
        return send_from_directory(static_folder, 'index.html')
    elif path == "":
        return send_from_directory(static_folder, 'index.html')


api.add_resource(Login, '/api/login')
api.add_resource(LogOut, '/api/logout')
api.add_resource(AddUser, '/api/register')
api.add_resource(TestSuiteAPI, '/api/test-suite')
api.add_resource(TestCaseLogAPI, '/api/each-case-detail')
api.add_resource(TestCaseJob, '/api/test-case-job')
api.add_resource(TestCaseSparkJob,
                 '/api/spark-job-status/<int:test_case_log_id>')
api.add_resource(TestCaseLogDetail,
                 '/api/test-case-log')
api.add_resource(ExportTestLog, '/api/export')
api.add_resource(ProjectAPI, '/api/project')
api.add_resource(OrganizationAPI, '/api/organization/')
api.add_resource(DbDetails, '/api/db-detail')
api.add_resource(CheckConnection, '/api/check-connection')
api.add_resource(DbConnection, '/api/db-connection-detail')
api.add_resource(CaseDetails, '/api/test-case-detail')
api.add_resource(EditTestCase, '/api/edit-test-case')
api.add_resource(SelectConnection, '/api/select-connection')
api.add_resource(SideBarMenu, '/api/sidebar-menu')
api.add_resource(ProjectDQI, '/api/project-data-quality-index')
api.add_resource(OrganizationDQI, '/api/organization-data-quality-index')
api.add_resource(DashBoardStatus, '/api/dash-board-status')
api.add_resource(RoleAPI, '/api/role')
api.add_resource(ForgotPassword, '/api/forgot-password')
api.add_resource(ForgotPasswordVerifyToken,
                 '/api/forgot-password-verify-token')
api.add_resource(ResetPassword, '/api/reset-password')
api.add_resource(GetToken, '/api/generate-token')
api.add_resource(TestCaseJobExternal, '/api/test-case-job-external')
api.add_resource(ChangePassword, '/api/change-password')
api.add_resource(UserAPI, '/api/user')
api.add_resource(UserRoleAPI, '/api/user-role')
