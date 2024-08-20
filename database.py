import sqlite3

def create_connection():
    conn = sqlite3.connect('school_portal.db')
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            file_path TEXT NOT NULL,
            uploaded_by TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
