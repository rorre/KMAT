from datetime import datetime
from typing import TYPE_CHECKING

from kmat.plugins import db, login_manager

if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model

    BaseModel = db.make_declarative_base(Model)
else:
    BaseModel = db.Model

role_association = db.Table(
    "role_user",
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.osu_uid"), primary_key=True),
)


class User(BaseModel):
    __tablename__ = "users"

    #########################
    # osu! API + Authlib
    #########################
    osu_uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True, nullable=False)
    access_token = db.Column(db.String, nullable=True)
    refresh_token = db.String(length=200)
    expires_at = db.Column(db.Integer)

    @staticmethod
    @login_manager.user_loader
    def load_user(osu_uid):
        return User.query.filter_by(osu_uid=osu_uid).first()

    def get_id(self):
        return str(self.osu_uid)

    def to_token(self):
        return dict(
            access_token=self.access_token,
            token_type="Bearer",
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
        )

    #########################
    # Site stuffs
    #########################
    roles = db.relationship(
        "Role",
        secondary=role_association,
        lazy="subquery",
        backref=db.backref("users", lazy=True),
    )
    submissions = db.relationship("Submission", backref="mapper", lazy=True)


class Submission(BaseModel):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    file_path = db.Column(db.String)
    mapper_id = db.Column(db.Integer, db.ForeignKey("users.osu_uid"), nullable=False)
    artist = db.Column(db.String)
    title = db.Column(db.String)
    difficulty = db.Column(db.String)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Role(BaseModel):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    role_color = db.Column(db.String(6))
    judge = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
