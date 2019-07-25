"""File to handle API routes."""
import os

from flask import send_from_directory
from application.api.project import ProjectAPI
from application.api.organization import OraganizationAPI
from application.api.login import (Login, LogOut, AddUser)
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
api.add_resource(LogOut, '/api/loginout')
api.add_resource(AddUser, '/api/adduser/<string:email>')
api.add_resource(ProjectAPI, '/api/project')
api.add_resource(OraganizationAPI, '/api/organization/')
