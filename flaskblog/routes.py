from flask import render_template, url_for, flash, redirect, request, jsonify
from flaskblog import app
from flaskblog.forms import RegistrationForm, LoginForm, GoalPlanningForm
from flaskblog.models import User, Post
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from math import ceil


# This would ideally be stored in a database. For this example, we'll use a global variable.
notifications = []

# Read the CSV file
df = pd.read_csv('Data/Uncleaned_employees_final_dataset (1).csv')
def calculate_performance_score(row):
    if row['no_of_trainings'] > 2 and row['previous_year_rating'] > 3:
        return np.random.randint(75, 100)
    else:
        # Calculate a score based on trainings and rating
        base_score = (row['no_of_trainings'] * 10) + (row['previous_year_rating'] * 10)
        # Normalize to a 0-100 scale
        return min(max(base_score, 0), 74)  # Cap at 74 to differentiate from high performers

# Add performance score to the dataframe
df['performance_score'] = df.apply(calculate_performance_score, axis=1)
df = df[:15]

from flask import request

@app.context_processor
def inject_request():
    return dict(request=request)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/home2")
def home2():
    return render_template('home2.html')


@app.route('/slider')
def slider():
    # Dummy data for the slider
    slides = [
        {"image": "https://via.placeholder.com/300x200?text=Slide+1", "title": "Slide 1", "description": "Description for Slide 1"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+2", "title": "Slide 2", "description": "Description for Slide 2"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+3", "title": "Slide 3", "description": "Description for Slide 3"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+4", "title": "Slide 4", "description": "Description for Slide 4"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+5", "title": "Slide 5", "description": "Description for Slide 5"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+6", "title": "Slide 6", "description": "Description for Slide 6"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+7", "title": "Slide 7", "description": "Description for Slide 7"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+8", "title": "Slide 8", "description": "Description for Slide 8"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+9", "title": "Slide 9", "description": "Description for Slide 9"},
    ]
    return render_template('slider.html', slides=slides)


def generate_team_plots():
    # For this example, we'll consider 'department' as teams
    top_3_departments = df['department'].value_counts().nlargest(3).index

    plots = []
    for dept in top_3_departments:
        team_data = df[df['department'] == dept]

        # Generate plot
        plt.figure(figsize=(8, 6))
        plt.hist(team_data['performance_score'], bins=10, edgecolor='black')
        plt.title(f'{dept} Team Performance Distribution')
        plt.xlabel('Performance Score')
        plt.ylabel('Number of Employees')

        # Save plot to a base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        plots.append({
            'team': dept,
            'plot': plot_data
        })

    return plots


@app.route('/manager_dashboard')
def manager_dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of employees per page

    # Calculate the start and end indices for the current page
    start = (page - 1) * per_page
    end = start + per_page

    # Get the total number of employees
    total_employees = len(df)

    # Calculate the total number of pages
    total_pages = ceil(total_employees / per_page)

    # Calculate the range of pages to display
    page_range_start = max(1, page - 2)
    page_range_end = min(total_pages, page + 2)
    page_range = list(range(page_range_start, page_range_end + 1))

    # Get the employees for the current page
    employees = df.iloc[start:end].to_dict('records')

    # Generate team performance plots
    team_plots = generate_team_plots()

    recent_updates = [
        {'author': 'Team Lead', 'author_avatar': 'sumit.jpeg', 'date_posted': '2024-07-24',
         'content': 'Project X milestone achieved!'},
        # Add more updates...
    ]
    return render_template('manager_dashboard.html',
                           title='Manager Dashboard',
                           employees=employees,
                           recent_updates=recent_updates,
                           page=page,
                           total_pages=total_pages,
                           page_range=page_range,
                           team_plots=team_plots)

@app.route('/employee_dashboard')
def employee_dashboard():
    employee = {
        'name': 'Jane Doe',
        'position': 'Software Developer',
        'department': 'IT',
        'email': 'jane.doe@example.com',
        'status': 'Active'
    }
    recent_updates = [
        {'author': 'HR Team', 'author_avatar': 'path_to_avatar.jpg', 'date_posted': '2024-07-24', 'content': 'Remember to submit your time sheets by Friday!'},
        # Add more updates...
    ]
    upcoming_tasks = [
        {'description': 'Complete project proposal', 'due_date': '2024-07-30'},
        {'description': 'Team meeting', 'due_date': '2024-07-26'},
        # Add more tasks...
    ]
    slides = [
        {"image": "https://via.placeholder.com/300x200?text=Slide+1", "title": "Slide 1", "description": "Description for Slide 1"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+2", "title": "Slide 2", "description": "Description for Slide 2"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+3", "title": "Slide 3", "description": "Description for Slide 3"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+4", "title": "Slide 4", "description": "Description for Slide 4"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+5", "title": "Slide 5", "description": "Description for Slide 5"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+6", "title": "Slide 6", "description": "Description for Slide 6"},
    ]

    return render_template('employee_dashboard.html'
                           , title='Employee Dashboard'
                           , employee=employee
                           , recent_updates=recent_updates
                           , upcoming_tasks=upcoming_tasks
                           , slides=slides)

@app.route('/employee_dashboard2')
def employee_dashboard2():
    employee = {
        'name': 'Jane Doe',
        'position': 'Software Developer',
        'department': 'IT',
        'email': 'jane.doe@example.com',
        'status': 'Active'
    }
    recent_updates = [
        {'author': 'HR Team', 'author_avatar': 'path_to_avatar.jpg', 'date_posted': '2024-07-24', 'content': 'Remember to submit your time sheets by Friday!'},
        # Add more updates...
    ]
    upcoming_tasks = [
        {'description': 'Complete project proposal', 'due_date': '2024-07-30'},
        {'description': 'Team meeting', 'due_date': '2024-07-26'},
        # Add more tasks...
    ]
    slides = [
        {"image": "https://via.placeholder.com/300x200?text=Slide+1", "title": "Slide 1", "description": "Description for Slide 1"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+2", "title": "Slide 2", "description": "Description for Slide 2"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+3", "title": "Slide 3", "description": "Description for Slide 3"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+4", "title": "Slide 4", "description": "Description for Slide 4"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+5", "title": "Slide 5", "description": "Description for Slide 5"},
        {"image": "https://via.placeholder.com/300x200?text=Slide+6", "title": "Slide 6", "description": "Description for Slide 6"},
    ]

    return render_template('employee_dashboard2.html'
                           , title='Employee Dashboard'
                           , employee=employee
                           , recent_updates=recent_updates
                           , upcoming_tasks=upcoming_tasks
                           , slides=slides)

@app.route('/plan-goals', methods=['GET', 'POST'])
def plan_goals():
    form = GoalPlanningForm()

    if form.validate_on_submit():
        selected_projects = form.projects.data
        selected_courses = form.courses.data
        # Process the selected projects and courses as needed
        return render_template('home.html', success=True)

    return render_template('plan_goals.html', form=form)

@app.route("/goal_planning_route")
def goal_planning_route():
    return render_template('goal_planning_route.html', title='About')

@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/notification")
def notification():
    return render_template('notification.html')

@app.route("/logout")
def logout():
    return render_template('home.html')

@app.route("/profile")
def profile():
    return render_template('profile.html', title='Profile')

@app.route("/tasks")
def tasks():
    return render_template('tasks.html', title='Tasks')

@app.route("/performance")
def performance():
    return render_template('performance.html', title='Performance')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/generate_nudge', methods=['POST'])
def generate_nudge():
    data = request.json
    employee = data.get('employee')
    message = f"Nudge generated for {employee}: Great job on your recent project! Keep up the good work!"

    # Add the new notification
    notifications.append({
        'message': message,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    return jsonify({'message': message})


@app.route('/get_notifications')
def get_notifications():
    return jsonify(notifications)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'manager@infosys.com' and form.password.data == '1234':
            return redirect(url_for('manager_dashboard'))
        elif form.email.data == 'employee@infosys.com' and form.password.data == '1234':
            return redirect(url_for('employee_dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/login2", methods=['GET', 'POST'])
def login2():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'manager@infosys.com' and form.password.data == '1234':
            return redirect(url_for('manager_dashboard2'))
        elif form.email.data == 'employee@infosys.com' and form.password.data == '1234':
            return redirect(url_for('employee_dashboard2'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/huss_goals")
def huss_goals():

    return render_template('huss_goals.html')