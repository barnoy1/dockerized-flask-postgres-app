

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, Time
from flask_login import UserMixin
from sqlalchemy.schema import Sequence

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def to_dict(self):
        return {'id': self.id, 'name': self.name}
