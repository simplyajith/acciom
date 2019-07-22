import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

levels = {"DEBUG": logging.DEBUG,
          "INFO": logging.INFO,
          "ERROR": logging.ERROR,
          "WARNING": logging.WARNING}


def config_log(app):
    log_directory = app.config['LOG_LOCATION']
    log_file_location = log_directory + 'acciom.log'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    handler = RotatingFileHandler(log_file_location,
                                  maxBytes=10000,
                                  backupCount=1)
    handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
    app.logger.addHandler(handler)
    app.logger.setLevel(app.config['LOG_LEVEL'])


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.cfg')
    config_log(app)
    return app


basedir = os.path.abspath(os.path.dirname(__file__))
static_folder = basedir + '/static/acciom_ui/'

app = create_app()
app.url_map.strict_slashes = False
db = SQLAlchemy(app)
api = Api(app)
