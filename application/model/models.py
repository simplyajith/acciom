from datetime import datetime

# from flask import current_app
from sqlalchemy.dialects.postgresql import JSON

from index import db

supported_db_type = ("postgresql", "mysql", "mssql", "oracle", "sqlite")
supported_test_class = ("countcheck", "nullcheck", "ddlcheck",
                        "duplicatecheck", "datavalidation")
execution_status_type = ("inprogress", "pass", "fail", "error", "new")


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.TEXT, nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now)

    # sqlalchemy ORM relation
    session = db.relationship("Session", back_populates='user', lazy=True)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def __init__(self, email, first_name, last_name, password_hash,
                 is_verified=False):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password_hash = password_hash
        self.is_verified = is_verified


class Organization(db.Model):
    __tablename__ = 'organization'
    org_id = db.Column(db.Integer, primary_key=True)
    org_name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.ForeignKey('user.user_id'), nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def __init__(self, org_name, user_id):
        self.org_name = org_name
        self.user_id = user_id


class Project(db.Model):
    __tablename__ = 'project'
    project_id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(50), nullable=False)
    org_id = db.Column(db.ForeignKey('organization.org_id'), nullable=False,
                       index=True)
    user_id = db.Column(db.ForeignKey('user.user_id'), nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def __init__(self, project_name, org_id, user_id):
        self.project_name = project_name
        self.org_id = org_id
        self.user_id = user_id


class Group(db.Model):
    __tablename__ = "group"
    group_id = db.Column(db.Integer, primary_key=True, index=True)
    org_id = db.Column(db.ForeignKey('organization.org_id'), nullable=False,
                       index=True)
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, project_name, org_id, user_id):
        self.project_name = project_name
        self.org_id = org_id
        self.user_id = user_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class UserGroup(db.Model):
    __tablename__ = "user_group"
    user_id = db.Column(db.ForeignKey('user.user_id'), nullable=False,
                        primary_key=True, index=True)
    org_id = db.Column(db.ForeignKey('organization.org_id'), nullable=False,
                       primary_key=True, index=True)
    project_id = db.Column(db.ForeignKey('project.project_id'), nullable=False,
                           primary_key=True, index=True)
    group_id = db.Column(db.ForeignKey('group.group_id'), nullable=False,
                         primary_key=True, index=True)

    def __init__(self, user_id, org_id, project_id, group_id):
        self.user_id = user_id
        self.org_id = org_id
        self.project_id = project_id
        self.group_id = group_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class Permission(db.Model):
    __tablename__ = "permission"
    permission_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class GroupPermission(db.Model):
    __tablename__ = "group_permission"
    org_id = db.Column(db.ForeignKey('organization.org_id'),
                       nullable=False, primary_key=True, index=True)
    group_id = db.Column(db.ForeignKey('group.group_id'),
                         nullable=False, primary_key=True, index=True)
    permission_id = db.Column(db.ForeignKey('permission.permission_id'),
                              nullable=False, primary_key=True, index=True)

    def __init__(self, org_id, group_id, permission_id):
        self.org_id = org_id
        self.group_id = group_id
        self.permission_id = permission_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class DbConnection(db.Model):
    __tablename__ = "db_connection"
    db_connection_id = db.Column(db.Integer, primary_key=True, )
    project_id = db.Column(db.ForeignKey('project.project_id'),
                           nullable=False, index=True)
    user_id = db.Column(db.ForeignKey('user.user_id'), nullable=False)
    db_connection_name = db.Column(db.Text)
    db_type = db.Column(db.SMALLINT, nullable=False)
    db_name = db.Column(db.String(80), nullable=False)
    db_hostname = db.Column(db.String(255), nullable=False)
    db_username = db.Column(db.String(80), nullable=False)
    db_encrypted_password = db.Column(db.Text, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, project_id, user_id, db_connection_name,
                 db_type, db_name,
                 db_hostname, db_username, db_encrypted_password):
        self.project_id = project_id
        self.user_id = user_id
        self.db_connection_name = db_connection_name
        self.db_type = db_type
        self.db_name = db_name
        self.db_hostname = db_hostname
        self.db_username = db_username
        self.db_encrypted_password = db_encrypted_password

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class TestSuite(db.Model):
    __tablename__ = "test_suite"
    test_suite_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.ForeignKey('project.project_id'),
                           nullable=False, index=True)
    user_id = db.Column(db.ForeignKey('user.user_id'),
                        nullable=False)
    excel_name = db.Column(db.Text, nullable=False)
    test_suite_name = db.Column(db.Text, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, project_id, user_id, excel_name, test_suite_name):
        self.project_id = project_id
        self.user_id = user_id
        self.excel_name = excel_name
        self.test_suite_name = test_suite_name

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class TestCase(db.Model):
    __tablename__ = "test_case"
    test_case_id = db.Column(db.Integer, primary_key=True)
    test_suite_id = db.Column(db.ForeignKey(TestSuite.test_suite_id),
                              nullable=False, index=True)
    user_id = db.Column(db.ForeignKey('user.user_id'), nullable=False)
    test_case_class = db.Column(db.SMALLINT, nullable=False)
    latest_execution_status = db.Column(db.SMALLINT,
                                        nullable=False, default='new')
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    test_case_detail = db.Column(JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def __init__(self, test_suite_id, user_id, test_case_class,
                 test_case_detail):
        self.test_suite_id = test_suite_id
        self.user_id = user_id
        self.test_case_class = test_case_class
        self.test_case_detail = test_case_detail


class TestCaseLog(db.Model):
    __tablename__ = "test_case_log"
    test_case_log_id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.ForeignKey(TestCase.test_case_id), index=True)
    execution_status = db.Column(db.SMALLINT, nullable=False)
    user_id = db.Column(db.ForeignKey('user.user_id'),
                        nullable=False)
    execution_log = db.Column(JSON, nullable=True)
    executed_at = db.Column(db.DateTime, default=datetime.now, index=True)

    def __init__(self, test_case_id, execution_status, user_id,
                 execution_log):
        self.test_case_id = test_case_id
        self.execution_status = execution_status
        self.user_id = user_id
        self.execution_log = execution_log

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class PersonalToken(db.Model):
    __tablename__ = 'personal_token'
    personal_token_id = db.Column(db.Integer, primary_key=True
                                  )
    user_id = db.Column(db.ForeignKey(User.user_id), index=True,
                        nullable=False)
    encrypted_personal_token = db.Column(db.String(256), unique=True,
                                         index=True,
                                         nullable=False)
    note = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, user_id, encrypted_personal_token, note):
        self.user_id = user_id
        self.encrypted_personal_token = encrypted_personal_token
        self.note = note

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class Session(db.Model):
    """
    To store user session to invalidate logout token
    """
    __tablename__ = 'session'
    session_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.ForeignKey(User.user_id), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now())

    # sqlalchemy ORM relation
    user = db.relationship("User", back_populates='session', lazy=True)

    def __init__(self, user_id):
        """Create Session Object

        Args:
            user_id (int): User Id from user table
        """
        self.user_id = user_id

    def save_to_db(self):
        """To store current changes in DB

        Returns: None
        """
        db.session.add(self)
        db.session.commit()

    def delete_user_session(self):
        """To delete current object in DB

        Returns: None
        """
        db.session.delete(self)
        db.session.commit()
