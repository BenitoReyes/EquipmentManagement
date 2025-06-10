import sqlite3

DB_NAME = "C:/Users/benny/Documents/GitHub/EquipmentManagement/database/students.db"

def connect_db():
    """Establish connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    return conn, cursor
def create_tables():
    """Create the students table with student_id as the primary key."""
    conn, cursor = connect_db()

    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,  -- Now Student ID is the unique identifier
        first_name TEXT,
        last_name TEXT,
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

def add_student(student_id, first_name, last_name, section, phone, email, shako_num, hanger_num,
                garment_bag, coat_num, pants_num, spats_size, gloves_size, guardian_name, guardian_phone):
    """Insert a new student record, ensuring the ID is unique."""
    conn, cursor = connect_db()

    try:
        cursor.execute(
            "INSERT INTO students (student_id, first_name, last_name, section, phone, email, shako_num, hanger_num, garment_bag, coat_num, pants_num, spats_size, gloves_size, guardian_name, guardian_phone) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (student_id, first_name, last_name, section, phone, email, shako_num, hanger_num, garment_bag, coat_num,
             pants_num, spats_size, gloves_size, guardian_name, guardian_phone))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Error: Student ID {student_id} already exists!")
    finally:
        conn.close()

def get_students():
    """Fetch all student records."""
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return students

def get_student_by_id(student_id):
    """Retrieve a single student's details by ID."""
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()
    conn.close()
    return student

def update_student(student_id, field, new_value):
    """Update a student's record only if they exist."""
    conn, cursor = connect_db()

    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    if cursor.fetchone() is None:
        print("Error: Student ID not found.")
        return

    cursor.execute(f"UPDATE students SET {field} = ? WHERE student_id = ?", (new_value, student_id))
    conn.commit()
    conn.close()



def delete_student(student_id):
    """Delete a student only if they exist."""
    conn, cursor = connect_db()

    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    if cursor.fetchone() is None:
        print("Error: Student ID not found.")
        return

    cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()

from db import create_tables

create_tables()  # Ensure the tables exist before running the app
