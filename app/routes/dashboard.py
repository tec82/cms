from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from models import (db,Post,Favorite,Payment,PostView)

dashboard_bp = Blueprint('dashboard', __name__,url_prefix='/dashboard')


# =========================================================
# DASHBOARD HOME
# =========================================================
@dashboard_bp.route('/')
@login_required
def index():

    favorites_count = Favorite.query.filter_by(user_id=current_user.id).count()
    payments_count = Payment.query.filter_by(user_id=current_user.id).count()
    history_count = PostView.query.filter_by(user_id=current_user.id).count()
    premium_posts_count = Post.query.filter_by(is_paid=True).count()

    # Últimos acessos
    recent_views = db.session.query(PostView, Post).join(Post, Post.id == PostView.post_id).filter(PostView.user_id == current_user.id).order_by(PostView.viewed_at.desc()).limit(5).all()

    # Últimos pagamentos
    recent_payments = Payment.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Payment.created_at.desc()
    ).limit(5).all()

    return render_template(
        'dashboard/index.html',

        favorites_count=favorites_count,
        payments_count=payments_count,
        history_count=history_count,
        premium_posts_count=premium_posts_count,

        recent_views=recent_views,
        recent_payments=recent_payments
    )


# =========================================================
# FAVORITOS
# =========================================================
@dashboard_bp.route('/favorites')
@login_required
def favorites():

    favorites = db.session.query(Favorite, Post)\
        .join(Post, Post.id == Favorite.post_id)\
        .filter(Favorite.user_id == current_user.id)\
        .order_by(Favorite.created_at.desc())\
        .all()

    return render_template(
        'dashboard/favorites.html',
        favorites=favorites
    )

'''
# =========================================================
# ADICIONAR FAVORITO
# =========================================================
@dashboard_bp.route('/favorite/add/<int:post_id>')
@login_required
def add_favorite(post_id):

    exists = Favorite.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()

    if exists:

        flash(
            'Este post já está nos favoritos.',
            'warning'
        )

        return redirect(url_for('site.post', id=post_id))

    favorite = Favorite(
        user_id=current_user.id,
        post_id=post_id
    )

    db.session.add(favorite)
    db.session.commit()

    flash(
        'Post adicionado aos favoritos.',
        'success'
    )

    return redirect(url_for('site.post', id=post_id))


# =========================================================
# REMOVER FAVORITO
# =========================================================
@dashboard_bp.route('/favorite/remove/<int:id>')
@login_required
def remove_favorite(id):

    favorite = Favorite.query.get_or_404(id)

    if favorite.user_id != current_user.id:

        flash(
            'Acesso negado.',
            'danger'
        )

        return redirect(url_for('dashboard.favorites'))

    db.session.delete(favorite)
    db.session.commit()

    flash(
        'Favorito removido.',
        'success'
    )

    return redirect(url_for('dashboard.favorites'))


# =========================================================
# HISTÓRICO
# =========================================================
@dashboard_bp.route('/history')
@login_required
def history():

    history = db.session.query(PostView, Post)\
        .join(Post, Post.id == PostView.post_id)\
        .filter(PostView.user_id == current_user.id)\
        .order_by(PostView.viewed_at.desc())\
        .all()

    return render_template(
        'dashboard/history.html',
        history=history
    )


# =========================================================
# PAGAMENTOS
# =========================================================
@dashboard_bp.route('/payments')
@login_required
def payments():

    payments = Payment.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Payment.created_at.desc()
    ).all()

    return render_template(
        'dashboard/payments.html',
        payments=payments
    )


# =========================================================
# POSTS PREMIUM
# =========================================================
@dashboard_bp.route('/premium')
@login_required
def premium_posts():

    if not current_user.is_premium:

        flash(
            'Você precisa de um plano premium.',
            'warning'
        )

        return redirect(url_for('dashboard.index'))

    posts = Post.query.filter_by(
        is_paid=True
    ).order_by(
        Post.created_at.desc()
    ).all()

    return render_template(
        'dashboard/premium.html',
        posts=posts
    )'''
