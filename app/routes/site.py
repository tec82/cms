from flask import Blueprint, render_template, request, abort
from flask_login import current_user
from models import PostView, Favorite, Post, Category, TrailProgress, db
from sqlalchemy import func
import json

site_bp = Blueprint('site', __name__)

@site_bp.route('/')
def index():    
    # POST DESTAQUE (último post)
    featured = Post.query.filter(Post.is_detach == True).first()     
    recent_posts = Post.query.filter(Post.is_detach == False,Post.is_paid == False).order_by(Post.id.desc()).limit(5).all()

    # CATEGORIAS + CONTAGEM 
    categories = db.session.query(
        Category,
        func.count(Post.id).label('total')
    ).outerjoin(Post).filter(Category.is_detach).group_by(Category.id).all()

    return render_template(
        'site/index.html',
        featured=featured,
        recent_posts=recent_posts,
        categories=categories
    )


@site_bp.route('/artigos')
def posts():
    # Captura busca e categoria
    search_query = request.args.get('q')
    category_slug = request.args.get('category')

    query = Post.query

    if search_query:
        query = query.filter(Post.title.contains(search_query),Post.is_paid == False)
    
    if category_slug:
        query = query.join(Category).filter(Category.slug == category_slug,Post.is_paid == False)

    # Pegamos os posts e as categorias
    posts_list = query.filter(Post.is_detach == False,Post.is_paid == False).order_by(Post.id.desc()).all()

    categories = db.session.query(
        Category,
        func.count(Post.id).label('total')
    ).outerjoin(Post).filter(Category.is_detach,Post.is_paid == False).group_by(Category.id).all()

    return render_template(
        'site/posts.html',
        posts=posts_list,
        categories=categories
    )


@site_bp.route('/artigo/<slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug).first()
    # conteúdo pago (se quiser usar depois)
    if post.is_paid and not current_user.is_authenticated:
         return "Conteúdo pago 🔒"   

    # evita erro de None
    if not post:
        abort(404)

    favorite = None

    if current_user.is_authenticated and not current_user.is_super_user:
        # REGISTRA VISUALIZAÇÃO
        existing_view = PostView.query.filter_by(user_id=current_user.id,post_id=post.id).first()
        if not existing_view:
            view = PostView(user_id=current_user.id,post_id=post.id)
            db.session.add(view)
            db.session.commit()

        # REGISTRA PROGRESSO NA TRILHA
        if post.category and post.category.is_paid:
            progress = TrailProgress.query.filter_by(
                user_id=current_user.id,
                category_id=post.category_id
            ).first()

            if not progress:
                progress = TrailProgress(
                    user_id=current_user.id,
                    category_id=post.category_id,
                    last_post_id=post.id
                )
                db.session.add(progress)
            else:
                progress.last_post_id = post.id
            
            db.session.commit()

        # EXIBE SE O POST ESTÁ NOS FAVORITOS DO USUÁRIO
        favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            post_id=post.id
        ).first()
        
    

    return render_template('site/post.html', post=post, favorite=favorite)


@site_bp.route('/trilhas')
def trilhas():
    categories_query = db.session.query(
        Category,
        func.count(Post.id).label('total')
    ).outerjoin(
        Post,
        db.and_(Post.category_id == Category.id, Post.is_draft == False)
    ).filter(
        Category.is_paid == True
    ).group_by(
        Category.id
    ).all()
    
    trilhas_data = []
    
    for category, total in categories_query:
        progress_pct = 0
        last_post = None
        started = False
        
        if current_user.is_authenticated and not current_user.is_super_user:
            # Pegar o registro do progresso
            progress = TrailProgress.query.filter_by(
                user_id=current_user.id,
                category_id=category.id
            ).first()
            
            if progress:
                started = True
                last_post = progress.last_post
                
                # Calcular porcentagem: total de posts na categoria vistos pelo usuário
                vistos_count = db.session.query(func.count(PostView.id))\
                    .join(Post, Post.id == PostView.post_id)\
                    .filter(
                        PostView.user_id == current_user.id,
                        Post.category_id == category.id,
                        Post.is_draft == False
                    ).scalar() or 0
                
                if total > 0:
                    progress_pct = int((vistos_count / total) * 100)
                    if progress_pct > 100:
                        progress_pct = 100
        
        trilhas_data.append({
            'category': category,
            'total': total,
            'started': started,
            'progress_pct': progress_pct,
            'last_post': last_post
        })
        
    return render_template(
        'site/trilhas.html',
        trilhas=trilhas_data
    )

@site_bp.route('/trilhas-detalhes/<slug>')
def datail_trilhas(slug):
    category = Category.query.filter_by(
        slug=slug,
        is_paid=True
    ).first_or_404()

    posts = (
        Post.query
        .filter_by(
            category_id=category.id,
            is_draft=False
        )
        .order_by(Post.created_at.asc())
        .all()
    )

    total = len(posts)
    viewed_post_ids = set()
    last_post_id = None
    progress_pct = 0
    next_post = None

    if current_user.is_authenticated and not current_user.is_super_user:
        # Buscar os posts vistos pelo usuário nesta categoria
        vistos = db.session.query(PostView.post_id)\
            .join(Post, Post.id == PostView.post_id)\
            .filter(
                PostView.user_id == current_user.id,
                Post.category_id == category.id
            ).all()
        viewed_post_ids = {v[0] for v in vistos}

        # Calcular a porcentagem
        if total > 0:
            progress_pct = int((len(viewed_post_ids) / total) * 100)
            if progress_pct > 100:
                progress_pct = 100

        # Buscar onde o usuário parou
        progress = TrailProgress.query.filter_by(
            user_id=current_user.id,
            category_id=category.id
        ).first()
        if progress:
            last_post_id = progress.last_post_id

        # Encontrar o próximo post não lido
        for post in posts:
            if post.id not in viewed_post_ids:
                next_post = post
                break
        
        # Se todos já foram lidos, ou se não há nenhum não lido,
        # e o usuário já começou, podemos usar o last_post_id ou o primeiro
        if not next_post and progress:
            next_post = Post.query.get(last_post_id)
    
    # Se não começou ou não está logado, o próximo é o primeiro post
    if not next_post and total > 0:
        next_post = posts[0]

    return render_template(
        'site/trilha-detail.html',
        posts=posts,
        category=category,
        total=total,
        viewed_post_ids=viewed_post_ids,
        last_post_id=last_post_id,
        progress_pct=progress_pct,
        next_post=next_post
    )