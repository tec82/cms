from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))    
    is_super_user = db.Column(db.Boolean, default=False)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    slug = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    is_paid = db.Column(db.Boolean, default=False)    
    is_detach = db.Column(db.Boolean, default=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    slug = db.Column(db.String(200), unique=True)
    content = db.Column(db.Text)
    is_draft = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(500))
    is_paid = db.Column(db.Boolean, default=False)
    is_detach = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category')   

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer,db.ForeignKey('post.id'))
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    amount = db.Column(db.Float)
    status = db.Column(db.String(50))
    # paid
    # pending
    # canceled
    provider = db.Column(db.String(50))
    # stripe
    # mercado_pago
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

class PostView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer,db.ForeignKey('post.id'))
    viewed_at = db.Column(db.DateTime,default=datetime.utcnow)