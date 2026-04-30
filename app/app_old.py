from flask import Flask, render_template, request, redirect
from models import db, User, Category, Post, Course, Lesson, Purchase
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from slugify import slugify
import json

from sqlalchemy import func


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    db.create_all()

# HOME
@app.route('/')
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
        'index.html',
        featured=featured,
        summary=summary,
        categories=categories
    )

# REGISTER
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            password=generate_password_hash(request.form['password'])
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

# LOGIN
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect('/admin')
    return render_template('login.html')

# LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

# CREATE POST
@app.route('/admin', methods=['GET','POST'])
@login_required
def adminstrator():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('admin.html', posts=posts)

# CREATE POST
@app.route('/create', methods=['GET','POST'])
@login_required
def create_post():

    if request.method == 'POST':        
        title = request.form['title']
        content = request.form['content']
        category_id = request.form.get('category_id')
        new_category = request.form.get('new_category')

        # 🔥 PRIORIDADE: nova categoria
        if new_category:
            category = Category(
                name=new_category,
                slug=slugify(new_category)
            )
            db.session.add(category)
            db.session.commit()
        else:            
            category = Category.query.get(category_id)

        post = Post(
            title=title,
            slug=slugify(title),
            content=content,
            is_paid=bool(request.form.get('paid')),
            category=category
        )

        db.session.add(post)
        db.session.commit()

        return redirect('/admin')

    categories = Category.query.all()
    return render_template('create_post.html', categories=categories)

# VIEW POST
@app.route('/posts')
def posts():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('posts.html', posts=posts)

@app.route('/post/<slug>')
def post(slug):
    post = Post.query.filter_by(slug=slug).first()

    if post.is_paid and not current_user.is_authenticated:
        return "Conteúdo pago 🔒"

    content = json.loads(post.content)
    return render_template('post.html', post=post, content=content)

# COURSES
@app.route('/courses')
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/course/<int:id>')
def course(id):
    course = Course.query.get(id)
    lessons = Lesson.query.filter_by(course_id=id).all()
    return render_template('course.html', course=course, lessons=lessons)

def has_access(user, course_id):
    return Purchase.query.filter_by(user_id=user.id, course_id=course_id).first()

@app.route('/lesson/<int:id>')
@login_required
def lesson(id):
    lesson = Lesson.query.get(id)

    if not has_access(current_user, lesson.course_id):
        return "Compre o curso"

    return render_template('lesson.html', lesson=lesson)

if __name__ == '__main__':
    app.run(debug=True)