# ------------------------------------------------------------------------------
# Fetch functions for new uniform components
# ------------------------------------------------------------------------------
def get_all_shakos():
    conn, cursor = connect_db()
    cursor.execute("SELECT id, shako_num, status, student_id, notes FROM shakos ORDER BY shako_num")
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_coats():
    conn, cursor = connect_db()
    cursor.execute("SELECT id, coat_num, hanger_num, status, student_id, notes FROM coats ORDER BY coat_num")
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_pants():
    conn, cursor = connect_db()
    cursor.execute("SELECT id, pants_num, status, student_id, notes FROM pants ORDER BY pants_num")
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_garment_bags():
    conn, cursor = connect_db()
    cursor.execute("SELECT id, bag_num, status, student_id, notes FROM garment_bags ORDER BY bag_num")
    results = cursor.fetchall()
    conn.close()
    return results

def find_shako_by_number(shako_num):
    conn, cursor = connect_db()
    cursor.execute("SELECT id, shako_num, status, student_id, notes FROM shakos WHERE shako_num = ?", (shako_num,))
    res = cursor.fetchone()
    conn.close()
    return res

def find_coat_by_number(coat_num):
    conn, cursor = connect_db()
    cursor.execute("SELECT id, coat_num, hanger_num, status, student_id, notes FROM coats WHERE coat_num = ?", (coat_num,))
    res = cursor.fetchone()
    conn.close()
    return res

def find_pants_by_number(pants_num):
    conn, cursor = connect_db()
    cursor.execute("SELECT id, pants_num, status, student_id, notes FROM pants WHERE pants_num = ?", (pants_num,))
    res = cursor.fetchone()
    conn.close()
    return res

def find_bag_by_number(bag_num):
    conn, cursor = connect_db()
    cursor.execute("SELECT id, bag_num, status, student_id, notes FROM garment_bags WHERE bag_num = ?", (bag_num,))
    res = cursor.fetchone()
    conn.close()
    return res

def find_instrument_by_serial(serial):
    conn, cursor = connect_db()
    cursor.execute("SELECT id, student_id, instrument_name, instrument_serial, instrument_case, status, notes FROM instruments WHERE instrument_serial = ?", (serial,))
    res = cursor.fetchone()
    conn.close()
    return res

def update_instrument_by_id(inst_id, student_id=None, status=None, notes=None, case=None, name=None, model=None, condition=None):
    conn, cursor = connect_db()
    fields = []
    params = []
    # Always update student_id, even if None (set to NULL)
    fields.append("student_id = ?")
    params.append(student_id)
    if status is not None:
        fields.append("status = ?")
        params.append(status)
    if notes is not None:
        fields.append("notes = ?")
        params.append(notes)
    if case is not None:
        fields.append("instrument_case = ?")
        params.append(case)
    if name is not None:
        fields.append("instrument_name = ?")
        params.append(name)
    if model is not None:
        fields.append("model = ?")
        params.append(model)
    if condition is not None:
        fields.append("condition = ?")
        params.append(condition)
    if not fields:
        conn.close()
        return
    params.append(inst_id)
    cursor.execute(f"UPDATE instruments SET {', '.join(fields)} WHERE id = ?", tuple(params))
    conn.commit()
    conn.close()
# ------------------------------------------------------------------------------
# Migration/Initialization for Uniform Component Tables
# ------------------------------------------------------------------------------
def initialize_uniform_components():
    """
    Create all new uniform component tables if they do not exist.
    """
    create_shako_table()
    create_coat_table()
    create_pants_table()
    create_garment_bag_table()
import sqlite3
import sys
import os

def resource_path(relative_path):
    """
    Resolves path to resource whether running from source or PyInstaller bundle.
    If bundled, uses the temporary _MEIPASS directory.
    If not, uses the current working directory.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Use this if you're bundling the DB (not recommended for persistence)
DB_NAME = resource_path("Database/students.db")

# Use this if you're shipping the DB alongside the .exe (recommended)
#DB_NAME = os.path.join(os.path.dirname(sys.executable), "Database", "students.db")
# Establishes a connection to the database and returns both the connection and cursor
def connect_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    return conn, cursor


# ------------------------------------------------------------------------------
# Table creation functions
# ------------------------------------------------------------------------------

def create_student_table():
    """
    Creates the 'students' table if it doesn't exist.
    Adds 'Flags' to the allowed sections.
    """
    conn, cursor = connect_db()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            email TEXT,
            year_came_up TEXT,
            status TEXT CHECK(status IN ('Student','Former','Alumni')),
            guardian_name TEXT,
            guardian_phone TEXT,
            section TEXT CHECK(section IN (
                'Trumpet','Trombone','Euphonium','French Horn','Tuba',
                'Flute','Clarinet','Saxophone','Bassoon','Oboe','Percussion',
                'Flags'
            ))
        )
    ''')
    conn.commit()
    conn.close()

def create_shako_table(): 
    """ 
    Creates the 'shakos' table for individual shako inventory. 
    """ 
    conn, cursor = connect_db() 
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS shakos ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            shako_num INTEGER UNIQUE, 
            status TEXT CHECK(status IN ('Available','Assigned','Maintenance','Retired')) DEFAULT 'Available', 
            student_id TEXT NULL, 
            notes TEXT, 
            FOREIGN KEY(student_id) REFERENCES students(student_id) 
        ) 
    ''') 
    conn.commit() 
    conn.close() 
 
def create_coat_table(): 
    """ 
    Creates the 'coats' table for individual coat inventory. 
    """ 
    conn, cursor = connect_db() 
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS coats ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            coat_num INTEGER UNIQUE, 
            hanger_num INTEGER, 
            status TEXT CHECK(status IN ('Available','Assigned','Maintenance','Retired')) DEFAULT 'Available', 
            student_id TEXT NULL, 
            notes TEXT, 
            FOREIGN KEY(student_id) REFERENCES students(student_id) 
        ) 
    ''') 
    conn.commit() 
    conn.close() 
 
def create_pants_table(): 
    """ 
    Creates the 'pants' table for individual pants inventory. 
    """ 
    conn, cursor = connect_db() 
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS pants ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            pants_num INTEGER UNIQUE, 
            status TEXT CHECK(status IN ('Available','Assigned','Maintenance','Retired')) DEFAULT 'Available', 
            student_id TEXT NULL, 
            notes TEXT, 
            FOREIGN KEY(student_id) REFERENCES students(student_id) 
        ) 
    ''') 
    conn.commit() 
    conn.close() 
 
def create_garment_bag_table(): 
    """ 
    Creates the 'garment_bags' table for individual garment bag inventory. 
    """ 
    conn, cursor = connect_db() 
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS garment_bags ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            bag_num TEXT UNIQUE, 
            status TEXT CHECK(status IN ('Available','Assigned','Maintenance','Retired')) DEFAULT 'Available', 
            student_id TEXT NULL, 
            notes TEXT, 
            FOREIGN KEY(student_id) REFERENCES students(student_id) 
        ) 
    ''') 
    conn.commit() 
    conn.close() 


def create_uniform_table():
    """
    Creates the 'uniforms' table if it doesn't exist.
    Tracks uniforms with optional student assignment.
    """
    conn, cursor = connect_db()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uniforms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NULL,
            shako_num INTEGER,
            hanger_num INTEGER,
            garment_bag TEXT,
            coat_num INTEGER,
            pants_num INTEGER,
            status TEXT CHECK(status IN ('Available','Assigned','Maintenance','Retired')) DEFAULT 'Available',
            is_checked_in BOOLEAN DEFAULT 1,
            notes TEXT,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
    ''')
    conn.commit()
    conn.close()

def add_or_update_student(student_id, first_name, last_name, status, section, phone, email, guardian_name, guardian_phone, year_came_up):
    conn, cursor = connect_db()
    cursor.execute("SELECT 1 FROM students WHERE student_id = ?", (student_id,))
    exists = cursor.fetchone() is not None
    if exists:
        cursor.execute('''
            UPDATE students SET first_name=?, last_name=?, status=?, section=?, phone=?, email=?, guardian_name=?, guardian_phone=?, year_came_up=? WHERE student_id=?
        ''', (first_name, last_name, status, section, phone, email, guardian_name, guardian_phone, year_came_up, student_id))
    else:
        cursor.execute('''
            INSERT INTO students (student_id, first_name, last_name, phone, email, year_came_up, status, guardian_name, guardian_phone, section)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, first_name, last_name, phone, email, year_came_up, status, guardian_name, guardian_phone, section))
    conn.commit()
    conn.close()
    # Return True if a new row was inserted, False if updated
    return not exists

def add_or_update_uniform(id, student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num, status, is_checked_in, notes):
    conn, cursor = connect_db()
    cursor.execute("SELECT 1 FROM uniforms WHERE id = ?", (id,))
    exists = cursor.fetchone() is not None
    if exists:
        cursor.execute('''
            UPDATE uniforms SET student_id=?, shako_num=?, hanger_num=?, garment_bag=?, coat_num=?, pants_num=?, status=?, is_checked_in=?, notes=? WHERE id=?
        ''', (student_id or None, shako_num or None, hanger_num or None, garment_bag or None, coat_num or None, pants_num or None, status or None, int(is_checked_in) if is_checked_in not in (None, '') else 1, notes or None, id))
    else:
        cursor.execute('''
            INSERT INTO uniforms (id, student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num, status, is_checked_in, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id, student_id or None, shako_num or None, hanger_num or None, garment_bag or None, coat_num or None, pants_num or None, status or None, int(is_checked_in) if is_checked_in not in (None, '') else 1, notes or None))
    conn.commit()
    conn.close()
    return not exists

def add_or_update_instrument(id, student_id, name, serial, case, model, condition, status, is_checked_in, notes):
    conn, cursor = connect_db()
    cursor.execute("SELECT 1 FROM instruments WHERE id = ?", (id,))
    exists = cursor.fetchone() is not None
    if exists:
        cursor.execute('''
            UPDATE instruments SET student_id=?, instrument_name=?, instrument_serial=?, instrument_case=?, model=?, condition=?, status=?, is_checked_in=?, notes=? WHERE id=?
        ''', (student_id or None, name or None, serial or None, case or None, model or None, condition or None, status or None, int(is_checked_in) if is_checked_in not in (None, '') else 1, notes or None, id))
    else:
        cursor.execute('''
            INSERT INTO instruments (id, student_id, instrument_name, instrument_serial, instrument_case, model, condition, status, is_checked_in, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id, student_id or None, name or None, serial or None, case or None, model or None, condition or None, status or None, int(is_checked_in) if is_checked_in not in (None, '') else 1, notes or None))
    conn.commit()
    conn.close()
    return not exists

def create_instrument_table():
    """
    Creates the 'instruments' table if it doesn't exist.
    Tracks instruments with optional student assignment.
    """
    conn, cursor = connect_db()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instruments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NULL,
            instrument_name TEXT,
            instrument_section TEXT,
            instrument_serial TEXT,
            instrument_case TEXT,
            model TEXT,
            condition TEXT CHECK(condition IN ('Excellent','Good','Fair','Poor')) DEFAULT 'Good',
            status TEXT CHECK(status IN ('Available','Assigned','Maintenance','Retired')) DEFAULT 'Available',
            is_checked_in BOOLEAN DEFAULT 1,
            notes TEXT,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
    ''')
    conn.commit()
    conn.close()
    # Ensure instrument_section column exists for older DBs
    conn, cursor = connect_db()
    cursor.execute("PRAGMA table_info(instruments)")
    cols = [r[1] for r in cursor.fetchall()]
    if 'instrument_section' not in cols:
        try:
            cursor.execute("ALTER TABLE instruments ADD COLUMN instrument_section TEXT")
            conn.commit()
        except Exception:
            # If alter fails for any reason, ignore; app can continue without section
            pass
    conn.close()

# ------------------------------------------------------------------------------
# Student functions
# ------------------------------------------------------------------------------

def add_student(
    student_id, first_name, last_name, phone, email, year_came_up,
    status, guardian_name, guardian_phone, section,
    shako_num=None, hanger_num=None, garment_bag=None,
    coat_num=None, pants_num=None,
    instrument_name=None, instrument_serial=None, instrument_case=None
):
    """
    Inserts a new student record.
    Then conditionally adds uniform/instrument records if any related fields are provided.
    """
    conn, cursor = connect_db()
    cursor.execute('''
        INSERT INTO students (
            student_id, first_name, last_name, phone, email, year_came_up,
            status, guardian_name, guardian_phone, section
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        student_id, first_name, last_name, phone, email, year_came_up,
        status, guardian_name, guardian_phone, section
    ))

    # Add uniform assignment if any uniform fields are provided
    if any(x not in (None, "") for x in [shako_num, hanger_num, garment_bag, coat_num, pants_num]):
        cursor.execute('''
            INSERT INTO uniforms (
                student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num, is_checked_in
            ) VALUES (?, ?, ?, ?, ?, ?, 0)
        ''', (student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num))

    # Add instrument assignment if any instrument fields are provided
    if any(x not in (None, "") for x in [instrument_name, instrument_serial, instrument_case]):
        cursor.execute('''
            INSERT INTO instruments (
                student_id, instrument_name, instrument_serial, instrument_case, is_checked_in
            ) VALUES (?, ?, ?, ?, 0)
        ''', (student_id, instrument_name, instrument_serial, instrument_case))

    conn.commit()
    conn.close()

def get_student_by_id(student_id):
    """
    Retrieve a single student's details by their ID.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()
    conn.close()
    return student

def get_student_by_name(first_name, last_name):
    """
    Retrieve a single student's details by full name.
    """
    conn, cursor = connect_db()
    cursor.execute(
        "SELECT * FROM students WHERE first_name = ? AND last_name = ?",
        (first_name, last_name)
    )
    student = cursor.fetchone()
    conn.close()
    return student

def get_students_by_last_name(last_name):
    """
    Fetch all students matching a last name (case-insensitive).
    """
    conn, cursor = connect_db()
    cursor.execute(
        "SELECT * FROM students WHERE last_name = ? COLLATE NOCASE",
        (last_name,)
    )
    students = cursor.fetchall()
    conn.close()
    return students

def get_students_by_section(section):
    """
    Fetch all students in a given section.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM students WHERE section = ?", (section,))
    students = cursor.fetchall()
    conn.close()
    return students

def get_students():
    """
    Fetch all student records.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return students

def update_student(student_id, field, new_value):
    """
    Update a student's single field. Validates phone lengths and enforces
    allowed values for status and section.
    """
    conn, cursor = connect_db()

    valid_fields = {
        "first_name", "last_name", "phone", "email",
        "year_came_up", "status", "guardian_name",
        "guardian_phone", "section"
    }
    status_options = {"Student", "Former", "Alumni"}
    section_options = {
        "Trumpet", "Trombone", "Euphonium", "French Horn", "Tuba",
        "Flute", "Clarinet", "Saxophone", "Bassoon", "Oboe", "Percussion"
    }

    if field not in valid_fields:
        print(f"Error: Invalid field '{field}'")
        conn.close()
        return

    # Validate status
    if field == "status" and new_value not in status_options:
        print(f"Error: Status must be one of {status_options}")
        conn.close()
        return

    # Validate section
    if field == "section" and new_value not in section_options:
        print(f"Error: Section must be one of {section_options}")
        conn.close()
        return

    # Validate phone numbers
    if field in {"phone", "guardian_phone"}:
        if new_value in (None, ""):
            new_value = None
        elif not str(new_value).isdigit() or len(str(new_value)) != 10:
            print("Error: Phone number must be exactly 10 digits.")
            conn.close()
            return

    # Normalize empty strings to NULL
    if new_value in (None, "", "None"):
        new_value = None

    query = f"UPDATE students SET {field} = ? WHERE student_id = ?"
    cursor.execute(query, (new_value, student_id))
    conn.commit()
    conn.close()

def delete_student(student_id):
    """
    Delete a student record if it exists.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT 1 FROM students WHERE student_id = ?", (student_id,))
    if cursor.fetchone() is None:
        print("Error: Student ID not found.")
        conn.close()
        return
    # Before deleting the student, unassign any related equipment:
    try:
        # Unassign uniforms: set student_id NULL, mark checked in and available
        cursor.execute("UPDATE uniforms SET student_id = NULL, is_checked_in = 1, status = 'Available' WHERE student_id = ?", (student_id,))
        # Unassign instruments
        cursor.execute("UPDATE instruments SET student_id = NULL, is_checked_in = 1, status = 'Available' WHERE student_id = ?", (student_id,))
        # Unassign component parts (shakos, coats, pants, garment_bags)
        cursor.execute("UPDATE shakos SET student_id = NULL, status = 'Available' WHERE student_id = ?", (student_id,))
        cursor.execute("UPDATE coats SET student_id = NULL, status = 'Available' WHERE student_id = ?", (student_id,))
        cursor.execute("UPDATE pants SET student_id = NULL, status = 'Available' WHERE student_id = ?", (student_id,))
        cursor.execute("UPDATE garment_bags SET student_id = NULL, status = 'Available' WHERE student_id = ?", (student_id,))
    except Exception:
        # best-effort: ignore failures and continue to delete student
        pass

    cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()

# ------------------------------------------------------------------------------
# Uniform functions
# ------------------------------------------------------------------------------

def assign_uniform(student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num):
    """
    Assign a new uniform to a student. Marks it as 'not returned'.
    """
    conn, cursor = connect_db()
    cursor.execute('''
        INSERT INTO uniforms (
            student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num, is_checked_in
        ) VALUES (?, ?, ?, ?, ?, ?, 0)
    ''', (student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num))
    conn.commit()
    conn.close()

def return_uniform(student_id):
    """
    Mark the latest uniform assignment as returned (is_checked_in = 1).
    """
    conn, cursor = connect_db()
    cursor.execute('''
        UPDATE uniforms
        SET is_checked_in = 1
        WHERE student_id = ? AND is_checked_in = 0
    ''', (student_id,))
    conn.commit()
    conn.close()


def assign_shako_to_student(shako_num, student_id):
    """Mark a shako as assigned to a student."""
    conn, cursor = connect_db()
    cursor.execute("UPDATE shakos SET status='Assigned', student_id=? WHERE shako_num=?",
                   (student_id, shako_num))
    conn.commit()
    conn.close()


def assign_coat_to_student(coat_num, student_id):
    """Mark a coat as assigned to a student."""
    conn, cursor = connect_db()
    cursor.execute("UPDATE coats SET status='Assigned', student_id=? WHERE coat_num=?",
                   (student_id, coat_num))
    conn.commit()
    conn.close()


def assign_pants_to_student(pants_num, student_id):
    """Mark a pants entry as assigned to a student."""
    conn, cursor = connect_db()
    cursor.execute("UPDATE pants SET status='Assigned', student_id=? WHERE pants_num=?",
                   (student_id, pants_num))
    conn.commit()
    conn.close()


def assign_bag_to_student(bag_num, student_id):
    """Mark a garment bag as assigned to a student."""
    conn, cursor = connect_db()
    cursor.execute("UPDATE garment_bags SET status='Assigned', student_id=? WHERE bag_num=?",
                   (student_id, bag_num))
    conn.commit()
    conn.close()

def is_shako_available(shako_num):
    conn, cursor = connect_db()
    cursor.execute("SELECT status FROM shakos WHERE shako_num = ?", (shako_num,))
    r = cursor.fetchone()
    conn.close()
    return (r is not None) and (r[0] == 'Available')

def is_coat_available(coat_num):
    conn, cursor = connect_db()
    cursor.execute("SELECT status FROM coats WHERE coat_num = ?", (coat_num,))
    r = cursor.fetchone()
    conn.close()
    return (r is not None) and (r[0] == 'Available')

def is_pants_available(pants_num):
    conn, cursor = connect_db()
    cursor.execute("SELECT status FROM pants WHERE pants_num = ?", (pants_num,))
    r = cursor.fetchone()
    conn.close()
    return (r is not None) and (r[0] == 'Available')

def is_bag_available(bag_num):
    conn, cursor = connect_db()
    cursor.execute("SELECT status FROM garment_bags WHERE bag_num = ?", (bag_num,))
    r = cursor.fetchone()
    conn.close()
    return (r is not None) and (r[0] == 'Available')

def update_shako(shako_num, student_id=None, status=None, notes=None):
    conn, cursor = connect_db()
    fields = []
    params = []
    # Always update student_id, even if None (set to NULL)
    fields.append("student_id = ?")
    params.append(student_id)
    if status is not None:
        fields.append("status = ?")
        params.append(status)
    if notes is not None:
        fields.append("notes = ?")
        params.append(notes)
    if not fields:
        conn.close()
        return
    params.append(shako_num)
    cursor.execute(f"UPDATE shakos SET {', '.join(fields)} WHERE shako_num = ?", tuple(params))
    conn.commit()
    conn.close()

def update_coat(coat_num, student_id=None, status=None, hanger_num=None, notes=None):
    conn, cursor = connect_db()
    fields = []
    params = []
    # Always update student_id, even if None (set to NULL)
    fields.append("student_id = ?")
    params.append(student_id)
    if status is not None:
        fields.append("status = ?")
        params.append(status)
    if hanger_num is not None:
        fields.append("hanger_num = ?")
        params.append(hanger_num)
    if notes is not None:
        fields.append("notes = ?")
        params.append(notes)
    if not fields:
        conn.close()
        return
    params.append(coat_num)
    cursor.execute(f"UPDATE coats SET {', '.join(fields)} WHERE coat_num = ?", tuple(params))
    conn.commit()
    conn.close()

def update_pants(pants_num, student_id=None, status=None, notes=None):
    conn, cursor = connect_db()
    fields = []
    params = []
    # Always update student_id, even if None (set to NULL)
    fields.append("student_id = ?")
    params.append(student_id)
    if status is not None:
        fields.append("status = ?")
        params.append(status)
    if notes is not None:
        fields.append("notes = ?")
        params.append(notes)
    if not fields:
        conn.close()
        return
    params.append(pants_num)
    cursor.execute(f"UPDATE pants SET {', '.join(fields)} WHERE pants_num = ?", tuple(params))
    conn.commit()
    conn.close()

def update_bag(bag_num, student_id=None, status=None, notes=None):
    conn, cursor = connect_db()
    fields = []
    params = []
    # Always update student_id, even if None (set to NULL)
    fields.append("student_id = ?")
    params.append(student_id)
    if status is not None:
        fields.append("status = ?")
        params.append(status)
    if notes is not None:
        fields.append("notes = ?")
        params.append(notes)
    if not fields:
        conn.close()
        return
    params.append(bag_num)
    cursor.execute(f"UPDATE garment_bags SET {', '.join(fields)} WHERE bag_num = ?", tuple(params))
    conn.commit()
    conn.close()

def get_students_with_uniforms_and_instruments():
    """
    Fetch all students plus their latest assigned uniform and instrument details, if any.
    """
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT
            s.student_id, s.first_name, s.last_name, s.status,
            s.phone, s.email, s.guardian_name, s.guardian_phone, s.year_came_up, s.section,
            u.shako_num, u.hanger_num, u.garment_bag, u.coat_num, u.pants_num,
            i.instrument_name, i.instrument_serial, i.instrument_case
        FROM students s
        LEFT JOIN (
            SELECT * FROM uniforms
            WHERE is_checked_in = 0
            GROUP BY student_id
            HAVING MAX(id)
        ) u ON s.student_id = u.student_id
        LEFT JOIN (
            SELECT * FROM instruments
            WHERE is_checked_in = 0
            GROUP BY student_id
            HAVING MAX(id)
        ) i ON s.student_id = i.student_id
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_students_with_outstanding_uniforms():
    """
    Get students who currently have uniforms assigned and not returned.
    """
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT s.first_name, s.last_name,
               u.shako_num, u.hanger_num, u.garment_bag, u.coat_num, u.pants_num
        FROM students s
        JOIN uniforms u ON s.student_id = u.student_id
        WHERE u.is_checked_in = 0
          AND u.id = (
              SELECT MAX(id) FROM uniforms
              WHERE student_id = s.student_id AND is_checked_in = 0
          )
    ''')
    results = cursor.fetchall()
    conn.close()
    return results

def get_students_with_outstanding_uniforms_by_section(section):
    """
    Get students in a specific section who currently have uniforms assigned.
    """
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT s.first_name, s.last_name,
               u.shako_num, u.hanger_num, u.garment_bag, u.coat_num, u.pants_num
        FROM students s
        JOIN uniforms u ON s.student_id = u.student_id
        WHERE u.is_checked_in = 0
          AND s.section = ?
          AND u.id = (
              SELECT MAX(id) FROM uniforms
              WHERE student_id = s.student_id AND is_checked_in = 0
          )
    ''', (section,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_uniforms():
    """
    Fetch all uniform records with their current status.
    """
    conn, cursor = connect_db()
    cursor.execute("""
        SELECT id, student_id, shako_num, hanger_num, garment_bag,
               coat_num, pants_num, status, is_checked_in, notes
        FROM uniforms
        ORDER BY 
            CASE status 
                WHEN 'Assigned' THEN 1
                WHEN 'Available' THEN 2
                WHEN 'Maintenance' THEN 3
                WHEN 'Retired' THEN 4
            END,
            id
    """)
    results = cursor.fetchall()
    conn.close()
    return results

def add_uniform(id, student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num, is_checked_in):
    """
    Manually insert a uniform record (used for admin or migration).
    """
    conn, cursor = connect_db()
    cursor.execute('''
        INSERT INTO uniforms (
            id, student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num, is_checked_in
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (id, student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num, is_checked_in))
    conn.commit()
    conn.close()

# ------------------------------------------------------------------------------
# Instrument functions
# ------------------------------------------------------------------------------

def assign_instrument(student_id, instrument_name, instrument_serial, instrument_case):
    """
    Assign a new instrument to a student. Marks it as 'not returned'.
    """
    conn, cursor = connect_db()
    cursor.execute('''
        INSERT INTO instruments (
            student_id, instrument_name, instrument_serial, instrument_case, is_checked_in
        ) VALUES (?, ?, ?, ?, 0)
    ''', (student_id, instrument_name, instrument_serial, instrument_case))
    conn.commit()
    conn.close()

def return_instrument(student_id):
    """
    Mark the latest instrument assignment as returned (is_checked_in = 1).
    """
    conn, cursor = connect_db()
    cursor.execute('''
        UPDATE instruments
        SET is_checked_in = 1, student_id = NULL, status = 'Available'
        WHERE student_id = ? AND status = 'Assigned'
    ''', (student_id,))
    conn.commit()
    conn.close()

def get_students_with_outstanding_instruments():
    """
    Get students who currently have instruments assigned and not returned.
    """
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT s.first_name, s.last_name, s.section,
               i.instrument_name, i.instrument_serial, i.instrument_case
        FROM students s
        JOIN instruments i ON s.student_id = i.student_id
        WHERE i.is_checked_in = 0
          AND i.id = (
              SELECT MAX(id) FROM instruments
              WHERE student_id = s.student_id AND is_checked_in = 0
          )
    ''')
    results = cursor.fetchall()
    conn.close()
    return results

def get_students_with_outstanding_instruments_by_section(section):
    """
    Get students in a specific section who currently have instruments assigned.
    """
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT s.first_name, s.last_name, s.section,
               i.instrument_name, i.instrument_serial, i.instrument_case
        FROM students s
        JOIN instruments i ON s.student_id = i.student_id
        WHERE i.is_checked_in = 0
          AND s.section = ?
          AND i.id = (
              SELECT MAX(id) FROM instruments
              WHERE student_id = s.student_id AND is_checked_in = 0
          )
    ''', (section,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_instruments():
    """
    Fetch all instrument records with their current status and condition.
    """
    conn, cursor = connect_db()
    cursor.execute("""
        SELECT id, student_id, instrument_name, instrument_serial,
               instrument_case, model, condition, status, is_checked_in, notes
        FROM instruments
        ORDER BY 
            CASE status 
                WHEN 'Assigned' THEN 1
                WHEN 'Available' THEN 2
                WHEN 'Maintenance' THEN 3
                WHEN 'Retired' THEN 4
            END,
            instrument_name,
            id
    """)
    results = cursor.fetchall()
    conn.close()
    return results

def add_instrument(id, student_id, instrument_name, instrument_serial, instrument_case, is_checked_in):
    """
    Manually insert an instrument record (used for admin or migration).
    """
    conn, cursor = connect_db()
    cursor.execute('''
        INSERT INTO instruments (
            id, student_id, instrument_name, instrument_serial, instrument_case, is_checked_in
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (id, student_id, instrument_name, instrument_serial, instrument_case, is_checked_in))
    conn.commit()
    conn.close()

# ------------------------------------------------------------------------------
# Admin utility functions
# ------------------------------------------------------------------------------

def delete_all_students():
    """Delete all student records from the database."""
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM students")
    conn.commit()
    conn.close()

def delete_all_shakos():
    """Delete all shako records from the database."""
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM shakos")
    conn.commit()
    conn.close()

def delete_all_coats():
    """Delete all coat records from the database."""
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM coats")
    conn.commit()
    conn.close()

def delete_all_pants():
    """Delete all pants records from the database."""
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM pants")
    conn.commit()
    conn.close()

def delete_all_garment_bags():
    """Delete all garment bag records from the database."""
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM garment_bags")
    conn.commit()
    conn.close()

def delete_all_uniforms():
    """Delete all uniform records from the database."""
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM uniforms")
    conn.commit()
    conn.close()

def delete_all_instruments():
    """Delete all instrument records from the database."""
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM instruments")
    conn.commit()
    conn.close()