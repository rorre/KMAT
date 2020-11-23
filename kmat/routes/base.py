from flask import Blueprint, render_template

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
