import sqlite3
import hashlib

# Database functions
def setup_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    
    # Create programs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS programs (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    )
    ''')
    
    # Create courses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        program_id INTEGER NOT NULL,
        FOREIGN KEY (program_id) REFERENCES programs(id),
        UNIQUE(name, program_id)
    )
    ''')
    
    # Create categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        course_id INTEGER NOT NULL,
        FOREIGN KEY (course_id) REFERENCES courses(id),
        UNIQUE(name, course_id)
    )
    ''')
    
    # Create documents table for RAG
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        indexed BOOLEAN DEFAULT 0,
        metadata TEXT NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    ''')
    
    # Add default users if needed
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
        student_pass = hashlib.sha256("student123".encode()).hexdigest()
        
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                      ("admin", admin_pass, "admin"))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                      ("student", student_pass, "student"))
    
    # Add default program if not exists
    cursor.execute("SELECT COUNT(*) FROM programs")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO programs (name) VALUES (?)", ("Inteligencia Artificial",))
        program_id = cursor.lastrowid
        
        # Add default course
        cursor.execute("INSERT INTO courses (name, program_id) VALUES (?, ?)", ("PLN", program_id))
        course_id = cursor.lastrowid
        
        # Add default categories
        default_categories = ["Ejercicios", "Examenes", "Información", "Temas"]
        for category in default_categories:
            cursor.execute("INSERT INTO categories (name, course_id) VALUES (?, ?)", 
                         (category, course_id))
    
    conn.commit()
    conn.close()