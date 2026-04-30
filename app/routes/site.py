from flask import Flask, render_template, redirect, request
from flask import Blueprint, render_template, json
from flask_login import current_user
from models import Post, Category, db
from sqlalchemy import func

site_bp = Blueprint('site', __name__)

@site_bp.route('/')
def index():    
    # POST DESTAQUE (último post)
    featured = Post.query.order_by(Post.created_at.desc()).first()

    # gerar resumo (EditorJS JSON → texto simples)
    summary = ""
    if featured:
        try:
            data = json.loads(featured.content)
            for block in data["blocks"]:
                if block["type"] == "paragraph":
                    summary += block["data"]["text"] + " "
            summary = summary[:150]
        except:
            summary = ""

    # CATEGORIAS + CONTAGEM
    categories = db.session.query(
        Category,
        func.count(Post.id).label('total')
    ).outerjoin(Post).group_by(Category.id).all()

    return render_template(
        'site/index.html',
        featured=featured,
        summary=summary,
        categories=categories
    )

@site_bp.route('/Artigos')
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
    categories = db.session.query(Category, func.count(Post.id).label('total')).outerjoin(Post).group_by(Category.id).all()

    for post in posts_list:
        try:
            # Criamos um atributo temporário 'json_content' que NÃO existe no banco
            # Isso evita que o SQLAlchemy tente salvar a alteração
            post.json_content = json.loads(post.content)
        except:
            post.json_content = {"blocks": []}
    return render_template('site/posts.html', posts=posts_list, categories=categories)

@site_bp.route('/<slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug).first()
    
    if post.is_paid and not current_user.is_authenticated:
        return "Conteúdo pago 🔒"
    
    return render_template('site/post.html', post=post)