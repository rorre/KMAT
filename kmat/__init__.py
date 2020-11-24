__version__ = "0.1.0"

import json

from flask import Flask, flash, redirect, render_template, url_for
from flask_admin.contrib.sqla import ModelView
from flask_bootstrap import Bootstrap
from flask_login import current_user

from urllib.parse import unquote


def create_app(config_file="config.json"):
    with open(config_file, "r") as f:
        data = json.load(f)

    if "SENTRY_URL" in data:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        sentry_sdk.init(dsn=data["SENTRY_URL"], integrations=[FlaskIntegration()])

    app = Flask(__name__, static_url_path="/static", static_folder="static")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["BOOTSTRAP_BOOTSWATCH_THEME"] = "darkly"
    app.config.from_mapping(data)

    from kmat.models import Role, Submission, User
    from kmat.plugins import admin, db, login_manager, migrate, oauth, toolbar

    admin.init_app(app)
    init_oauth(app, oauth)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    Bootstrap().init_app(app)
    toolbar.init_app(app)

    app.jinja_env.filters["unquote"] = unquote

    admin.add_view(AdminView(User, db.session, endpoint="/user"))
    admin.add_view(AdminView(Submission, db.session, endpoint="/submission"))
    admin.add_view(AdminView(Role, db.session, endpoint="/role"))

    from kmat.routes import base, submission, user, judge

    app.register_blueprint(base.blueprint)
    app.register_blueprint(judge.blueprint)
    app.register_blueprint(submission.blueprint)
    app.register_blueprint(user.blueprint)

    @app.errorhandler(403)
    def unauthorized(e):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("500.html"), 500

    @app.before_first_request
    def init_db():
        db.create_all()

    return app


class AdminView(ModelView):
    column_exclude_list = ("access_token",)
    form_excluded_columns = ("access_token",)

    def is_accessible(self):
        return current_user.is_authenticated and any(
            [r.admin for r in current_user.roles]
        )

    def inaccessible_callback(self, name, **kwargs):
        flash("You must be an admin to see this page.", "error")
        return redirect(url_for("base.index"))


def fetch_token(name):
    from flask_login import current_user

    return current_user.to_token()


def update_token(name, token, refresh_token=None, access_token=None):
    from flask_login import current_user

    from kmat.plugins import db

    current_user.access_token = token["access_token"]
    current_user.refresh_token = token.get("refresh_token")
    current_user.expires_at = token["expires_at"]
    db.session.commit()


def init_oauth(app, oauth):
    oauth.register(
        "osu",
        client_id=app.config.get("OSU_CLIENT_ID"),
        client_secret=app.config.get("OSU_CLIENT_SECRET"),
        api_base_url="https://osu.ppy.sh/api/v2/",
        authorize_url="https://osu.ppy.sh/oauth/authorize",
        access_token_url="https://osu.ppy.sh/oauth/token",
        client_kwargs=dict(
            scope="public identify",
        ),
    )
    oauth.init_app(app, fetch_token=fetch_token)
