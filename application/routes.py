import os

from flask import send_from_directory

from application.api.login import (Login, LogOut, AddUser)
from application.api.testcase import TestCaseJob, TestCaseSparkJob
from application.api.testsuite import (AddTestSuite, TestCaseLogDetail,
                                       ExportTestLog)
from application.model.models import db
from index import (app, api, static_folder)

db


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
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
api.add_resource(LogOut, '/api/loginout')
api.add_resource(AddUser, '/api/adduser/<string:email>')
api.add_resource(AddTestSuite, '/api/test-suite')
api.add_resource(TestCaseJob, '/api/test-case-job')
api.add_resource(TestCaseSparkJob,
                 '/api/spark-job-status/<int:test_case_log_id>')
api.add_resource(TestCaseLogDetail,
                 '/api/test-case-log/<int:test_case_log_id>')
api.add_resource(ExportTestLog, '/api/export/<int:case_log_id>')
