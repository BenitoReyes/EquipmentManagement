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
        phone INTEGER,
        email TEXT,
        shako_num INTEGER,
        hanger_num INTEGER,
        garment_bag TEXT,
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
    conn, cursor = connect_db()
    cursor.execute('''
        INSERT INTO students (student_id, first_name, last_name, section, phone, email,
                              shako_num, hanger_num, garment_bag, coat_num, pants_num,
                              spats_size, gloves_size, guardian_name, guardian_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        student_id, first_name, last_name, section, phone, email,
        shako_num if shako_num not in ("", None) else None,
        hanger_num if hanger_num not in ("", None) else None,
        garment_bag if garment_bag not in ("", None) else None,
        coat_num if coat_num not in ("", None) else None,
        pants_num if pants_num not in ("", None) else None,
        spats_size, gloves_size, guardian_name, guardian_phone
    ))
    # If any uniform field is filled, add to uniforms table as "not returned"
    if any(x not in ("", None) for x in [shako_num, hanger_num, garment_bag, coat_num, pants_num]):
        cursor.execute('''
            INSERT INTO uniforms (student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num, is_checked_in)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        ''', (
            student_id,
            shako_num if shako_num not in ("", None) else None,
            hanger_num if hanger_num not in ("", None) else None,
            garment_bag if garment_bag not in ("", None) else None,
            coat_num if coat_num not in ("", None) else None,
            pants_num if pants_num not in ("", None) else None
        ))
    conn.commit()
    conn.close()

def get_students():
    """Fetch all student records."""
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return students

def get_students_with_uniforms():
    """Fetch all students and their latest assigned uniform (if any)."""
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT s.student_id, s.first_name, s.last_name, s.section, s.phone, s.email,
               COALESCE(u.shako_num, s.shako_num) as shako_num,
               COALESCE(u.hanger_num, s.hanger_num) as hanger_num,
               COALESCE(u.garment_bag, s.garment_bag) as garment_bag,
               COALESCE(u.coat_num, s.coat_num) as coat_num,
               COALESCE(u.pants_num, s.pants_num) as pants_num,
               s.spats_size, s.gloves_size, s.guardian_name, s.guardian_phone
        FROM students s
        LEFT JOIN (
            SELECT uu.student_id, uu.shako_num, uu.hanger_num, uu.garment_bag, uu.coat_num, uu.pants_num
            FROM uniforms uu
            WHERE uu.is_checked_in = 0
              AND uu.id = (
                  SELECT MAX(id) FROM uniforms
                  WHERE student_id = uu.student_id AND is_checked_in = 0
              )
        ) u ON s.student_id = u.student_id
    ''')
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

def get_student_by_name(first_name, last_name):
    """Retrieve a single student's details by name."""
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM students WHERE first_name = ? AND last_name = ?", (first_name, last_name))
    student = cursor.fetchone()
    conn.close()
    return student

def update_student(student_id, field, new_value):
    """Update a student's record safely."""
    conn, cursor = connect_db()

    valid_fields = {
        "first_name", "last_name", "section", "phone", "email",
        "shako_num", "hanger_num", "garment_bag", "coat_num", "pants_num",
        "spats_size", "gloves_size", "guardian_name", "guardian_phone"
    }

    # Ensure field is valid before running query
    if field not in valid_fields:
        print(f"Error: Invalid field '{field}'")
        return

    query = f"UPDATE students SET {field} = ? WHERE student_id = ?"
    cursor.execute(query, (new_value, student_id))

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

def create_uniform_table():
    conn, cursor = connect_db()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uniforms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            shako_num INTEGER,
            hanger_num INTEGER,
            garment_bag TEXT,
            coat_num INTEGER,
            pants_num INTEGER,
            is_checked_in BOOLEAN DEFAULT 0,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
    ''')
    conn.commit()
    conn.close()

def assign_uniform(student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num):
    conn, cursor = connect_db()
    cursor.execute('''
        INSERT INTO uniforms (student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num, is_checked_in)
        VALUES (?, ?, ?, ?, ?, ?, 0)
    ''', (student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num))
    conn.commit()
    conn.close()

def return_uniform(student_id):
    conn, cursor = connect_db()
    cursor.execute('''
        UPDATE uniforms SET is_checked_in = 1
        WHERE student_id = ? AND is_checked_in = 0
    ''', (student_id,))
    conn.commit()
    conn.close()

def get_students_with_outstanding_uniforms():
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT s.first_name, s.last_name, u.shako_num, u.hanger_num, u.garment_bag, u.coat_num, u.pants_num
        FROM students s
        JOIN uniforms u ON s.student_id = u.student_id
        WHERE u.is_checked_in = 0
    ''')
    results = cursor.fetchall()
    conn.close()
    return results

from db import create_tables, create_uniform_table


create_tables()
create_uniform_table()  # Ensure the tables exist before running the app
