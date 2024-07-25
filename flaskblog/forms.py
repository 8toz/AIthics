from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.widgets import CheckboxInput


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class GoalPlanningForm(FlaskForm):
    projects = [
    {'id': 1, 'name': 'Project A'},
    {'id': 2, 'name': 'Project B'},
    {'id': 3, 'name': 'Project C'},
    ]

    courses = [
    {'id': 1, 'name': 'Course X'},
    {'id': 2, 'name': 'Course Y'},
    {'id': 3, 'name': 'Course Z'},
    ]

    project_choices = [(str(project['id']), project['name']) for project in projects]
    course_choices = [(str(course['id']), course['name']) for course in courses]

    projects = SelectMultipleField('Select Projects', choices=project_choices, option_widget=CheckboxInput(), widget=CheckboxInput())
    courses = SelectMultipleField('Select Courses', choices=course_choices, option_widget=CheckboxInput(), widget=CheckboxInput())
    goal_text = StringField('Goal Text')
    submit = SubmitField('Submit')
