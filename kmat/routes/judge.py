from typing import Any, Dict, List, Union

from flask import Blueprint, abort, render_template, request
from flask.globals import current_app
from flask.helpers import flash, url_for
from flask_login import current_user
from werkzeug.utils import redirect

from kmat.models import Submission
from kmat.models.submission import CriteriaEnum, Judging, Score
from kmat.plugins import db

blueprint = Blueprint("judge", __name__, url_prefix="/judge")


@blueprint.before_request
def check_access():
    if not current_user.has_access("admin"):
        if not current_user.has_access("judge"):
            return abort(403)
        if current_app.config["STATUS"] != "judging":
            flash("It is not judging phase.")
            return redirect(url_for("base.index"))


@blueprint.app_errorhandler(500)
def handle_error(e):
    return {"error": True, "message": str(e)}, 500


@blueprint.route("/")
def listing():
    submissions: List[Submission] = Submission.query.all()
    for s in submissions:
        s.has_judged = False
        for judging in s.judgings:
            if judging.judge.osu_uid == current_user.osu_uid:
                s.has_judged = True
                s.my_judging = judging

    return render_template(
        "pages/judge/listing.html", submissions=submissions, title="Judge"
    )


@blueprint.route("/<submission_id>", methods=["POST"])
def judge(submission_id: str):
    js: Dict[str, Any] = request.get_json()

    submission: Submission = Submission.query.get(submission_id)
    judging_obj: Judging = Judging.query.filter_by(
        submission_id=submission_id, judge_id=current_user.osu_uid
    ).one_or_none()

    if not judging_obj:
        judging_obj = Judging(
            submission=submission,
            judge=current_user,
            comment=js["comment"],
        )
    else:
        judging_obj.comment = js["comment"]

    scores = []
    score: Dict[str, Union[str, int]]
    for score in js["scores"]:
        score["criteria"] = CriteriaEnum(score["name"])
        score["score"] = score["value"]
        del score["name"]
        del score["value"]

        # Check for existing criteria scoring
        score_obj = Score.query.filter_by(
            judging_id=judging_obj.id,
            criteria=score["criteria"],
        ).one_or_none()

        if score_obj:
            # If it exists, then just update it
            for key, value in score.items():
                setattr(score_obj, key, value)
        else:
            # Else, create a new object.
            score["judging"] = judging_obj
            score_obj = Score(**score)

        scores.append(score_obj)

    db.session.add_all(scores)
    db.session.commit()

    return {"error": False, "message": "OK"}
