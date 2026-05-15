from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

from auth.oauth import google

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# REGISTER
@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        user_exists = User.query.filter(User.username == username).first()

        if user_exists:
            flash('Este usuário já existe.', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(
            username=username,
            password=generate_password_hash(request.form['password']),            
            is_super_user=False 
        )
        db.session.add(user)
        db.session.commit()

        flash('Usuário registrado com sucesso.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

# LOGIN
@auth_bp.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            if user.is_super_user:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('dashboard.index'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')            
        
    return render_template('auth/login.html')

# LOGOUT
@auth_bp.route('/logout')
@login_required
def logout():    
    logout_user()
    return redirect(url_for('auth.login'))