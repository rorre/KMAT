from datetime import datetime
from typing import TYPE_CHECKING

import enum
from sqlalchemy.sql.sqltypes import Enum
from kmat.helper import generate_id
from kmat.plugins import db

if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model
    from kmat.models import User

    BaseModel = db.make_declarative_base(Model)
else:
    BaseModel = db.Model


class CriteriaEnum(enum.Enum):
    MusicalRepresentation = "musicRepr"
    Gameplay = "gameplay"
    Creativity = "creativity"
    Hitsounding = "hitsound"


class Score(BaseModel):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    judging: "Judging"

    criteria = db.Column(Enum(CriteriaEnum))
    score = db.Column(db.Float)

    judging_id = db.Column(db.Integer, db.ForeignKey("judging.id"), nullable=False)


class Judging(BaseModel):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    submission: "Submission"
    judge: "User"

    comment = db.Column(db.String)
    scores = db.relationship("Score", backref="judging", lazy=True)

    submission_id = db.Column(
        db.Integer, db.ForeignKey("submission.id"), nullable=False
    )
    judge_id = db.Column(db.Integer, db.ForeignKey("users.osu_uid"), nullable=False)


class Submission(BaseModel):
    id = db.Column(db.String, primary_key=True, nullable=False, default=generate_id)
    mapper: "User"

    # osz
    file_path = db.Column(db.String)
    anon_path = db.Column(db.String)

    # Metadata
    artist = db.Column(db.String)
    title = db.Column(db.String)
    difficulty = db.Column(db.String)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    anon_name = db.Column(db.String, unique=True)

    judgings = db.relationship("Judging", backref="submission", lazy=True)

    mapper_id = db.Column(db.Integer, db.ForeignKey("users.osu_uid"), nullable=False)
