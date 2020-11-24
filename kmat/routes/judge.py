from typing import List
from flask import Blueprint, render_template
from flask_login import current_user

from kmat.models import Submission

blueprint = Blueprint("judge", __name__, url_prefix="/judge")


@blueprint.route("/")
def listing():
    submissions: List[Submission] = Submission.query.all()
    for s in submissions:
        s.has_judged = False
        for judging in s.judgings:
            if judging.judge.osu_uid == current_user.osu_uid:
                s.has_judged = True

    return render_template("pages/judge/listing.html", submissions=submissions)
