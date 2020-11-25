import os
import traceback
from typing import Optional

from flask import Blueprint, abort, current_app, redirect, render_template, url_for
from flask.helpers import flash
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms.fields.simple import SubmitField

from kmat.helper import generate_id, generate_name, prepare_osz
from kmat.models import Submission, User
from kmat.plugins import db, requires

current_user: User
blueprint = Blueprint("submission", __name__, url_prefix="/submission")


@blueprint.before_request
def check_access():
    if not current_user.has_access("admin"):
        if not current_user.has_access("submit"):
            return abort(403)
        if current_app.config["STATUS"] != "mapping":
            flash("It is not mapping phase.")
            return redirect(url_for("base.index"))


class EntryForm(FlaskForm):
    osz = FileField(
        "File .osz",
        validators=[FileRequired(), FileAllowed(["osz"])],
    )
    submit = SubmitField("Submit")


def delete_submission(s: Submission):
    data_path = current_app.config.get("DATA_PATH", current_app.instance_path)
    db.session.delete(s)
    db.session.commit()

    # Remove all leading slash before attempting to join
    os.remove(os.path.join(data_path, s.anon_path[1:]))
    os.remove(os.path.join(data_path, s.file_path[1:]))


@blueprint.route("/submit", methods=["GET", "POST"])
@requires("submit")
def submit():
    submitted_entry: Optional[Submission] = Submission.query.filter_by(
        mapper_id=current_user.osu_uid
    ).first()

    form = EntryForm()
    if form.validate_on_submit():
        f = form.osz.data
        data_path = current_app.config.get("DATA_PATH", current_app.instance_path)

        # Generate random filename for original osz file.
        existing_filename = True
        while existing_filename:
            filename = generate_id() + ".osz"
            if not os.path.exists(filename):
                existing_filename = False

        path_original = os.path.join(
            data_path,
            "osz-original",
            filename,
        )
        f.save(path_original)

        # Generate random mapper name for anon judging phase.
        existing_name = True
        while existing_name:
            mapper_anon_name = generate_name()
            if not Submission.query.filter_by(anon_name=mapper_anon_name).first():
                existing_name = False

        path_modified = os.path.join(
            data_path,
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

        # Remove previously submitted entry
        if submitted_entry:
            delete_submission(submitted_entry)

        submission = Submission(
            # We don't need to know the absolute path of the file.
            file_path=path_original.replace(data_path, ""),
            anon_path=path_modified.replace(data_path, ""),
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
        admin_mode=current_user.has_access("admin")
        and current_app.config["STATUS"] != "mapping",
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
