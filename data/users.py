import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    username = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    route = orm.relation("Route", back_populates="user")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self):
        return check_password_hash(self.hashed_password)
