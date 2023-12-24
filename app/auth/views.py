from flask import (render_template, redirect, url_for,
                  flash, request, abort, jsonify)
from flask_login import login_user, logout_user, login_required
from . import auth
from ..models import User
from .forms import RegistrationForm, LoginForm
from .. import db
# from ..email import mail_message


@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    role_id = data.get('role_id')

    if not email or not username or not password or not role_id:
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    if role_id not in [1, 2]:
        return jsonify({'error': 'Invalid role id'}), 400
    
    user = User(email=email, username=username, password=password, role_id=role_id)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Registration successful'}), 201

@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    user = User.query.filter_by(email=email).first()

    if user is not None and user.verify_password(password):
        login_user(user)
        return jsonify({'message': 'Login successful'}), 200

    return jsonify({'error': 'Invalid email or password'}), 401

@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200