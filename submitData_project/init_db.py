import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    data TEXT NOT NULL,
    status TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("Database and table created.")
