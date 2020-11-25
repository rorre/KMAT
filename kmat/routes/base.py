from flask import Blueprint, current_app, render_template, send_from_directory

from kmat.models import Role

blueprint = Blueprint("base", __name__)


@blueprint.route("/")
def index():
    return render_template("pages/index.html")


@blueprint.route("/informasi")
def info():
    return render_template("pages/information.html", title="Informasi")


@blueprint.route("/staff")
def staff():
    # Not using User.query because in terms of performance, it will be 100x
    # more awful than this one.
    staff_roles = Role.query.filter_by(admin=True).all()
    judge_roles = Role.query.filter_by(judge=True).all()

    staffs = []
    for role in staff_roles:
        staffs.extend(list(role.users))

    judges = []
    for role in judge_roles:
        judges.extend(list(role.users))

    return render_template(
        "pages/staff.html",
        title="Staff",
        staffs=staffs,
        judges=judges,
    )


@blueprint.route("/data/<path:filename>")
def cdn(filename):
    return send_from_directory(current_app.config["DATA_PATH"], filename)
