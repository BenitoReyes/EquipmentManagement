import sqlite3

DB_NAME = "../Database/students.db"

def connect_db():
    """Establish connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    return conn, cursor
def create_tables():
    """Create the students table if it doesn't exist."""
    conn, cursor = connect_db()

    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        student_id TEXT UNIQUE,
        section TEXT,
        phone TEXT,
        email TEXT,
        shako_num INTEGER,
        hanger_num INTEGER,
        garment_bag INTEGER,
        coat_num INTEGER,
        pants_num INTEGER,
        spats_size TEXT,
        gloves_size TEXT,
        guardian_name TEXT,
        guardian_phone TEXT
    )''')

    conn.commit()
    conn.close()


def add_student(first_name, last_name, student_id, section, phone, email, shako_num, hanger_num, garment_bag, coat_num,
                pants_num, spats_size, gloves_size, guardian_name, guardian_phone):
    """Insert a new student record into the database."""
    conn, cursor = connect_db()

    cursor.execute(
        "INSERT INTO students (first_name, last_name, student_id, section, phone, email, shako_num, hanger_num, garment_bag, coat_num, pants_num, spats_size, gloves_size, guardian_name, guardian_phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (first_name, last_name, student_id, section, phone, email, shako_num, hanger_num, garment_bag, coat_num,
         pants_num, spats_size, gloves_size, guardian_name, guardian_phone))

    conn.commit()
    conn.close()

def get_students():
    """Fetch all student records."""
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return students


def update_student(student_id, field, new_value):
    """Update a student's record."""
    conn, cursor = connect_db()

    cursor.execute(f"UPDATE students SET {field} = ? WHERE student_id = ?", (new_value, student_id))

    conn.commit()
    conn.close()


def delete_student(student_id):
    """Delete a student's record."""
    conn, cursor = connect_db()

    cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))

    conn.commit()
    conn.close()

from db import create_tables

create_tables()  # Ensure the tables exist before running the app
