import sqlite3
import os

# Save the DB in the root folder (one level above backend)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "lockedin.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT DEFAULT 'Guest Developer',
            total_points INTEGER DEFAULT 0,
            rank TEXT DEFAULT 'Code Initiate'
        )
    ''')
    # Create Sessions History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            max_level INTEGER,
            violations INTEGER,
            syntax_errors INTEGER,
            logic_errors INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Initialize a default user if database is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username) VALUES ('Guest Developer')")
    
    conn.commit()
    conn.close()

def save_session(max_level, violations, syntax, logic):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Calculate EXP: 100 points per level, minus 10 points per violation
    points = max(0, (max_level * 100) - (violations * 10))
    
    cursor.execute('''INSERT INTO sessions 
                      (user_id, max_level, violations, syntax_errors, logic_errors) 
                      VALUES (1, ?, ?, ?, ?)''', (max_level, violations, syntax, logic))
    
    cursor.execute("UPDATE users SET total_points = total_points + ? WHERE id = 1", (points,))
    
    # Ranking System
    cursor.execute("SELECT total_points FROM users WHERE id = 1")
    total = cursor.fetchone()[0]
    new_rank = "Code Initiate"
    if total > 10000: new_rank = "7-Star Architect"
    elif total > 5000: new_rank = "Logic Master"
    elif total > 2000: new_rank = "Senior Scripter"
    elif total > 500: new_rank = "Syntax Soldier"
    
    cursor.execute("UPDATE users SET rank = ? WHERE id = 1", (new_rank,))
    conn.commit()
    conn.close()

def get_profile():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = 1")
    user = dict(cursor.fetchone())
    
    # Fetch recent history
    cursor.execute("SELECT * FROM sessions ORDER BY timestamp DESC LIMIT 20")
    history = [dict(row) for row in cursor.fetchall()]
    
    # Count total sessions
    cursor.execute("SELECT COUNT(*) FROM sessions")
    total_sessions = cursor.fetchone()[0]
    
    conn.close()
    return {"user": user, "history": history, "total_sessions": total_sessions}