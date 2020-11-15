from flask import (
    Blueprint,
    render_template,
)

blueprint = Blueprint("base", __name__)


@blueprint.route("/")
def index():
    return render_template("pages/index.html")


@blueprint.route("/informasi")
def info():
    return render_template("pages/information.html")