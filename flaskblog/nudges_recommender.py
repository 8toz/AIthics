import sqlite3

def make_data_table():
    conn = sqlite3.connect(r'C:\Users\hussin.TRN\Desktop\ai_for_infosys_hr\AIthics\flaskblog.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nudges (
            employee_id INTEGER,
            nudge TEXT,
            time TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def get_nudges():
    conn = sqlite3.connect(r'C:\Users\hussin.TRN\Desktop\ai_for_infosys_hr\AIthics\flaskblog.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM nudges')
    results = cursor.fetchall()

    conn.close()
    return results

if __name__ == "__main__":
    make_data_table()
    nudges = get_nudges()
    print(nudges)