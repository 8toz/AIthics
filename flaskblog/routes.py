from flask import Flask, render_template, url_for, flash, redirect, request, jsonify, g
import sqlite3
from flaskblog import app
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import base64
from math import ceil

# This would ideally be stored in a database. For this example, we'll use a global variable.
notifications = []

# Function to establish SQLite database connection
def get_db_connection():
    conn = sqlite3.connect('flaskblog.db')
    conn.row_factory = sqlite3.Row  # Access rows as dictionaries
    return conn

# Close database connection when context is popped
@app.teardown_appcontext
def close_connection(exception=None):
    conn = getattr(g, '_database', None)
    if conn is not None:
        conn.close()

# Function to generate team plots using Plotly
def generate_team_plots():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch top 3 departments based on performance score
    cursor.execute('SELECT department, AVG(performance_score) AS avg_performance FROM employees GROUP BY department ORDER BY avg_performance DESC LIMIT 3')
    top_3_departments = cursor.fetchall()

    plots = []
    for dept, avg_performance in top_3_departments:
        # Fetch team data for the department
        cursor.execute('SELECT performance_score FROM employees WHERE department=?', (dept,))
        print(cursor.fetchall())
        team_data = cursor.fetchall()

        # Check if team_data is empty or None
        if team_data:
            # Extract performance scores
            performance_scores = [data['performance_score'] for data in team_data if data['performance_score'] is not None]

            if performance_scores:
                # Create a Plotly histogram figure
                fig = go.Figure(data=[go.Histogram(x=performance_scores, nbinsx=10)])
                fig.update_layout(
                    title=f'{dept} Team Performance Distribution',
                    xaxis_title='Performance Score',
                    yaxis_title='Number of Employees'
                )

                # Convert Plotly figure to JSON to embed in HTML
                plot_json = fig.to_json()

                plots.append({
                    'team': dept,
                    'plot': plot_json
                })
        else:
            app.logger.warning(f"No performance scores found for department: {dept}")

    cursor.close()
    conn.close()

    return plots

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route('/manager_dashboard')
def manager_dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of employees per page

    start = (page - 1) * per_page
    end = start + per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch employees from SQLite database
    cursor.execute('SELECT * FROM employees')
    employees = cursor.fetchall()

    total_employees = len(employees)
    total_pages = ceil(total_employees / per_page)

    page_range_start = max(1, page - 2)
    page_range_end = min(total_pages, page + 2)
    page_range = list(range(page_range_start, page_range_end + 1))

    employees = employees[start:end]  # Limit to current page

    team_plots = generate_team_plots()

    recent_updates = [
        {'author': 'Team Lead', 'author_avatar': 'sumit.jpeg', 'date_posted': '2024-07-24',
         'content': 'Project X milestone achieved!'},
        # Add more updates...
    ]

    cursor.close()
    conn.close()

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
    return render_template('employee_dashboard.html', title='Employee Dashboard', employee=employee, recent_updates=recent_updates, upcoming_tasks=upcoming_tasks)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

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
def generate_employee_plots(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch employee data
    cursor.execute('SELECT * FROM employees WHERE id=?', (employee_id,))
    employee_data = cursor.fetchone()

    if not employee_data:
        flash(f'Employee with ID {employee_id} not found', 'danger')
        return None

    # Fetch performance scores
    performance_scores = [employee_data['performance_score']]

    # Create a Plotly bar chart figure
    fig = go.Figure(data=[go.Bar(x=['Performance Score'], y=performance_scores)])
    fig.update_layout(
        title=f'Performance Scores for Employee ID: {employee_id}',
        xaxis_title='Performance Score',
        yaxis_title='Score Value'
    )

    # Convert Plotly figure to JSON to embed in HTML
    plot_json = fig.to_json()

    cursor.close()
    conn.close()

    return plot_json
@app.route('/get_insights/<int:employee_id>')
def get_insights(employee_id):
    # Generate plots for the employee
    employee_plots = generate_employee_plots(employee_id)

    if not employee_plots:
        # Handle case where employee data or plots couldn't be generated
        flash(f'Unable to generate insights for Employee ID {employee_id}', 'danger')
        return redirect(url_for('manager_dashboard'))

    return render_template('insights.html', title='Employee Insights', employee_id=employee_id, employee_plots=employee_plots)

@app.route('/get_notifications')
def get_notifications():
    return jsonify(notifications)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'manager@infosys.com' and form.password.data == '1234':
            flash('Hi boss! How are you feeling today', 'success')
            return redirect(url_for('manager_dashboard'))
        elif form.email.data == 'employee@infosys.com' and form.password.data == '1234':
            return redirect(url_for('employee_dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)
