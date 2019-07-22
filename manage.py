from flask_migrate import Migrate

from application.routes import app, db

# from index import db

migrate = Migrate(app, db)
