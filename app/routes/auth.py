from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

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
            is_premium=True,
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
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')            
        
    return render_template('auth/login.html')

# LOGOUT
@auth_bp.route('/logout')
@login_required
def logout():    
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET','POST'])
def profile():
    
    if request.method == 'POST':        
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # ALTERAR SENHA
        if new_password:

            if not current_password:
                flash('Informe sua senha atual.', 'danger')
                return redirect(url_for('auth.profile'))

            if not check_password_hash(
                current_user.password,
                current_password
            ):
                flash('Senha atual inválida.', 'danger')
                return redirect(url_for('auth.profile'))

            if new_password != confirm_password:
                flash('As senhas não coincidem.', 'danger')
                return redirect(url_for('auth.profile'))

            current_user.password = generate_password_hash(new_password)

        db.session.commit()

        flash('Perfil atualizado com sucesso.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')