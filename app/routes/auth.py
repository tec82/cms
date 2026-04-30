from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# REGISTER
@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            password=generate_password_hash(request.form['password'])
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

# LOGIN
@auth_bp.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        
    return render_template('auth/login.html')

# LOGOUT
@auth_bp.route('/logout')
@login_required
def logout():    
    logout_user()
    return redirect(url_for('auth.login'))