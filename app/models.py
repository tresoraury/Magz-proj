from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from . import db
from .extension import db

db = SQLAlchemy()

class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    # description = db.Column(db.String(500), nullable=True)
    # images = db.relationship('Image', backref='item', lazy=True)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)

    def __repr__(self):
        return f'<Item {self.name}>'
    
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    