from functools import wraps
import flask
import flask_login
from authlib.integrations.flask_client import OAuth
from flask_admin import Admin
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
login_manager = LoginManager()
oauth = OAuth()
admin = Admin(name="KMAT")
migrate = Migrate()
login_manager.login_view = "base.index"


# fmt: off
def requires(permission):
    def decorator(f):
        @wraps(f)
        @flask_login.login_required
        def decorated(*f_args, **f_kwargs):
            if flask_login.current_user.has_access(permission):
                return f(*f_args, **f_kwargs)
            return flask.abort(403)
        return decorated
    return decorator
# fmt: on
