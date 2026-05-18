from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required,current_user
from models import db, Post, Category
from slugify import slugify


import cloudinary.uploader

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Protege todas as rotas deste blueprint
@admin_bp.before_request
@login_required
def protect_admin():
    if not current_user.is_super_user:
        return redirect(url_for('auth.logout'))       

@admin_bp.route('/')
def dashboard():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('admin/admin.html', posts=posts)


@admin_bp.route('/create', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        try:

                title = request.form['title']
                content = request.form.get('content')
                category_id = request.form.get('category_id')
                category = Category.query.get(category_id)

                image = request.files.get('image')
                url = None

                post = Post(
                    title=title,
                    slug=slugify(title),
                    content=content,
                    is_draft=True if request.form.get('is_draft') else False,            
                    category=category,
                    is_paid=True if request.form.get('paid') else False,
                    is_detach=True if request.form.get('is_detach') else False,
                    image_url='/static/img/default-post.jpg'
                )

                db.session.add(post)
                db.session.commit()

                if image:                                        
                    result = cloudinary.uploader.upload(
                        image,
                        folder="posts",
                        width=800,
                        crop="scale",
                        overwrite=True
                    )
                    
                    post.image_url = result['secure_url']
                    db.session.commit()

        except Exception as e:            
            db.session.rollback()
            flash('Erro ao criar post.','danger')
        
        except Exception as cloud_error:            
            db.session.rollback()
            flash('Post criado, mas houve erro no upload da imagem.','warning')

    categories = Category.query.all()
    return render_template('admin/posts/create_post.html',categories=categories)

@admin_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def update_post(id):

    post = Post.query.get_or_404(id)

    if request.method == 'POST':
        try:
            post.title = request.form.get('title')
            post.slug = slugify(post.title)
            post.content = request.form.get('content')
            post.is_draft = True if request.form.get('is_draft') else False
            post.is_paid = True if request.form.get('paid') else False
            post.is_detach = True if request.form.get('is_detach') else False

            # Categoria
            category_id = request.form.get('category_id')

            if category_id:
                post.category_id = int(category_id)

            # Upload da imagem
            image = request.files.get('image')

            if image:

                result = cloudinary.uploader.upload(
                    image,
                    folder="posts",
                    width=800,
                    crop="scale",
                    overwrite=True
                )

                post.image_url = result['secure_url']

            db.session.commit()

            return redirect(url_for('admin.dashboard'))

        except Exception as e:            
            db.session.rollback()
            flash('Erro ao criar post.','danger')
        
        except Exception as cloud_error:            
            db.session.rollback()
            flash('Post criado, mas houve erro no upload da imagem.','warning')

    categories = Category.query.all()

    return render_template(
        'admin/posts/update_post.html',
        post=post,
        categories=categories
    )

@admin_bp.route('/delete/<id>', methods=['GET'])
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))

#  ROTAS DE CATEGORIAS
@admin_bp.route('/categories')
def categories():
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template(
        'admin/categories/index.html',
        categories=categories
    )


@admin_bp.route('/categories/create', methods=['GET', 'POST'])
def create_category():

    if request.method == 'POST':

        name = request.form.get('name')
        description = request.form.get('description')

        category = Category(
            name=name,
            slug=slugify(name),
            description=description,
            is_paid=True if request.form.get('paid') else False,
            is_detach=True if request.form.get('is_detach') else False,
        )

        db.session.add(category)
        db.session.commit()

        return redirect(url_for('admin.categories'))

    return render_template('admin/categories/create.html')


@admin_bp.route('/categories/update/<int:id>', methods=['GET', 'POST'])
def update_category(id):

    category = Category.query.get_or_404(id)

    if request.method == 'POST':
        category.name = request.form.get('name')
        category.slug = slugify(category.name)
        category.description = request.form.get('description')
        category.is_paid = True if request.form.get('paid') else False
        category.is_detach = True if request.form.get('is_detach') else False   
        db.session.commit()

        return redirect(url_for('admin.categories'))

    return render_template(
        'admin/categories/update.html',
        category=category
    )


@admin_bp.route('/categories/delete/<int:id>')
def delete_category(id):

    category = Category.query.get_or_404(id)

    db.session.delete(category)
    db.session.commit()

    return redirect(url_for('admin.categories'))