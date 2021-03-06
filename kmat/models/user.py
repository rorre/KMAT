from typing import TYPE_CHECKING, List

from sqlalchemy.orm.collections import attribute_mapped_collection

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

    def __repr__(self) -> str:
        return f"<User(osu_uid='{self.osu_uid}', username='{self.username}')>"

    #########################
    # osu! API + Authlib
    #########################
    osu_uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True, nullable=False)
    access_token = db.Column(db.String, nullable=True)
    refresh_token = db.String(length=200)
    expires_at = db.Column(db.Integer)
    is_active = True
    is_authenticated = True

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

    def has_access(self, permission):
        for role in self.roles.values():
            if getattr(role, permission):
                return True

        return False

    #########################
    # Site stuffs
    #########################
    roles = db.relationship(
        "Role",
        secondary=role_association,
        lazy=False,
        backref=db.backref("users", lazy=False),
        collection_class=attribute_mapped_collection("name"),
    )
    submissions = db.relationship(
        "Submission",
        backref="mapper",
        lazy=True,
        cascade="all,delete,delete-orphan",
    )
    judgings = db.relationship(
        "Judging",
        backref="judge",
        lazy=True,
        cascade="all,delete,delete-orphan",
    )


class Role(BaseModel):
    def __repr__(self) -> str:
        return f"<Role(name='{self.name}')>"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String)
    role_color = db.Column(db.String(6), default="FFFFFF")
    judge = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    submit = db.Column(db.Boolean, default=True)
    users: List[User]
