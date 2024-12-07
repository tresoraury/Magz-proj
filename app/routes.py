from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from .models import db, Item, User
from flask_login import login_user, login_required, logout_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from werkzeug.utils import secure_filename
import os
from flask import current_app

main = Blueprint('main', __name__)
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='sha256')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Successfully Registered!')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('main.item_page'))
        flash('Login failed! Please try again.')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('login.html')

@main.route('/items', methods=['GET'])
def item_page():
    items = Item.query.all()
    logging.debug(f"Items retrieved: {items}")
    return render_template('items.html', items=items)

@main.route('/items', methods=['POST'])
def create_item():
    item = Item(name=request.json['name']) 
    db.session.add(item)
    db.session.commit()
    return jsonify({'id': item.id, 'name': item.name}), 201

@main.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    item.name = request.json['name']
    db.session.commit()
    return jsonify({'id': item.id, 'name': item.name})

@main.route('/items/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    if request.form.get('_method') == 'DELETE':
        item = Item.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted !')
        return redirect(url_for('main.item_page'))
    return "method not allowed", 405

@main.route('/update_item/<int:item_id>', methods=['GET', 'POST'])
def update_item_page(item_id):
    item = Item.query.get_or_404(item_id)
    if request.method == 'POST':
        item.name = request.form['name']
        db.session.commit()
        flash('Item updated !')
        return redirect(url_for('main.item_page'))
    return render_template('update_item.html', item=item)

@main.route('/add_item_page', methods=['GET', 'POST'])
def add_item_page():
    if request.method == 'POST':
        item_name = request.form['name']
        image_files = request.files.getlist('images')  
        image_urls = []

        images_dir = os.path.join(current_app.root_path, 'static/images')
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        for image_file in image_files:
            if image_file:
                filename = secure_filename(image_file.filename)
                save_path = os.path.join(images_dir, filename)

                if os.path.exists(save_path):
                    base, extension = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(save_path):
                        filename = f"{base}_{counter}{extension}"
                        save_path = os.path.join(images_dir, filename)
                        counter += 1

                try:
                    image_file.save(save_path)
                    image_urls.append(f'images/{filename}')  
                except Exception:
                    flash('Error saving image, try again.', 'error')

        if image_urls:
            image_url = ', '.join(image_urls)  
        else:
            image_url = None  

        new_item = Item(name=item_name, image_url=image_url)
        db.session.add(new_item)

        try:
            db.session.commit()
            logging.info("Item added to the database.")  
        except Exception as e:
            logging.error("Error committing to database:", e)
            db.session.rollback()  

        flash('Item added!')
        return redirect(url_for('main.item_page'))

    return render_template('add_item.html')

@main.route('/items/<int:item_id>/view', methods=['GET'])
def view_item(item_id):
    item = Item.query.get_or_404(item_id)
    if not item.image_url:
        flash("No images for this Item !")
    return render_template('view_item.html', item=item)