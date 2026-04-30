import os
from dotenv import load_dotenv

load_dotenv()  # 🔥 carrega o .env

from flask import Flask
from models import db, User
from flask_login import LoginManager
from routes.site import site_bp
from routes.admin import admin_bp
from routes.auth import auth_bp

import cloudinary
import cloudinary.uploader

# ☁️ Config Cloudinary via ENV
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

app = Flask(__name__)

# Flask
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# MySQL
'''app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)'''
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(site_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)