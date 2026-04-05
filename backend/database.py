import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "lockedin.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Users table now requires a password hash
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            total_points INTEGER DEFAULT 0,
            rank TEXT DEFAULT 'Code Initiate'
        )
    ''')
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
    conn.commit()
    conn.close()

def create_user(username, password_hash):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False # Username already exists
    conn.close()
    return success

def get_user_by_username(username):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def save_session(user_id, max_level, violations, syntax, logic):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    points = max(0, (max_level * 100) - (violations * 10))
    
    cursor.execute('''INSERT INTO sessions 
                      (user_id, max_level, violations, syntax_errors, logic_errors) 
                      VALUES (?, ?, ?, ?, ?)''', (user_id, max_level, violations, syntax, logic))
    
    cursor.execute("UPDATE users SET total_points = total_points + ? WHERE id = ?", (points, user_id))
    
    cursor.execute("SELECT total_points FROM users WHERE id = ?", (user_id,))
    total = cursor.fetchone()[0]
    new_rank = "Code Initiate"
    if total > 10000: new_rank = "7-Star Architect"
    elif total > 5000: new_rank = "Logic Master"
    elif total > 2000: new_rank = "Senior Scripter"
    elif total > 500: new_rank = "Syntax Soldier"
    
    cursor.execute("UPDATE users SET rank = ? WHERE id = ?", (new_rank, user_id))
    conn.commit()
    conn.close()

def get_profile(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, total_points, rank FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return None
        
    cursor.execute("SELECT * FROM sessions WHERE user_id = ? ORDER BY timestamp DESC LIMIT 20", (user_id,))
    history = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT COUNT(*) FROM sessions WHERE user_id = ?", (user_id,))
    total_sessions = cursor.fetchone()[0]
    
    conn.close()
    return {"user": dict(user), "history": history, "total_sessions": total_sessions}