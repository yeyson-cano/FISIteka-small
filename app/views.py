from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from app.models import User, Resource

def is_admin():
    return current_user.role == 'profesor'

def can_edit_resource(resource):
    return is_admin() or current_user == resource.author

@app.route('/')
@login_required
def index():
    resources = Resource.query.all()
    return render_template('index.html', resources=resources)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already taken. Please choose another.', 'error')
        elif not username or not password:
            flash('Username and password are required fields.', 'error')
        else:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/resource/new', methods=['GET', 'POST'])
@login_required
def new_resource():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        resource = Resource(title=title, content=content, author=current_user)
        db.session.add(resource)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new_resource.html')

@app.route('/resource/<int:resource_id>')
def view_resource(resource_id):
    resource = Resource.query.get(resource_id)
    if not resource:
        flash('Resource not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('view_resource.html', resource=resource)

@app.route('/resource/edit/<int:resource_id>', methods=['GET', 'POST'])
@login_required
def edit_resource(resource_id):
    resource = Resource.query.get(resource_id)
    if not resource:
        flash('Resource not found', 'error')
        return redirect(url_for('index'))

    if not can_edit_resource(resource):
        flash('Permission denied', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        resource.title = request.form['title']
        resource.content = request.form['content']
        db.session.commit()
        flash('Resource updated successfully', 'success')
        return redirect(url_for('index'))

    return render_template('edit_resource.html', resource=resource)

@app.route('/resource/delete/<int:resource_id>', methods=['POST'])
@login_required
def delete_resource(resource_id):
    resource = Resource.query.get(resource_id)
    if not resource:
        flash('Resource not found', 'error')
        return redirect(url_for('index'))

    if not can_edit_resource(resource):
        flash('Permission denied', 'error')
        return redirect(url_for('index'))

    db.session.delete(resource)
    db.session.commit()
    flash('Resource deleted successfully', 'success')
    return redirect(url_for('index'))
