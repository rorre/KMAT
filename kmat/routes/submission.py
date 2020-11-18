import os
import traceback
from typing import Optional

from flask import Blueprint, current_app, redirect, render_template, url_for
from flask.helpers import flash
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms.fields.simple import SubmitField

from kmat.helper import generate_id, generate_name, prepare_osz
from kmat.models import Submission, User
from kmat.plugins import db

current_user: User
blueprint = Blueprint("submission", __name__, url_prefix="/submission")


class EntryForm(FlaskForm):
    osz = FileField(
        "File .osz",
        validators=[FileRequired(), FileAllowed(["osz"])],
    )
    submit = SubmitField("Submit")


def delete_submission(s: Submission):
    db.session.delete(s)
    db.session.commit()

    os.remove(s.anon_path)
    os.remove(s.file_path)


@blueprint.route("/submit", methods=["GET", "POST"])
@login_required
def submit():
    submitted_entry: Optional[Submission] = Submission.query.filter_by(
        mapper_id=current_user.osu_uid
    ).first()

    form = EntryForm()
    if form.validate_on_submit():
        f = form.osz.data
        existing_filename = True
        while existing_filename:
            filename = generate_id() + ".osz"
            if not os.path.exists(filename):
                existing_filename = False

        path_original = os.path.join(
            current_app.config.get("DATA_PATH", current_app.instance_path),
            "osz-original",
            filename,
        )
        f.save(path_original)

        existing_name = True
        while existing_name:
            mapper_anon_name = generate_name()
            if not Submission.query.filter_by(anon_name=mapper_anon_name).first():
                existing_name = False

        path_modified = os.path.join(
            current_app.config.get("DATA_PATH", current_app.instance_path),
            "osz",
            mapper_anon_name + ".osz",
        )

        try:
            artist, title, version = prepare_osz(f, path_modified, mapper_anon_name)
        except ValueError as e:
            flash(str(e))
            traceback.print_exc()

            os.remove(path_original)
            return render_template(
                "pages/submit.html",
                form=form,
                submitted_entry=submitted_entry,
                title="Submit",
            )

        if submitted_entry:
            delete_submission(submitted_entry)

        submission = Submission(
            file_path=path_original,
            anon_path=path_modified,
            mapper=current_user,
            artist=artist,
            title=title,
            difficulty=version,
            anon_name=mapper_anon_name,
        )
        db.session.add(submission)
        db.session.commit()
        flash("Submitted!")
        return redirect(url_for("base.index"))
    return render_template(
        "pages/submit.html",
        form=form,
        submitted_entry=submitted_entry,
        title="Submit",
    )


@blueprint.route("/<submission_id>/remove", methods=["GET", "POST"])
@login_required
def remove(submission_id: str):
    submission = Submission.query.get_or_404(submission_id)
    if submission.mapper_id != current_user.osu_uid:
        flash("You are not allowed to do that.", "danger")
        return redirect(url_for("base.index"), code=400)

    delete_submission(submission)
    flash("Done!", "success")
    return redirect(url_for("submission.submit"))
