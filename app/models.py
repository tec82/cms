from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200), nullable=True)
    avatar = db.Column(db.String(500))
    provider = db.Column(db.String(50))
    google_id = db.Column(db.String(200))
    github_id = db.Column(db.String(200))

    is_super_user = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    slug = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    is_paid = db.Column(db.Boolean, default=False)    
    is_detach = db.Column(db.Boolean, default=False)
    style = db.Column(db.String(100))
    

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #order = db.Column(db.Integer, default=0)
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
    created_at = db.Column(db.DateTime,default=lambda: datetime.now(timezone.utc))

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
    created_at = db.Column(db.DateTime,default=lambda: datetime.now(timezone.utc))


class PostView(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    post_id = db.Column(db.Integer,db.ForeignKey('post.id'),nullable=False)
    viewed_at = db.Column(db.DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),nullable=False)

    # Impede visualizações duplicadas
    __table_args__ = (
        db.UniqueConstraint(
            'user_id',
            'post_id',
            name='unique_user_post_view'
        ),
    )

    # Relacionamentos
    user = db.relationship(
        'User',
        backref=db.backref(
            'views',
            lazy=True,
            cascade='all, delete-orphan'
        )
    )

    post = db.relationship(
        'Post',
        backref=db.backref(
            'views',
            lazy=True,
            cascade='all, delete-orphan'
        )
    )

class TrailProgress(db.Model):
    __tablename__ = 'trail_progress'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey('category.id'),
        nullable=False
    )

    last_post_id = db.Column(
        db.Integer,
        db.ForeignKey('post.id'),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Impede múltiplos registros para o mesmo usuário na mesma trilha
    __table_args__ = (
        db.UniqueConstraint(
            'user_id',
            'category_id',
            name='unique_user_category_progress'
        ),
    )

    # Relacionamentos
    user = db.relationship(
        'User',
        backref=db.backref(
            'trail_progresses',
            lazy=True,
            cascade='all, delete-orphan'
        )
    )

    category = db.relationship(
        'Category',
        backref=db.backref(
            'trail_progresses',
            lazy=True,
            cascade='all, delete-orphan'
        )
    )

    last_post = db.relationship('Post')