from flask import Flask, render_template, url_for, flash, redirect, request, jsonify, g
import sqlite3
from flaskblog import app
from flaskblog.forms import RegistrationForm, LoginForm, GoalPlanningForm
from flaskblog.models import User, Post
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import base64
from math import ceil
from flaskblog.forms import GoalPlanningForm

from flaskblog import recomendation_employee
from ollama import Client

CURRENT_USER_ROLE = None
# This would ideally be stored in a database. For this example, we'll use a global variable.
notifications = []

# Function to establish SQLite database connection
def get_db_connection():
    conn = sqlite3.connect(r'C:\Users\hussin.TRN\Desktop\ai_for_infosys_hr\AIthics\flaskblog.db')
    conn.row_factory = sqlite3.Row  # Access rows as dictionaries
    return conn


def get_pending_recommendations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recommendations WHERE status = 'Pending' ORDER BY timestamp DESC")
    recommendations = cursor.fetchall()
    conn.close()
    return recommendations


def get_employee_recommendations(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recommendations WHERE employee_id = ? AND status = 'Approved' ORDER BY timestamp DESC LIMIT 5", (employee_id,))
    nudges = cursor.fetchall()
    conn.close()
    return nudges




@app.route('/view_recommendation/<int:recommendation_id>', methods=['GET', 'POST'])
def view_recommendation(recommendation_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recommendations WHERE id = ?", (recommendation_id,))
    recommendation = cursor.fetchone()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'approve':
            cursor.execute("UPDATE recommendations SET status = 'Approved' WHERE id = ?", (recommendation_id,))
            flash('Recommendation approved successfully', 'success')
        elif action == 'reject':
            cursor.execute("UPDATE recommendations SET status = 'Rejected' WHERE id = ?", (recommendation_id,))
            flash('Recommendation rejected. A new recommendation will be generated.', 'info')

            # Regenerate recommendation
            new_recommendation = recomendation_employee.handle_new_goal(
                recommendation['employee_id'],
                recommendation['new_goal'],
                recommendation['current_performance_score'],
                recommendation['current_project']
            )

            cursor.execute('''
                INSERT INTO recommendations (employee_id, recommendation, current_project, current_performance_score, new_goal, status)
                VALUES (?, ?, ?, ?, ?, 'Pending')
            ''', (recommendation['employee_id'], new_recommendation, recommendation['current_project'],
                  recommendation['current_performance_score'], recommendation['new_goal']))

            new_recommendation_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return redirect(url_for('view_recommendation', recommendation_id=new_recommendation_id))

        conn.commit()
        return redirect(url_for('manager_dashboard'))

    conn.close()
    return render_template('view_recommendation.html', recommendation=recommendation)

# Close database connection when context is popped
@app.teardown_appcontext
def close_connection(exception=None):
    conn = getattr(g, '_database', None)
    if conn is not None:
        conn.close()


def get_old_recommendations(employee_id):
    database = sqlite3.connect(r'C:\Users\hussin.TRN\Desktop\ai_for_infosys_hr\AIthics\flaskblog.db')
    cursor = database.cursor()

    # Calculate the date one month ago from today or older
    one_month_ago = datetime.now() - timedelta(days=30)


    # Query recommendations older than one month
    cursor.execute('''
        SELECT * FROM recommendations 
        WHERE employee_id = ?
    ''', (employee_id,))

    old_recommendations = cursor.fetchall()
    print(old_recommendations)
    cursor.close()
    database.close()

    return old_recommendations
# Function to generate team plots using Plotly

# Function to generate nudges and store them in the database
def generate_nudges(employee_id, recommendations):
    client = Client(host='http://localhost:11434')

    for recommendation in recommendations:
        new_goal = recommendation[4]  # Assuming 'new_goal' is at index 4 in the recommendation tuple
        prompt = f"Generate a nudge for employee {employee_id} on goal {new_goal}"

        try:
            response = client.generate(model='nudges_model:latest', prompt=prompt)
            nudge = response['response']
            print(f"Nudge generated for recommendation: {recommendation}. Nudge: {nudge}")
            store_nudges(employee_id, nudge)  # Store nudge in the database
        except Exception as e:
            print(f"Error generating nudge for recommendation: {recommendation}. Error: {e}")


# Function to store nudges in the database
def store_nudges(employee_id, nudge):
    database = sqlite3.connect(r'C:\Users\hussin.TRN\Desktop\ai_for_infosys_hr\AIthics\flaskblog.db')
    cursor = database.cursor()
    cursor.execute('''
        INSERT INTO nudges (employee_id, nudge, time)
        VALUES (?, ?, ?)
    ''', (employee_id, nudge, datetime.now()))
    database.commit()
    print(f"Nudge stored for Employee ID {employee_id}")
    cursor.close()
    database.close()


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

    pending_recommendations = get_pending_recommendations()

    return render_template('manager_dashboard.html',
                           title='Manager Dashboard',
                           employees=employees,
                           recent_updates=recent_updates,
                           page=page,
                           total_pages=total_pages,
                           page_range=page_range,
                           team_plots=team_plots,
                           pending_recommendations=pending_recommendations)




def get_nudges(employee_id):
    database = sqlite3.connect(r'C:\Users\hussin.TRN\Desktop\ai_for_infosys_hr\AIthics\flaskblog.db')
    cursor = database.cursor()

    # Fetch nudges for the specific employee
    cursor.execute('''
        SELECT * FROM nudges WHERE employee_id = ?
    ''', (employee_id,))

    nudges = cursor.fetchall()
    cursor.close()
    database.close()

    return nudges

@app.route('/employee_dashboard')
def employee_dashboard():
    employee_id = 74430  # Replace with actual employee ID retrieval logic

    # Fetch recommendations (older than one month)
    recommendations = get_old_recommendations(employee_id)

    # Generate nudges based on recommendations
    # generate_nudges(employee_id, recommendations)

    # Fetch nudges for the employee
    nudges = get_nudges(employee_id)

    # Example data for other sections
    employee = {
        'name': 'Jane Doe',
        'position': 'Software Developer',
        'department': 'IT',
        'email': 'jane.doe@example.com',
        'status': 'Active'
    }
    recent_updates = [
        {'author': 'HR Team', 'author_avatar': 'path_to_avatar.jpg', 'date_posted': '2024-07-24',
         'title': 'New Policy Update', 'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'},
        # More recent updates as needed
    ]
    slides = [
        {'image': '/static/slide1.jpg', 'title': 'Slide 1'},
        {'image': '/static/slide2.jpg', 'title': 'Slide 2'},
        # More slides as needed
    ]

    return render_template('employee_dashboard.html',
                           title='Employee Dashboard',
                           employee=employee,
                           recommendations=recommendations,
                           nudges=nudges,
                           recent_updates=recent_updates,
                           slides=slides)



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

@app.route("/notification")
def notification():

    return render_template('notification.html')

@app.route("/home2")
def home2():
    return render_template('home2.html')

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
@app.route("/huss_goals")
def huss_goals():

    return render_template('huss_goals.html')


@app.route('/plan_goals', methods=['GET', 'POST'])
def plan_goals():
    form = GoalPlanningForm()

    if request.method == 'GET':
        conn = sqlite3.connect(r'C:\Users\hussin.TRN\Desktop\ai_for_infosys_hr\AIthics\flaskblog.db')
        cursor = conn.cursor()
        cursor.execute('SELECT project FROM projects WHERE employee_id = 74430')
        projects_data = cursor.fetchall()
        projects = [(project[0], project[0]) for project in projects_data]

        form.select_project.choices = projects

    if form.validate_on_submit():
        goal_text = form.goal_text.data
        selected_project = form.select_project.data
        # lets remove the [ ] from the selected project
        selected_project = selected_project[1:-1]

        # Get employee performance score
        employee_id = 74430  # Replace with actual employee ID
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT performance_score FROM employees WHERE employee_id = ?', (employee_id,))
        result = cursor.fetchone()

        if result is None:
            flash(f'No performance score found for Employee ID {employee_id}', 'danger')
            conn.close()
            return redirect(url_for('plan_goals'))

        performance_score = result[0]
        print(performance_score)
        conn.close()

        # Generate recommendation
        recommendation = recomendation_employee.handle_new_goal(employee_id, goal_text, performance_score, selected_project)
        print(recommendation)
        # Store recommendation
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO recommendations (employee_id, recommendation, current_project, current_performance_score, new_goal, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (employee_id, recommendation,'project2', performance_score, goal_text, datetime.now(), 'Pending'))

        conn.commit()
        conn.close()

        flash('Goal set and recommendation generated successfully!', 'success')
        return redirect(url_for('plan_goals'))

    return render_template('plan_goals.html', title='Plan Goals', form=form)



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
        global CURRENT_USER_ROLE
        if form.email.data == 'manager@infosys.com' and form.password.data == '1234':
            CURRENT_USER_ROLE = 'manager'
            flash('Hi boss! How are you feeling today', 'success')
            return redirect(url_for('manager_dashboard'))
        elif form.email.data == 'employee@infosys.com' and form.password.data == '1234':
            CURRENT_USER_ROLE = 'employee'
            return redirect(url_for('employee_dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)
