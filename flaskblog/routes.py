from flask import render_template, url_for, flash, redirect
from flaskblog import app
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route('/manager_dashboard')
def manager_dashboard():
    employees = [
        {'name': 'John Doe', 'position': 'Developer', 'department': 'IT', 'status': 'Active'},
        {'name': 'Jane Smith', 'position': 'Designer', 'department': 'Creative', 'status': 'On Leave'},
        # Add more employees...
    ]
    recent_updates = [
        {'author': 'Team Lead', 'author_avatar': 'sumit.jpeg', 'date_posted': '2024-07-24', 'content': 'Project X milestone achieved!'},
        # Add more updates...
    ]
    return render_template('manager_dashboard.html', title='Manager Dashboard', employees=employees, recent_updates=recent_updates)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'manager@infosys.com' and form.password.data == '1234':
            flash('Hi boss! How are you feeling today', 'success')
            return redirect(url_for('manager_dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)
