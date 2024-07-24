import sqlite3

import numpy as np
import pandas as pd

# Initialize SQLite database
conn = sqlite3.connect('flaskblog.db')
# Create a cursor object using the connection
cursor = conn.cursor()
# Create a table 'employees' if it does not exist

df = pd.read_csv('Data/Uncleaned_employees_final_dataset (1).csv')
print(df.columns)
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
df.drop(columns=['gender',  'age', 'education', 'recruitment_channel'] ,inplace=True)
df = df[:15]


cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        employee_id INTEGER,
        department TEXT,
        region TEXT,
        previous_year_rating INTEGER,
        length_of_service INTEGER,
        no_of_trainings INTEGER,
        KPIs_met_more_than_80 INTEGER,
        awards_won INTEGER,
        avg_training_score INTEGER,
        performance_score INTEGER
    )
''')
# Insert data into the 'employees' table from the CSV file
for index, row in df.iterrows():
    cursor.execute('''
        INSERT INTO employees (employee_id, department, region, previous_year_rating, length_of_service, 
                               no_of_trainings, KPIs_met_more_than_80, awards_won, avg_training_score, 
                               performance_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (row['employee_id'], row['department'], row['region'], row['previous_year_rating'],
          row['length_of_service'], row['no_of_trainings'], row['KPIs_met_more_than_80'],
          row['awards_won'], row['avg_training_score'], row['performance_score']))

# Commit changes to the database

conn.commit()
# lets check the data in the database
cursor.execute('SELECT * FROM employees')
# Fetch all results
results = cursor.fetchall()
print(results)
conn.commit()
# Close the cursor and connection
cursor.close()
conn.close()
