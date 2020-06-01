import os
from flask import render_template, redirect, Blueprint, session, url_for, flash
from flask_login import login_user, logout_user, login_required

auth = Blueprint('auth', __name__)

from .models import User
from .forms import LoginForm

#---------------------------------------------------------------------------------------------------------------------------------
# Login
#---------------------------------------------------------------------------------------------------------------------------------
@auth.route("/login", methods=["GET","POST"])
def login():

	form = LoginForm()

	if form.validate_on_submit():

		user = User.query.filter_by(username=form.username.data).first()

		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(url_for('main.home'))
		
		flash('Invalid username or password.')

	return render_template('auth/login.html', form=form)

@auth.route('/logout') 
@login_required
def logout():
	logout_user()
	flash('You have been logged out.') 

	return redirect(url_for('main.home'))

