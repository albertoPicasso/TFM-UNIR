import sqlite3

def get_programs():
    """Get list of all programs from the database"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM programs")
    programs = cursor.fetchall()
    conn.close()
    return programs

def get_courses_by_program(program_id):
    """Get list of courses for a specific program"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM courses WHERE program_id = ?", (program_id,))
    courses = cursor.fetchall()
    conn.close()
    return courses

def get_subjects_by_course(course_id):
    """Get list of subjects (categories) for a specific course"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories WHERE course_id = ?", (course_id,))
    subjects = cursor.fetchall()
    conn.close()
    return subjects