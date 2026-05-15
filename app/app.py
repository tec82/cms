import os

from flask import Flask
from models import db, User
from flask_login import LoginManager

from routes.site import site_bp
from routes.admin import admin_bp
from routes.auth import auth_bp

import cloudinary
import cloudinary.uploader

DEBUG = os.getenv('DEBUG', 'False')

# ☁️ Config Cloudinary via ENV
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    db.create_all()
    
app.register_blueprint(site_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)