from typing import List

from flask import Blueprint, abort, render_template
from flask.globals import current_app
from flask_login import current_user
from kmat.models import Submission
from kmat.models.user import Role

blueprint = Blueprint("result", __name__, url_prefix="/result")


@blueprint.before_request
def check_access():
    if not current_user.has_access("admin") and current_app.config["STATUS"] != "end":
        abort(403)


@blueprint.route("/")
def listing():
    submissions: List[Submission] = Submission.query.all()
    judges = Role.query.filter_by(judge=True).first().users

    for s in submissions:
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
        s.score = sum(criteria_scores.values())
        s.criteria_scores = criteria_scores

    submissions.sort(key=lambda x: x.score, reverse=True)
    return render_template(
        "pages/result/listing.html", submissions=submissions, title="Results"
    )
