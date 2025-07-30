from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user
from AggFin import db, bcrypt
from AggFin.models import User 
from sqlalchemy.exc import IntegrityError

users = Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('users.login'))  # Redirect to login page
        except IntegrityError:
            db.session.rollback()
            flash('Email already exists. Please choose a different one.', 'danger')
    
    return render_template('register.html')
@users.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()  # Get user by email
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)  # Log the user in
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))  # Redirect to home page
        else:
            flash('Login failed. Check your email and password.', 'danger')
    
    return render_template('login.html')

