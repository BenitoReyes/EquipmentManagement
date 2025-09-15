import sqlite3
import sys, os

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
# DB_NAME = resource_path("Database/students.db")

# Use this if you're shipping the DB alongside the .exe (recommended)
DB_NAME = os.path.join(os.path.dirname(sys.executable), "Database", "students.db")
# Establishes a connection to the database and returns both the connection and cursor
def connect_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    return conn, cursor

# Creates the students table if it doesn't exist
def create_student_table():
    conn, cursor = connect_db()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
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
        guardian_phone TEXT,
        instrument_name TEXT,
        instrument_serial TEXT,
        instrument_case TEXT,
        year_came_up TEXT
    )''')
    conn.commit()
    conn.close()

#STUDENT FUNCTIONS
# Adds a new student and conditionally inserts uniform/instrument records
def add_student(student_id, first_name, last_name, section, phone, email, shako_num, hanger_num,
                garment_bag, coat_num, pants_num, spats_size, gloves_size, guardian_name, guardian_phone,
                instrument_name, instrument_serial, instrument_case, year_came_up):
    conn, cursor = connect_db()
    cursor.execute('''
        INSERT INTO students (student_id, first_name, last_name, section, phone, email,
                              shako_num, hanger_num, garment_bag, coat_num, pants_num,
                              spats_size, gloves_size, guardian_name, guardian_phone,
                              instrument_name, instrument_serial, instrument_case, year_came_up)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        student_id, first_name, last_name, section, phone, email,
        shako_num if shako_num not in ("", None) else None,
        hanger_num if hanger_num not in ("", None) else None,
        garment_bag if garment_bag not in ("", None) else None,
        coat_num if coat_num not in ("", None) else None,
        pants_num if pants_num not in ("", None) else None,
        spats_size, gloves_size, guardian_name, guardian_phone,
        instrument_name if instrument_name not in ("", None) else None,
        instrument_serial if instrument_serial not in ("", None) else None,
        instrument_case if instrument_case not in ("", None) else None,
        year_came_up if year_came_up not in ("", None) else None
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

    # Instrument logic: same as uniform
    if any(x not in ("", None) for x in [instrument_name, instrument_serial, instrument_case]):
        cursor.execute('''
            INSERT INTO instruments (student_id, instrument_name, instrument_serial, instrument_case, is_checked_in)
            VALUES (?, ?, ?, ?, 0)
        ''', (
            student_id,
            instrument_name if instrument_name not in ("", None) else None,
            instrument_serial if instrument_serial not in ("", None) else None,
            instrument_case if instrument_case not in ("", None) else None
        ))
    conn.commit()
    conn.close()

# Fetches a student by ID
def get_student_by_id(student_id):
    """Retrieve a single student's details by ID."""
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()
    conn.close()
    return student

# Fetches a student by full name
def get_student_by_name(first_name, last_name):
    """Retrieve a single student's details by name."""
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM students WHERE first_name = ? AND last_name = ?", (first_name, last_name))
    student = cursor.fetchone()
    conn.close()
    return student

# Fetches all students with a matching last name (case-insensitive)
def get_students_by_last_name(last_name):
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM students WHERE last_name = ? COLLATE NOCASE", (last_name,))
    students = cursor.fetchall()
    conn.close()
    return students

# Fetches all students in a given section
def get_students_by_section(section):
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM students WHERE section = ?", (section,))
    students = cursor.fetchall()
    conn.close()
    return students

# Fetches all student records
def get_students():
    """Fetch all student records."""
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return students

# Updates a specific field for a student
def update_student(student_id, field, new_value):
    """Update a student's record safely."""
    conn, cursor = connect_db()

    valid_fields = {
        "first_name", "last_name", "section", "phone", "email",
        "shako_num", "hanger_num", "garment_bag", "coat_num", "pants_num",
        "spats_size", "gloves_size", "guardian_name", "guardian_phone",
        "instrument_name", "instrument_serial", "instrument_case", "year_came_up"
    }

    if field not in valid_fields:
        print(f"Error: Invalid field '{field}'")
        conn.close()
        return

    # Handle phone number validation
    if field in {"phone", "guardian_phone"}:
        if new_value in ("", None):
            new_value = None  # Set to NULL in DB
        elif not str(new_value).isdigit() or len(str(new_value)) != 10:
            print("Error: Phone number must be 10 digits.")
            conn.close()
            return

    # Handle other empty values
    if new_value in ("", "None", None):
        new_value = None

    query = f"UPDATE students SET {field} = ? WHERE student_id = ?"
    cursor.execute(query, (new_value, student_id))

    conn.commit()
    conn.close()

# Deletes a student only if they exist
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

#UNIFORM FUNCTIONS
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

# Assigns a uniform to a student
def assign_uniform(student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num):
    conn, cursor = connect_db()
    cursor.execute('''
        INSERT INTO uniforms (student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num, is_checked_in)
        VALUES (?, ?, ?, ?, ?, ?, 0)
    ''', (student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num))
    conn.commit()
    conn.close()
    
# Marks a student's uniform as returned and clears their student record fields
def return_uniform(student_id):
    conn, cursor = connect_db()

    # Mark uniform as returned
    cursor.execute('''
        UPDATE uniforms SET is_checked_in = 1
        WHERE student_id = ? AND is_checked_in = 0
    ''', (student_id,))

    # Clear uniform fields in students table
    cursor.execute('''
        UPDATE students
        SET shako_num = NULL, hanger_num = NULL, garment_bag = NULL, coat_num = NULL, pants_num = NULL
        WHERE student_id = ?
    ''', (student_id,))
    conn.commit()
    conn.close()

# Fetches all students with their latest uniform and instrument assignments
def get_students_with_uniforms_and_instruments():
    """
    Fetch all students and their latest assigned uniform and instrument (if any).
    Returns a list of tuples, each containing all student fields,
    latest uniform fields, and latest instrument fields.
    """
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT
            s.student_id, s.last_name, s.first_name, s.section, s.phone, s.email,
            COALESCE(u.shako_num, s.shako_num) as shako_num,
            COALESCE(u.hanger_num, s.hanger_num) as hanger_num,
            COALESCE(u.garment_bag, s.garment_bag) as garment_bag,
            COALESCE(u.coat_num, s.coat_num) as coat_num,
            COALESCE(u.pants_num, s.pants_num) as pants_num,
            s.spats_size, s.gloves_size, s.guardian_name, s.guardian_phone,
            COALESCE(i.instrument_name, s.instrument_name) as instrument_name,
            COALESCE(i.instrument_serial, s.instrument_serial) as instrument_serial,
            COALESCE(i.instrument_case, s.instrument_case) as instrument_case,
            s.year_came_up
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
        LEFT JOIN (
            SELECT ii.student_id, ii.instrument_name, ii.instrument_serial, ii.instrument_case
            FROM instruments ii
            WHERE ii.is_checked_in = 0
              AND ii.id = (
                  SELECT MAX(id) FROM instruments
                  WHERE student_id = ii.student_id AND is_checked_in = 0
              )
        ) i ON s.student_id = i.student_id
    ''')
    students = cursor.fetchall()
    conn.close()
    return students

# Fetches students with outstanding uniforms
def get_students_with_outstanding_uniforms():
    """Get all students with uniforms that are not returned and contain actual data."""
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT s.first_name, s.last_name, u.shako_num, u.hanger_num,
               u.garment_bag, u.coat_num, u.pants_num
        FROM students s
        JOIN uniforms u ON s.student_id = u.student_id
        WHERE u.is_checked_in = 0
          AND u.id = (
              SELECT MAX(id) FROM uniforms
              WHERE student_id = s.student_id AND is_checked_in = 0
          )
          AND (
              u.shako_num IS NOT NULL OR
              u.hanger_num IS NOT NULL OR
              u.garment_bag IS NOT NULL OR
              u.coat_num IS NOT NULL OR
              u.pants_num IS NOT NULL
          )
    ''')
    results = cursor.fetchall()
    conn.close()
    return results

# Same as above, but filtered by section
def get_students_with_outstanding_uniforms_by_section(section):
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT s.first_name, s.last_name, u.shako_num, u.hanger_num,
               u.garment_bag, u.coat_num, u.pants_num
        FROM students s
        JOIN uniforms u ON s.student_id = u.student_id
        WHERE u.is_checked_in = 0
          AND s.section = ?
          AND u.id = (
              SELECT MAX(id) FROM uniforms
              WHERE student_id = s.student_id AND is_checked_in = 0
          )
          AND (
              u.shako_num IS NOT NULL OR
              u.hanger_num IS NOT NULL OR
              u.garment_bag IS NOT NULL OR
              u.coat_num IS NOT NULL OR
              u.pants_num IS NOT NULL
          )
    ''', (section,))
    results = cursor.fetchall()
    conn.close()
    return results

# Fetches all uniform records
def get_all_uniforms():
    conn, cursor = connect_db()
    # Fetch all uniforms
    query = "SELECT * FROM uniforms"
    cursor.execute(query)
    return cursor.fetchall()

# Adds a uniform record manually (used for admin or migration)
def add_uniform(id, student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num, is_checked_in):
    conn, cursor = connect_db()
    cursor.execute(
        "INSERT INTO uniforms (id, student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num, is_checked_in) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (id, student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num, is_checked_in)
    )
    conn.commit()
    conn.close()

#INSTRUMENT FUNCTIONS
def create_instrument_table():
    conn, cursor = connect_db()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instruments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            instrument_name TEXT,
            instrument_serial TEXT,
            instrument_case TEXT,
            is_checked_in BOOLEAN DEFAULT 0,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
    ''')
    conn.commit()
    conn.close()

def assign_instrument(student_id, instrument_name, instrument_serial, instrument_case):
    """Assign an instrument to a student (mark as not returned)."""
    conn, cursor = connect_db()
    cursor.execute('''
        INSERT INTO instruments (student_id, instrument_name, instrument_serial, instrument_case, is_checked_in)
        VALUES (?, ?, ?, ?, 0)
    ''', (student_id, instrument_name, instrument_serial, instrument_case))
    conn.commit()
    conn.close()

# Marks instrument as returned and clears student record fields
def return_instrument(student_id):
    """Mark the latest assigned instrument as returned for a student."""
    conn, cursor = connect_db()

    # Mark instrument as returned
    cursor.execute('''
        UPDATE instruments SET is_checked_in = 1
        WHERE student_id = ? AND is_checked_in = 0
    ''', (student_id,))

    # Clear instrument fields in students table
    cursor.execute('''
        UPDATE students
        SET instrument_name = NULL, instrument_serial = NULL, instrument_case = NULL
        WHERE student_id = ?
    ''', (student_id,))
    conn.commit()
    conn.close()

def get_students_with_outstanding_instruments():
    """Get all students with instruments that are not returned and contain actual data."""
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT s.first_name, s.last_name, i.instrument_name, i.instrument_serial, i.instrument_case
        FROM students s
        JOIN instruments i ON s.student_id = i.student_id
        WHERE i.is_checked_in = 0
          AND i.id = (
              SELECT MAX(id) FROM instruments
              WHERE student_id = s.student_id AND is_checked_in = 0
          )
          AND (
              i.instrument_name IS NOT NULL OR
              i.instrument_serial IS NOT NULL OR
              i.instrument_case IS NOT NULL
          )
    ''')
    results = cursor.fetchall()
    conn.close()
    return results

def get_students_with_outstanding_instruments_by_section(section):
    """Get all students from a specific section with instruments that are not returned and contain actual data."""
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT s.first_name, s.last_name, i.instrument_name, i.instrument_serial, i.instrument_case
        FROM students s
        JOIN instruments i ON s.student_id = i.student_id
        WHERE i.is_checked_in = 0
          AND s.section = ?
          AND i.id = (
              SELECT MAX(id) FROM instruments
              WHERE student_id = s.student_id AND is_checked_in = 0
          )
          AND (
              i.instrument_name IS NOT NULL OR
              i.instrument_serial IS NOT NULL OR
              i.instrument_case IS NOT NULL
          )
    ''', (section,))
    results = cursor.fetchall()
    conn.close()
    return results

# Adds an instrument record manually
def get_all_instruments():
    conn, cursor = connect_db()
    
    # Fetch all instruments
    query = "SELECT * FROM instruments"
    cursor.execute(query)
    return cursor.fetchall()

def add_instrument(id, student_id, instrument_name, instrument_serial, instrument_case, is_checked_in):
    conn, cursor = connect_db()
    cursor.execute(
        "INSERT INTO instruments (id, student_id, instrument_name, instrument_serial, instrument_case, is_checked_in) VALUES (?, ?, ?, ?, ?, ?)",
        (id, student_id, instrument_name, instrument_serial, instrument_case, is_checked_in)
    )
    conn.commit()
    conn.close()

#ADMIN FUNCTIONS
def delete_all_students():
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM students")
    conn.commit()
    conn.close()

def delete_all_uniforms():
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM uniforms")
    conn.commit()
    conn.close()

def delete_all_instruments():
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM instruments")
    conn.commit()
    conn.close()


