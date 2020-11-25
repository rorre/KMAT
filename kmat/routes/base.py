from flask import Blueprint, current_app, render_template, send_from_directory

from kmat.models import User

blueprint = Blueprint("base", __name__)


@blueprint.route("/")
def index():
    return render_template("pages/index.html")


@blueprint.route("/informasi")
def info():
    return render_template("pages/information.html", title="Informasi")


@blueprint.route("/staff")
def staff():
    staffs = User.query.filter(User.roles.any(admin=True)).all()
    judges = User.query.filter(User.roles.any(judge=True)).all()
    return render_template(
        "pages/staff.html",
        title="Staff",
        staffs=staffs,
        judges=judges,
    )


@blueprint.route("/data/<path:filename>")
def cdn(filename):
    return send_from_directory(current_app.config["DATA_PATH"], filename)
