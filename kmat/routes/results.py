from flask import Blueprint, abort, render_template, request
from flask.globals import current_app
from flask_login import current_user
from kmat.models import Submission
from kmat.models.user import Role

blueprint = Blueprint("result", __name__, url_prefix="/result")


@blueprint.before_request
def check_access():
    if not current_user.is_authenticated:
        return abort(401)

    if not current_user.has_access("admin") and current_app.config["STATUS"] != "end":
        abort(403)


@blueprint.route("/")
def listing():
    page = request.args.get("page", 1, type=int)
    submissions = Submission.query.order_by(Submission.total_score.desc()).paginate(
        page, 10
    )
    judges = Role.query.filter_by(judge=True).first().users

    for s in submissions.items:
        score = 0.0
        criteria_scores = {
            "musicRepr": 0,
            "gameplay": 0,
            "creativity": 0,
            "hitsound": 0,
        }
        checked_judges = []

        for j in s.judgings:
            for criteria, score in j.scores.items():
                criteria_scores[criteria] += score.score
            checked_judges.append(j.judge)

        s.missing_judges = set(judges) - set(checked_judges)
        s.criteria_scores = criteria_scores

    return render_template(
        "pages/result/listing.html",
        submissions=submissions,
        title="Results",
        admin_mode=current_user.has_access("admin")
        and current_app.config["STATUS"] != "end",
    )
