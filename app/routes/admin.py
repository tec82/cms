from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from models import db, Post, Category
from slugify import slugify

import cloudinary.uploader

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Protege todas as rotas deste blueprint
@admin_bp.before_request
@login_required
def protect_admin():
    pass

@admin_bp.route('/')
def dashboard():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('admin/admin.html', posts=posts)

@admin_bp.route('/create', methods=['GET', 'POST'])
def create_post():

    if request.method == 'POST':        
        title = request.form['title']
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        new_category = request.form.get('new_category')
        new_category_desc = request.form.get('new_category_description')

        # PRIORIDADE: nova categoria
        if new_category:
            category = Category(
                name=new_category,
                slug=slugify(new_category),
                description=new_category_desc
            )
            db.session.add(category)
            db.session.commit()
        else:            
            category = Category.query.get(category_id)

        # Upload da imagem
        image = request.files.get('image')

        if image:
            result = cloudinary.uploader.upload(
                image,
                folder="posts",
                width=800,
                crop="scale",
            )
            url = result['secure_url']

        post = Post(
            title=title,
            slug=slugify(title),
            content=content,
            is_paid=bool(request.form.get('paid')),
            category=category,
            image_url=url if image else None
        )

        db.session.add(post)
        db.session.commit()
                
        return redirect(url_for('admin.dashboard'))

    categories = Category.query.all()
    return render_template('admin/create_post.html', categories=categories)

@admin_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def update_post(id):
    post = Post.query.get_or_404(id)

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.is_paid = True if request.form.get('paid') else False

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
            url = result['secure_url']

        # Categoria nova ou existente
        new_category_name = request.form.get('new_category')
        new_category_desc = request.form.get('new_category_description')

        if new_category_name:
            category = Category.query.filter_by(name=new_category_name).first()

            if not category:
                category = Category(
                    name=new_category_name,
                    slug=slugify(new_category_name),
                    description=new_category_desc
                )
                db.session.add(category)
                db.session.flush()

            post.category_id = category.id
        else:
            category_id = request.form.get('category_id')
            if category_id:
                post.category_id = int(category_id)

        db.session.commit()
        return redirect(url_for('admin.dashboard'))

    categories = Category.query.all()
    return render_template('admin/update.html', post=post, categories=categories)

@admin_bp.route('/delete/<id>', methods=['GET'])
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))