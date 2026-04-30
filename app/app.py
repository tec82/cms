from flask import Flask
from models import db, User
from flask_login import LoginManager
from routes.site import site_bp
from routes.admin import admin_bp
from routes.auth import auth_bp

import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    cloud_name="dewdl5bvd",
    api_key="658834264543314",
    api_secret="9nKHfYhdxdGs7nFSrPDGExLt7rE"
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Define para onde vai quem não está logado
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# REGISTRO DOS BLUEPRINTS
app.register_blueprint(site_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)