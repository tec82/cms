from flask import Blueprint, render_template, request, abort
from flask_login import current_user
from models import Post, Category, db
from sqlalchemy import func
import json

site_bp = Blueprint('site', __name__)

@site_bp.route('/')
def index():    
    # POST DESTAQUE (último post)
    featured = Post.query.filter(Post.is_detach == True).first()     

    # CATEGORIAS + CONTAGEM 
    categories = db.session.query(
        Category,
        func.count(Post.id).label('total')
    ).outerjoin(Post).group_by(Category.id).all()

    return render_template(
        'site/index.html',
        featured=featured,
        categories=categories
    )


@site_bp.route('/artigos')
def posts():
    # Captura busca e categoria
    search_query = request.args.get('q')
    category_slug = request.args.get('category')

    query = Post.query

    if search_query:
        query = query.filter(Post.title.contains(search_query))
    
    if category_slug:
        query = query.join(Category).filter(Category.slug == category_slug)

    # Pegamos os posts e as categorias
    posts_list = query.order_by(Post.id.desc()).all()

    categories = db.session.query(
        Category,
        func.count(Post.id).label('total')
    ).outerjoin(Post).group_by(Category.id).all()

    # Processa conteúdo JSON
    for post in posts_list:
        try:
            post.json_content = json.loads(post.content)
        except:
            post.json_content = {"blocks": []}

    return render_template(
        'site/posts.html',
        posts=posts_list,
        categories=categories
    )


# ✅ ROTA CORRIGIDA (IMPORTANTE)
@site_bp.route('/artigo/<slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug).first()

    # 🔒 evita erro de None
    if not post:
        abort(404)

    # 🔒 conteúdo pago (se quiser usar depois)
    # if post.is_paid and not current_user.is_authenticated:
    #     return "Conteúdo pago 🔒"

    # Processa JSON também aqui (faltava isso)
    try:
        post.json_content = json.loads(post.content)
    except:
        post.json_content = {"blocks": []}

    return render_template('site/post.html', post=post)