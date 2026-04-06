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
    
    # Safely upgrade existing database tables without deleting the file
    try:
        cursor.execute("ALTER TABLE sessions ADD COLUMN violation_logs TEXT DEFAULT '[]'")
    except sqlite3.OperationalError:
        pass # Column already exists
        
    try:
        cursor.execute("ALTER TABLE sessions ADD COLUMN level_times TEXT DEFAULT '[]'")
    except sqlite3.OperationalError:
        pass # Column already exists
        
    try:
        cursor.execute("ALTER TABLE sessions ADD COLUMN categories_completed TEXT DEFAULT '[]'")
    except sqlite3.OperationalError:
        pass # Column already exists
        
    try:
        cursor.execute("ALTER TABLE sessions ADD COLUMN aptitude_score INTEGER DEFAULT NULL")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE sessions ADD COLUMN behavioral_feedback TEXT DEFAULT NULL")
    except sqlite3.OperationalError:
        pass

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aptitude_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            category TEXT
        )
    ''')
    
    # Ensure we have a large pool of questions
    cursor.execute("SELECT COUNT(*) FROM aptitude_questions")
    if cursor.fetchone()[0] < 40:
        cursor.execute("DELETE FROM aptitude_questions") # Clear old questions
        sample_q = [
            ("What is the time complexity of binary search?", "O(1)", "O(n)", "O(log n)", "O(n log n)", "O(log n)", "Algorithms"),
            ("Which data structure uses LIFO?", "Queue", "Stack", "Tree", "Graph", "Stack", "Data Structures"),
            ("What does TCP stand for?", "Transmission Control Protocol", "Transfer Control Protocol", "Transport Control Protocol", "Transmission Command Protocol", "Transmission Control Protocol", "Networking"),
            ("What is a deadlock?", "A network failure", "Two threads blocking each other", "A memory leak", "An infinite loop", "Two threads blocking each other", "OS"),
            ("In SQL, which command is used to remove a table?", "DELETE", "DROP", "TRUNCATE", "REMOVE", "DROP", "Databases"),
            ("What is the main advantage of a hash table?", "Ordered data", "O(1) average lookup", "Low memory usage", "Thread safety", "O(1) average lookup", "Data Structures"),
            ("Which sorting algorithm has the worst-case complexity of O(n^2)?", "Merge Sort", "Heap Sort", "Quick Sort", "Radix Sort", "Quick Sort", "Algorithms"),
            ("What is a race condition?", "Two processes competing for resources", "A fast execution path", "A syntax error", "A type of deadlock", "Two processes competing for resources", "OS"),
            ("What HTTP status code represents 'Not Found'?", "400", "401", "403", "404", "404", "Web"),
            ("Which paradigm does React primarily use?", "Object-Oriented", "Functional/Declarative", "Procedural", "Event-Driven", "Functional/Declarative", "Web"),
            ("What is the space complexity of Depth First Search (DFS) on a graph?", "O(1)", "O(V)", "O(E)", "O(V+E)", "O(V)", "Algorithms"),
            ("In REST, which method is typically used to update an existing resource completely?", "GET", "POST", "PUT", "PATCH", "PUT", "Web"),
            ("What does AC ACID stand for in databases?", "Atomicity, Consistency", "Accuracy, Completeness", "Allocation, Concurrency", "Addition, Calculation", "Atomicity, Consistency", "Databases"),
            ("Which layer of the OSI model does HTTP operate on?", "Transport", "Network", "Application", "Presentation", "Application", "Networking"),
            ("What is a primary key?", "A key used for encryption", "A unique identifier for a database record", "The first column in a table", "A foreign key reference", "A unique identifier for a database record", "Databases"),
            ("Which algorithm is used to find the shortest path in a weighted graph?", "DFS", "BFS", "Dijkstra's", "Kruskal's", "Dijkstra's", "Algorithms"),
            ("What is virtual memory?", "Cloud storage", "RAM installed on the motherboard", "Disk space acting as RAM", "Cache memory", "Disk space acting as RAM", "OS"),
            ("In Git, what command saves your staged changes to the local repository?", "git push", "git save", "git commit", "git add", "git commit", "Tools"),
            ("What is polymorphism in OOP?", "Hiding data", "Functions taking multiple forms", "Creating new classes", "Binding data and methods", "Functions taking multiple forms", "OOP"),
            ("Which port is standard for HTTPS?", "80", "443", "22", "21", "443", "Networking"),
            ("What is a zombie process?", "A process that consumes all RAM", "A process that has completed but still has an entry in the process table", "A virus", "A process waiting for I/O", "A process that has completed but still has an entry in the process table", "OS"),
            ("What is the time complexity to insert at the end of a dynamic array?", "O(1) amortized", "O(n)", "O(log n)", "O(n^2)", "O(1) amortized", "Data Structures"),
            ("What is a closure in JavaScript?", "A function with its lexical environment", "A closed browser tab", "A private variable", "A loop ending condition", "A function with its lexical environment", "Web"),
            ("Which design pattern ensures only one instance of a class exists?", "Factory", "Observer", "Singleton", "Decorator", "Singleton", "Design Patterns"),
            ("What does CSS stand for?", "Cascading Style Sheets", "Creative Style System", "Computer Style Sheets", "Colorful Style System", "Cascading Style Sheets", "Web"),
            ("What is an IP address?", "A physical hardware address", "A unique logical network identifier", "A website domain name", "A routing protocol", "A unique logical network identifier", "Networking"),
            ("Which of these is a NoSQL database?", "PostgreSQL", "MySQL", "MongoDB", "Oracle", "MongoDB", "Databases"),
            ("What does the 'S' in SOLID principles stand for?", "Single Responsibility", "Simple Object", "Static Typing", "Standard Interface", "Single Responsibility", "Design Patterns"),
            ("What is a memory leak?", "RAM physically breaking", "Failing to release allocated memory", "Too many variables", "Data corruption", "Failing to release allocated memory", "OS"),
            ("What is the best case time complexity of Bubble Sort?", "O(n)", "O(n log n)", "O(n^2)", "O(1)", "O(n)", "Algorithms"),
            ("What is Docker primarily used for?", "Editing code", "Containerization", "Version control", "Database management", "Containerization", "Tools"),
            ("Which protocol is used to resolve domain names to IP addresses?", "DHCP", "FTP", "DNS", "SMTP", "DNS", "Networking"),
            ("What is indexing in a database?", "Sorting all rows alphabetically", "Creating a data structure to speed up retrieval", "Deleting old records", "Compressing data", "Creating a data structure to speed up retrieval", "Databases"),
            ("What does JSON stand for?", "Java Standard Output Network", "JavaScript Object Notation", "JavaScript Oriented Node", "Java Syntax Object Notation", "JavaScript Object Notation", "Web"),
            ("What is a thread?", "A physical CPU core", "The smallest sequence of programmed instructions", "A network connection", "A database connection", "The smallest sequence of programmed instructions", "OS"),
            ("Which of the following is NOT a JavaScript framework/library?", "React", "Angular", "Vue", "Django", "Django", "Web"),
            ("What is Big O notation used for?", "Measuring disk space", "Describing algorithm complexity", "Network latency", "Database size", "Describing algorithm complexity", "Algorithms"),
            ("What is a foreign key?", "A key from another database", "A field that links to another table's primary key", "An encrypted key", "A composite key", "A field that links to another table's primary key", "Databases"),
            ("What is CI/CD?", "Continuous Integration / Continuous Deployment", "Code Injection / Code Delivery", "Custom Interface / Custom Design", "Central Intelligence / Central Data", "Continuous Integration / Continuous Deployment", "Tools"),
            ("What is a load balancer?", "A database index", "Distributes network traffic across multiple servers", "A CPU component", "A type of firewall", "Distributes network traffic across multiple servers", "Networking"),
            ("What does API stand for?", "Application Programming Interface", "Advanced Program Integration", "Automated Process Interaction", "Application Process Instance", "Application Programming Interface", "General CS")
        ]
        cursor.executemany("INSERT INTO aptitude_questions (question, option_a, option_b, option_c, option_d, correct_answer, category) VALUES (?, ?, ?, ?, ?, ?, ?)", sample_q)

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

def save_session(user_id, max_level, violations, syntax, logic, violation_logs="[]", level_times="[]", categories="[]", aptitude_score=None, behavioral_feedback=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    points = max(0, (max_level * 100) - (violations * 10))
    if aptitude_score: points += (aptitude_score * 10)

    cursor.execute('''INSERT INTO sessions 
                      (user_id, max_level, violations, syntax_errors, logic_errors, violation_logs, level_times, categories_completed, aptitude_score, behavioral_feedback) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (user_id, max_level, violations, syntax, logic, violation_logs, level_times, categories, aptitude_score, behavioral_feedback))

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

    # Calculate Category Stats for Radar Chart
    import json
    category_stats = {}
    for session in history:
        try:
            cats = json.loads(session.get('categories_completed', '[]'))
            for c in cats:
                category_stats[c] = category_stats.get(c, 0) + 1
        except: pass

    cursor.execute("SELECT COUNT(*) FROM sessions WHERE user_id = ?", (user_id,))
    total_sessions = cursor.fetchone()[0]

    conn.close()
    return {"user": dict(user), "history": history, "total_sessions": total_sessions, "category_stats": category_stats}

def get_random_aptitude_questions(limit=5):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, option_a, option_b, option_c, option_d, category FROM aptitude_questions ORDER BY RANDOM() LIMIT ?", (limit,))
    questions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return questions

def check_aptitude_answers(answers):
    # answers is a dict of {question_id: selected_option}
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    score = 0
    results = []
    
    for q_id, ans in answers.items():
        cursor.execute("SELECT question, correct_answer FROM aptitude_questions WHERE id = ?", (q_id,))
        row = cursor.fetchone()
        if row:
            question_text, correct_ans = row
            is_correct = (correct_ans == ans)
            if is_correct:
                score += 1
            results.append({
                "question_id": q_id,
                "question": question_text,
                "user_answer": ans,
                "correct_answer": correct_ans,
                "is_correct": is_correct
            })
    conn.close()
    return {"score": score, "total": len(answers), "results": results}