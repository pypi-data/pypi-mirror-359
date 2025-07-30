from flask import Blueprint, render_template, redirect, url_for, session
from flask_login import logout_user


auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template("login.html")

@auth.route('/logout')
def logout():
    logout_user()  # This will log the user out
    session.clear()  # Clear the session to log the user out
    return redirect(url_for('main.home'))  # Redirect to home or another page after logout


@auth.route('/sign-up')
def sign_up():
    return render_template("register.html")
