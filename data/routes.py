import sqlalchemy
from .db_session import SqlAlchemyBase


class Route(SqlAlchemyBase):
    __tablename__ = "routes"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    points = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
