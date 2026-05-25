from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

from auth.oauth import google

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# LOGIN
@auth_bp.route('/', methods=['GET','POST'])
def login():
    return render_template('auth/login.html')

# LOGOUT
@auth_bp.route('/logout')
@login_required
def logout():    
    logout_user()
    return redirect(url_for('auth.login'))

#@auth_bp.route('/profile', methods=['GET','POST'])
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

# LOGIN COM GOOGLE
@auth_bp.route('/login/google')
def login_google():

    redirect_uri = url_for(
        'auth.google_callback',
        _external=True
    )

    return google.authorize_redirect(redirect_uri)



@auth_bp.route('/google/callback')
def google_callback():

    token = google.authorize_access_token()
    user_info = token['userinfo']
    google_id = user_info['sub']
    email = user_info['email']
    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            username=user_info['name'],
            email=email,
            google_id=google_id,
            avatar=user_info['picture'],
            provider='google',
            password=None            
        )
        db.session.add(user)
    else:
        user.google_id = google_id
        #user.is_super_user = True

    db.session.commit()
    login_user(user)

    flash(
        'Login realizado com Google.',
        'success'
    )

    return redirect(url_for('site.index'))   