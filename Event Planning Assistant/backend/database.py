import sqlite3

DB_NAME = "event_planner.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS venues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        type TEXT,
        capacity INTEGER,
        location TEXT,
        rating REAL,
        booked_dates TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        event_type TEXT,
        date TEXT,
        guests INTEGER,
        venue_id INTEGER,
        theme TEXT,
        budget REAL,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (venue_id) REFERENCES venues (id)
    )
    """)
    
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_NAME)
