from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required,current_user
from models import db, Post, Category, User,Payment
from slugify import slugify
from werkzeug.security import generate_password_hash


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
                try:
                    order = int(request.form.get('order', 0))
                except (ValueError, TypeError):
                    order = 0

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
                    image_url='/static/img/default-post.jpg',
                    order=order
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
            #db.session.rollback()
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

            # Ordem
            try:
                post.order = int(request.form.get('order', 0))
            except (ValueError, TypeError):
                pass

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
        style = request.form.get('style')

        category = Category(
            name=name,
            slug=slugify(name),
            description=description,
            style=style,
            is_paid=True if request.form.get('is_paid') else False,
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
        category.is_paid = True if request.form.get('is_paid') else False
        category.is_detach = True if request.form.get('is_detach') else False
        category.style = request.form.get('style')

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


@admin_bp.route('/users')
def users():
    users = User.query.order_by(User.id.desc()).all()    
    return render_template('admin/users/index.html', users=users)

@admin_bp.route('/users/update/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        username = request.form.get('username') or request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        provider = request.form.get('provider')
        google_id = request.form.get('google_id')
        github_id = request.form.get('github_id')
        
        # Se for o próprio usuário, não permite remover privilégio de admin
        if user.id == current_user.id:
            is_super_user = True
        else:
            is_super_user = True if request.form.get('is_super_user') else False

        if not username or not email:
            flash('Nome de usuário e E-mail são obrigatórios.', 'danger')
            return redirect(url_for('admin.update_user', id=user.id))

        # Verificar duplicados excluindo o próprio
        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.id != user.id:
            flash('Este e-mail já está em uso por outro usuário.', 'danger')
            return redirect(url_for('admin.update_user', id=user.id))

        existing_username = User.query.filter_by(username=username).first()
        if existing_username and existing_username.id != user.id:
            flash('Este nome de usuário já está em uso por outro usuário.', 'danger')
            return redirect(url_for('admin.update_user', id=user.id))

        user.username = username
        user.email = email
        user.is_super_user = is_super_user
        
        if provider:
            user.provider = provider
        if google_id:
            user.google_id = google_id
        if github_id:
            user.github_id = github_id

        if password:
            user.password = generate_password_hash(password)

        avatar_file = request.files.get('avatar')
        if avatar_file:
            try:
                result = cloudinary.uploader.upload(
                    avatar_file,
                    folder="avatars",
                    width=200,
                    height=200,
                    crop="thumb",
                    gravity="face",
                    overwrite=True
                )
                user.avatar = result['secure_url']
            except Exception as e:
                flash('Houve erro no upload do novo avatar.', 'warning')
        else:
            form_avatar = request.form.get('avatar')
            if form_avatar:
                user.avatar = form_avatar

        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/users/update.html', user=user)


@admin_bp.route('/users/delete/<int:id>', methods=['GET', 'POST'])
def delete_user(id):
    if id == current_user.id:
        flash('Você não pode excluir a si mesmo!', 'danger')
        return redirect(url_for('admin.users'))

    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('admin.users'))
    