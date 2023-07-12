from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from models import User



auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')  
        phone = request.form.get('phone')  
        
        
        user = User.query.filter_by(username=username).first()
        email_user = User.query.filter_by(email=email).first()  
        phone_user = User.query.filter_by(phone=phone).first()  
        
        # Check if username, email or phone number is taken
        if user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('auth.register'))
        if email_user:
            flash('An account with this email already exists. Please use a different email.')
            return redirect(url_for('auth.register'))
        if phone_user:
            flash('An account with this phone number already exists. Please use a different phone number.')
            return redirect(url_for('auth.register'))
        
        new_user = User(username=username, email=email, phone=phone)  # Add email and phone to the User constructor
        new_user.set_password(password)  # Set password hash using set_password method
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')  # Render the registration form

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not user.check_password(password):
            flash('Invalid username or password. Please try again.')  # If user doesn't exist or password is wrong, reload the page with a message
            return redirect(url_for('auth.login'))
        
        # if the above check passes, then we know the user has the right credentials
        login_user(user)
        return redirect(url_for('feed'))  # After successful login, redirect to home page

    return render_template('login.html')  # Render the login form


@auth.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

         # validate old password
        if not current_user.check_password(old_password):
            flash('Old password is incorrect')
            return redirect(request.url)

        # check if new password and confirm password are the same
        if new_password != confirm_password:
            flash('Passwords do not match')
            return redirect(request.url)

        # update user's password
        current_user.password_hash = generate_password_hash(new_password, method='sha256')
        db.session.commit()

        flash('Password updated successfully')
        return redirect(url_for('edit_profile'))

    return render_template('reset_password.html')



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))