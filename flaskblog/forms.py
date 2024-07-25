import sqlite3

from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.widgets import CheckboxInput
from wtforms import SelectMultipleField, StringField, SubmitField, widgets
from wtforms.validators import DataRequired
from wtforms.widgets.core import ListWidget


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


# Define the form class
# Define the GoalPlanningForm class
class GoalPlanningForm(FlaskForm):
    goal_text = StringField('Goal Text', validators=[DataRequired()])
    select_project = SelectMultipleField('Select Project', choices=[], validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(GoalPlanningForm, self).__init__(*args, **kwargs)
        self.set_project_choices()

    def set_project_choices(self):
        conn = sqlite3.connect('flaskblog.db')
        cursor = conn.cursor()
        cursor.execute('SELECT project FROM projects')
        projects_data = cursor.fetchall()
        self.select_project.choices = [(project[0], project[0]) for project in projects_data]
        conn.close()
