import sqlite3
import random

import numpy as np
import pandas as pd

# Initialize SQLite database
conn = sqlite3.connect(r'C:\Users\hussin.TRN\Desktop\ai_for_infosys_hr\AIthics\flaskblog.db')
# Create a cursor object using the connection
cursor = conn.cursor()
# Create a table 'employees' if it does not exist

# df = pd.read_csv('Data/Uncleaned_employees_final_dataset (1).csv')
# print(df.columns)
# def calculate_performance_score(row):
#     if row['no_of_trainings'] > 2 and row['previous_year_rating'] > 3:
#         return np.random.randint(75, 100)
#     else:
#         # Calculate a score based on trainings and rating
#         base_score = (row['no_of_trainings'] * 10) + (row['previous_year_rating'] * 10)
#         # Normalize to a 0-100 scale
#         return min(max(base_score, 0), 74)  # Cap at 74 to differentiate from high performers
#
# # Add performance score to the dataframe
# df['performance_score'] = df.apply(calculate_performance_score, axis=1)
# df.drop(columns=['gender',  'age', 'education', 'recruitment_channel'] ,inplace=True)
# df = df[:15]
#
#
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS employees (
#         id INTEGER PRIMARY KEY,
#         employee_id INTEGER,
#         department TEXT,
#         region TEXT,
#         previous_year_rating INTEGER,
#         length_of_service INTEGER,
#         no_of_trainings INTEGER,
#         KPIs_met_more_than_80 INTEGER,
#         awards_won INTEGER,
#         avg_training_score INTEGER,
#         performance_score INTEGER
#     )
# ''')
# # Insert data into the 'employees' table from the CSV file
# for index, row in df.iterrows():
#     cursor.execute('''
#         INSERT INTO employees (employee_id, department, region, previous_year_rating, length_of_service,
#                                no_of_trainings, KPIs_met_more_than_80, awards_won, avg_training_score,
#                                performance_score)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     ''', (row['employee_id'], row['department'], row['region'], row['previous_year_rating'],
#           row['length_of_service'], row['no_of_trainings'], row['KPIs_met_more_than_80'],
#           row['awards_won'], row['avg_training_score'], row['performance_score']))
#
# # Commit changes to the database
#
# conn.commit()
# # lets check the data in the database
# cursor.execute('SELECT * FROM employees')
# # Fetch all results
# results = cursor.fetchall()
# print(results)
# conn.commit()
# # Close the cursor and connection
# cursor.close()
# conn.close()



# Read the Excel file into a DataFrame
# df = pd.read_csv('Data/coursea_data.csv')
#
# # Print columns to understand the structure
# print(df.columns)
#
# # Create a table 'courses' if it does not exist
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS courses (
#         id INTEGER PRIMARY KEY,
#         course_title TEXT,
#         course_organization TEXT,
#         course_Certificate_type TEXT,
#         course_rating FLOAT,
#         course_difficulty TEXT,
#         course_students_enrolled TEXT
#     )
# ''')
#
# # Insert data into the 'courses' table from the DataFrame
# for index, row in df.iterrows():
#     cursor.execute('''
#         INSERT INTO courses (course_title, course_organization, course_Certificate_type,
#                              course_rating, course_difficulty, course_students_enrolled)
#         VALUES (?, ?, ?, ?, ?, ?)
#     ''', (row['course_title'], row['course_organization'], row['course_Certificate_type'],
#           row['course_rating'], row['course_difficulty'], row['course_students_enrolled']))
#
# # Commit changes to the database
# conn.commit()
#
# # Check the data in the database by selecting all records from 'courses'
# cursor.execute('SELECT * FROM courses')
# results = cursor.fetchall()
# print(results)
#
# # Close cursor and connection
# cursor.close()
# conn.close()


#lets make a project tabel for each employee were we have 6 projects [project1, project2, project3, project4, project5, project6]  we can add project randomly to each employee

# Initialize SQLite database

# Create a cursor object using the connection

# for each employee id we will add a random project the value is 'project1', 'project2', 'project3', 'project4', 'project5', 'project6'

# get the employee ids from the database
# cursor.execute('SELECT employee_id FROM employees')
# employee_ids = cursor.fetchall()
# employee_ids = [employee_id[0] for employee_id in employee_ids]
#
# # Create a table 'projects' if it does not exist
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS projects (
#         id INTEGER PRIMARY KEY,
#         employee_id INTEGER,
#         project TEXT
#     )
# ''')
#
# # Insert data into the 'projects' table from the DataFrame
# for employee_id in employee_ids:
#     cursor.execute('''
#         INSERT INTO projects (employee_id, project)
#         VALUES (?, ?)
#     ''', (employee_id, random.choice(['project1', 'project2', 'project3', 'project4', 'project5', 'project6'])))
#
# # Commit changes to the database
# conn.commit()
#
# # Check the data in the database by selecting all records from 'projects'
# cursor.execute('SELECT * FROM projects')
# results = cursor.fetchall()
# print(results)
#
# # Close cursor and connection
# cursor.close()
# conn.close()
cursor.execute("DROP TABLE IF EXISTS recommendations")
conn.commit()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY,
        employee_id INTEGER,
        current_project TEXT,
        current_performance_score INTEGER,
        new_goal TEXT,
        recommendation VARCHAR(255),
        timestamp TIMESTAMP,
        status TEXT
    )
''')


conn.commit()


print("Table Created")
# lets see the columns in the table
# lets insert a one record in the table
cursor.execute('''
        INSERT INTO recommendations (employee_id, current_project, current_performance_score, new_goal, recommendation, timestamp, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (74430, 'project1', 80, 'project2', 'Employee should work on project2', '2022-06-04 12:00:00', 'idk'))


# Commit changes to the database
conn.commit()

# Check the data in the database by selecting all records from 'projects'
cursor.execute('SELECT * FROM recommendations')
results = cursor.fetchall()

print(results)
conn.commit()
cursor.close()
conn.close()
