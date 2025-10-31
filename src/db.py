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
# ------------------------------------------------------------------------------
# Database Core Module
# ------------------------------------------------------------------------------
# This module handles all database operations for the Equipment Management System.
# It uses SQLite3 for data storage with the following structure:
#
# Tables:
# - students: Core student information and section assignments
# - uniforms: Tracks complete uniform sets assigned to students
# - instruments: Manages instrument inventory and assignments
# - shakos, coats, pants, garment_bags: Individual uniform components
#
# Key Features:
# - Maintains referential integrity between students and equipment
# - Tracks equipment status (Available, Assigned, Maintenance, Retired)
# - Preserves assignment history for auditing
# ------------------------------------------------------------------------------

import sqlite3
import sys
import os

def resource_path(relative_path):
    """
    Resolves path to resource whether running from source or PyInstaller bundle.
    If bundled, uses the temporary _MEIPASS directory.
    If not, uses the current working directory.
    
    This function ensures the database file can be found both during development
    and after PyInstaller packaging into an exe.
    """
    if hasattr(sys, '_MEIPASS'):
        # Running from PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    # Running from source
    return os.path.join(os.path.abspath("."), relative_path)

# Database path configuration
# For development: Database in the project structure
DB_NAME = resource_path("Database/students.db")

# For deployment: Database alongside the executable (uncomment when packaging)
#DB_NAME = os.path.join(os.path.dirname(sys.executable), "Database", "students.db")

# Database Connection Management
# Each function should use this to get a fresh connection and close it when done

def connect_db():
    """
    Establishes a new connection to the SQLite database.
    
    Returns:
        tuple: (sqlite3.Connection, sqlite3.Cursor)
            - Connection object for transaction management
            - Cursor object for executing SQL commands
            
    Note:
        Every function should:
        1. Call this to get a fresh connection
        2. Use the cursor for queries
        3. Commit if making changes
        4. Close the connection when done
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    return conn, cursor

# ------------------------------------------------------------------------------
# Table creation functions
# ------------------------------------------------------------------------------
# These functions define the database schema and ensure all required tables exist.
# Each table has specific constraints and relationships:
#
# students:
#   - Primary key: student_id (TEXT)
#   - Tracks: names, section, contact info
#
# uniforms:
#   - Composite tracking of all uniform components
#   - Foreign key: student_id → students.student_id
#
# instruments:
#   - Tracks instrument inventory and assignments
#   - Foreign key: student_id → students.student_id
#   - Status tracking: Available, Assigned, Maintenance, Retired
# ------------------------------------------------------------------------------

def create_student_table():
    """
    Creates the 'students' table if it doesn't exist.
    This is the core table that all equipment assignments reference.
    
    Table Structure:
    - student_id (TEXT PRIMARY KEY): Unique identifier
    - first_name (TEXT): Student's first name
    - last_name (TEXT): Student's last name
    - section (TEXT): Band section/instrument group
        Valid sections include: Flags, Trumpet, etc.
    - grade (INTEGER): Student's grade level
    - phone (TEXT): Contact phone number
    - parent_phone (TEXT): Parent/guardian contact
    - email (TEXT): Student email address
    - notes (TEXT): Additional remarks
    
    Notes:
    - student_id is TEXT to allow for non-numeric IDs
    - All equipment tables reference back to this table
    - Sections list is extensible for different band configurations
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
    Creates the 'shakos' table for tracking individual marching band hats.
    
    Table Structure:
    - id (INTEGER PRIMARY KEY): Auto-incrementing unique identifier
    - number (TEXT): Shako identification number
    - size (TEXT): Hat size (S, M, L, XL, etc.)
    - condition (TEXT): Current state of the shako
    - location (TEXT): Storage location or assignment status
    - notes (TEXT): Maintenance history or special instructions
    
    Notes:
    - Each shako is tracked individually for precise inventory
    - Size field helps with quick student assignments
    - Condition tracking enables maintenance scheduling
    - Location tracking prevents loss of equipment
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
    Creates the 'coats' table for tracking band uniform coats/jackets.
    
    Table Structure:
    - id (INTEGER PRIMARY KEY): Auto-incrementing unique identifier
    - coat_num (INTEGER UNIQUE): Unique coat identification number
    - hanger_num (INTEGER): Associated hanger number for storage
    - status (TEXT): Current state with constraints:
        * Available: Ready for assignment
        * Assigned: Checked out to student
        * Maintenance: Being repaired/cleaned
        * Retired: No longer in service
    - student_id (TEXT): FK to students table, NULL if unassigned
    - notes (TEXT): Condition notes, maintenance history
    
    Constraints:
    - Foreign key to students table ensures data integrity
    - Status field limited to predefined values
    - Coat numbers must be unique in inventory
    
    Usage:
    - Tracks both assignment status and physical location (hanger)
    - Enables quick inventory and maintenance scheduling
    - Maintains history through notes field
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
    Creates the 'pants' table for tracking band uniform pants/trousers.
    
    Table Structure:
    - id (INTEGER PRIMARY KEY): Auto-incrementing unique identifier
    - pants_num (INTEGER UNIQUE): Unique pants identification number
    - status (TEXT): Equipment status with constraints:
        * Available: Ready for assignment
        * Assigned: Currently with student
        * Maintenance: Under repair/cleaning
        * Retired: Removed from inventory
    - student_id (TEXT): FK to students table, NULL when unassigned
    - notes (TEXT): Sizing, condition, and maintenance notes
    
    Constraints:
    - Foreign key ensures valid student assignments
    - Status limited to predefined valid states
    - Each pants number must be unique in system
    
    Notes:
    - Part of the complete uniform tracking system
    - Integrated with coat and shako assignments
    - Enables size-based matching with students
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
    Creates the 'garment_bags' table for tracking uniform storage bags.
    
    Table Structure:
    - id (INTEGER PRIMARY KEY): Auto-incrementing unique identifier
    - bag_num (TEXT UNIQUE): Unique bag identifier
    - status (TEXT): Current state with constraints:
        * Available: Ready for use
        * Assigned: With student
        * Maintenance: Being repaired
        * Retired: Out of service
    - student_id (TEXT): FK to students table, NULL if unassigned
    - notes (TEXT): Condition and maintenance notes
    
    Constraints:
    - Foreign key to students maintains data integrity
    - Status field limited to valid values
    - Bag numbers must be unique
    
    Purpose:
    - Protects uniforms during storage and transport
    - Helps track complete uniform sets
    - Ensures proper uniform care by students
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
    Creates the 'uniforms' table to track complete uniform sets.
    
    This table serves as a composite tracker that brings together all uniform
    components (shako, coat, pants, garment bag) into a single record.
    
    Table Structure:
    - id (INTEGER PRIMARY KEY): Auto-incrementing unique identifier
    - student_id (TEXT): FK to students table, NULL if unassigned
    - shako_num (INTEGER): Associated shako number
    - hanger_num (INTEGER): Hanger identifier for coat storage
    - garment_bag (TEXT): Associated storage bag ID
    - coat_num (INTEGER): Assigned coat number
    - pants_num (INTEGER): Assigned pants number
    - status (TEXT): Overall uniform status:
        * Available: Complete set ready for assignment
        * Assigned: Checked out to student
        * Maintenance: One or more pieces being serviced
        * Retired: Set no longer in service
    - notes (TEXT): Set-specific notes and history
    
    Key Features:
    - Links all uniform components to a single student
    - Enables complete uniform tracking and inventory
    - Maintains status of entire uniform set
    - Preserves assignment history through notes
    
    Note:
    This is a master table that provides a high-level view of uniform
    assignments, while individual component tables track detailed status
    of each piece.
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
            notes TEXT,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
    ''')
    conn.commit()
    conn.close()

def create_instrument_table():
    """
    Creates the 'instruments' table for comprehensive instrument tracking.
    
    This table manages the band's instrument inventory with detailed tracking
    of each instrument's characteristics, condition, and assignment status.
    
    Table Structure:
    - id (INTEGER PRIMARY KEY): Auto-incrementing unique identifier
    - instrument_name (TEXT): Type and section (e.g., "Trumpet - Flags")
    - instrument_serial (TEXT): Unique serial number
    - instrument_case (TEXT): Case identifier/number
    - model (TEXT): Specific model information
    - condition (TEXT): Current physical condition
    - status (TEXT): Equipment status:
        * Available: Ready for assignment
        * Assigned: With student
        * Maintenance: Under repair
        * Retired: Out of service
    - student_id (TEXT): FK to students table, NULL if unassigned
    - notes (TEXT): Maintenance history and special instructions
    
    Design Notes:
    - instrument_name combines type and section for better organization
    - Serial numbers enable manufacturer warranty tracking
    - Case tracking prevents mismatched instrument/case pairs
    - Condition tracking helps maintenance scheduling
    - Notes field preserves repair history
    
    Usage:
    - Track all school-owned instruments
    - Manage student assignments
    - Schedule maintenance
    - Monitor instrument condition over time
    """
    conn, cursor = connect_db()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instruments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,      -- Unique ID for each instrument
            student_id TEXT NULL,                      -- Optional: student currently assigned
            instrument_name TEXT,                      -- Combined name and section (e.g., "Tuba - Brass")
            instrument_serial TEXT,                    -- Serial number for tracking
            instrument_case TEXT,                      -- Case identifier
            model TEXT,                                -- Manufacturer model name/number
            condition TEXT CHECK(
                condition IN ('Excellent','Good','Fair','Poor')
            ) DEFAULT 'Good',                          -- Physical condition of instrument
            status TEXT CHECK(
                status IN ('Available','Assigned','Maintenance','Retired')
            ) DEFAULT 'Available',                     -- Usage status
            notes TEXT,                                -- Optional notes (repairs, history, etc.)
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
    ''')

    conn.commit()
    conn.close()

    # Remove legacy support for instrument_section column
    # If older databases still have this column, you can optionally drop it manually

# ------------------------------------------------------------------------------
# Student functions
# ------------------------------------------------------------------------------
# This section contains all functions for managing student records and retrieving
# student information along with their assigned equipment. Key features:
#
# - Comprehensive student lookup by ID or name
# - Equipment assignment tracking
# - Section/group management
# - Contact information handling
# - Status tracking (Student/Former/Alumni)
# ------------------------------------------------------------------------------

def get_student_by_id(student_id):
    """
    Retrieve a single student's complete record by their ID.
    
    This function performs a LEFT JOIN with both uniforms and instruments
    tables to get a complete picture of the student's equipment assignments.
    Only currently assigned items (status = 'Assigned') are included.
    
    Args:
        student_id (str): The student's unique identifier
        
    Returns:
        tuple: Student record containing:
        - Basic Info: ID, name, status, section
        - Contact: phone, email, guardian info
        - Uniform: shako, coat, pants, garment bag numbers
        - Instrument: name, serial number, case ID
        
    Note:
        LEFT JOINs ensure we get student info even if they have
        no equipment assigned. The WHERE clause on status ensures
        we only see current assignments, not historical ones.
    """
    conn, cursor = connect_db()
    cursor.execute("""
        SELECT s.student_id, s.first_name, s.last_name, s.status,
               s.phone, s.email, s.guardian_name, s.guardian_phone,
               s.year_came_up, s.section,
               u.shako_num, u.hanger_num, u.garment_bag, u.coat_num, u.pants_num,
               i.instrument_name, i.instrument_serial, i.instrument_case
        FROM students s
        LEFT JOIN uniforms u 
               ON s.student_id = u.student_id 
              AND u.status = 'Assigned'
        LEFT JOIN instruments i 
               ON s.student_id = i.student_id 
              AND i.status = 'Assigned'
        WHERE s.student_id = ?
    """, (student_id,))
    student = cursor.fetchone()
    conn.close()
    return student

def get_student_by_name(first_name, last_name):
    """
    Lookup a student's complete record using their full name.
    
    This function is similar to get_student_by_id() but searches by name
    instead of ID. It's useful when ID isn't known or for quick lookups.
    The function performs the same comprehensive joins to get all
    equipment assignments.
    
    Args:
        first_name (str): Student's first name
        last_name (str): Student's last name
        
    Returns:
        tuple: Complete student record containing:
        - Basic Info: ID, name, status, section
        - Contact: phone, email, guardian info
        - Uniform: All component numbers
        - Instrument: Current assignment details
        
    Note:
        - Case-sensitive name matching
        - Only returns currently assigned equipment
        - Multiple students with same name possible
        - Prefer get_student_by_id() when ID is known
    """
    conn, cursor = connect_db()
    cursor.execute("""
        SELECT s.student_id, s.first_name, s.last_name, s.status,
               s.phone, s.email, s.guardian_name, s.guardian_phone,
               s.year_came_up, s.section,
               u.shako_num, u.hanger_num, u.garment_bag, u.coat_num, u.pants_num,
               i.instrument_name, i.instrument_serial, i.instrument_case
        FROM students s
        LEFT JOIN uniforms u 
               ON s.student_id = u.student_id 
              AND u.status = 'Assigned'
        LEFT JOIN instruments i 
               ON s.student_id = i.student_id 
              AND i.status = 'Assigned'
        WHERE s.first_name = ? AND s.last_name = ?
    """, (first_name, last_name))
    student = cursor.fetchone()
    conn.close()
    return student

def get_students_by_last_name(last_name):
    """
    Search for all students with a matching last name.
    
    This function provides case-insensitive last name search and returns
    all matching students with their complete equipment assignments.
    Useful for finding family members or when only last name is known.
    
    Args:
        last_name (str): The last name to search for (case-insensitive)
        
    Returns:
        list of tuples: Each tuple contains complete student record:
        - Basic Info: ID, name, status, section
        - Contact: phone, email, guardian details
        - Uniform: Component numbers if assigned
        - Instrument: Current assignment if any
        
    Note:
        - Uses SQLite's COLLATE NOCASE for case-insensitive matching
        - Returns multiple records if multiple students share last name
        - Includes equipment info only for current assignments
        - Returns empty list if no matches found
    """
    conn, cursor = connect_db()
    cursor.execute("""
        SELECT s.student_id, s.first_name, s.last_name, s.status,
               s.phone, s.email, s.guardian_name, s.guardian_phone,
               s.year_came_up, s.section,
               u.shako_num, u.hanger_num, u.garment_bag, u.coat_num, u.pants_num,
               i.instrument_name, i.instrument_serial, i.instrument_case
        FROM students s
        LEFT JOIN uniforms u 
               ON s.student_id = u.student_id 
              AND u.status = 'Assigned'
        LEFT JOIN instruments i 
               ON s.student_id = i.student_id 
              AND i.status = 'Assigned'
        WHERE s.last_name = ? COLLATE NOCASE
    """, (last_name,))
    students = cursor.fetchall()
    conn.close()
    return students

def get_students_by_section(section):
    """
    Retrieve all students in a specific band/group section.
    
    This function is crucial for section leaders and instructors to manage
    their groups. It returns all students in a section along with their
    current equipment assignments. Sections are predefined in the schema
    (e.g., 'Trumpet', 'Flags', 'Percussion', etc.)
    
    Args:
        section (str): The section name to filter by (case-sensitive)
                      Must match one of the predefined section values
        
    Returns:
        list of tuples: Each tuple contains:
        - Student Info: ID, name, status, section (will match input)
        - Contact Details: For both student and guardian
        - Uniform Components: Current assignments if any
        - Instrument Info: Current assignment details
        
    Usage:
        - Section roster management
        - Equipment inventory by section
        - Contact lists for section leaders
        - Uniform/instrument distribution planning
    
    Note:
        Only returns active assignments (status = 'Assigned')
        Empty list if section has no students
    """
    conn, cursor = connect_db()
    cursor.execute("""
        SELECT s.student_id, s.first_name, s.last_name, s.status,
               s.phone, s.email, s.guardian_name, s.guardian_phone,
               s.year_came_up, s.section,
               u.shako_num, u.hanger_num, u.garment_bag, u.coat_num, u.pants_num,
               i.instrument_name, i.instrument_serial, i.instrument_case
        FROM students s
        LEFT JOIN uniforms u 
               ON s.student_id = u.student_id 
              AND u.status = 'Assigned'
        LEFT JOIN instruments i 
               ON s.student_id = i.student_id 
              AND i.status = 'Assigned'
        WHERE s.section = ?
    """, (section,))
    students = cursor.fetchall()
    conn.close()
    return students

def get_students_with_uniforms_and_instruments():
    """
    Generate a complete roster report with all student and equipment details.
    
    This function creates a comprehensive report suitable for:
    - Beginning/end of year inventory
    - Equipment audits
    - Administrative reviews
    - Parent/student equipment agreements
    
    Returns:
        tuple: (rows, headers)
        - rows: List of tuples containing all student and equipment data
        - headers: List of column names for report formatting
        
    Data Categories:
    1. Student Information:
       - Identification (ID, names)
       - Status and section
       - Contact details
    2. Uniform Components:
       - All numbered pieces
       - Storage items (hanger, garment bag)
    3. Instrument Details:
       - Name/type
       - Serial number
       - Case identifier
       
    Note:
        - Only shows current ('Assigned') equipment
        - Sorted by last name then first name
        - Includes header labels for report generation
        - LEFT JOINs ensure all students appear, with or without equipment
    """
    conn, cursor = connect_db()
    cursor.execute("""
        WITH student_instruments AS (
            SELECT student_id,
                   GROUP_CONCAT(instrument_name || ' (' || COALESCE(instrument_serial,'') || ')' || 
                              CASE WHEN instrument_case IS NOT NULL THEN ' [' || instrument_case || ']' ELSE '' END) as instruments
            FROM instruments 
            WHERE status = 'Assigned'
            GROUP BY student_id
        )
        SELECT s.student_id, s.first_name, s.last_name, s.status,
               s.phone, s.email, s.guardian_name, s.guardian_phone,
               s.year_came_up, s.section,
               u.shako_num, u.hanger_num, u.coat_num, u.pants_num, u.garment_bag,
               COALESCE(si.instruments, '') as instruments
        FROM students s
        LEFT JOIN uniforms u 
               ON s.student_id = u.student_id AND u.status = 'Assigned'
        LEFT JOIN student_instruments si
               ON s.student_id = si.student_id
        ORDER BY s.last_name, s.first_name
    """)
    rows = cursor.fetchall()
    conn.close()

    headers = [
        "Student ID", "First Name", "Last Name", "Status",
        "Phone", "Email", "Guardian Name", "Guardian Phone",
        "Year Joined", "Section",
        "Shako #", "Hanger #", "Coat #", "Pants #", "Garment Bag",
        "Instrument"
    ]
    return rows, headers

def get_students():
    """
    Retrieve all student records from the database.
    
    This is a simple utility function that returns every student record
    without any equipment information. Useful for:
    - Basic roster management
    - Quick student lookups
    - Data export/backup
    - Bulk operations planning
    
    Returns:
        list of tuples: Raw student records containing:
        - student_id: Unique identifier
        - first_name: Student's first name
        - last_name: Student's last name
        - phone: Contact number
        - email: Email address
        - year_came_up: Year joined
        - status: Current status (Student/Former/Alumni)
        - guardian_name: Parent/guardian name
        - guardian_phone: Parent/guardian contact
        - section: Band/group section
        
    Note:
        For equipment information, use get_students_with_uniforms_and_instruments()
        instead of this basic query.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return students

def add_student(
    student_id, first_name, last_name, phone, email, year_came_up,
    status, guardian_name, guardian_phone, section,
    shako_num=None, hanger_num=None, garment_bag=None,
    coat_num=None, pants_num=None,
    instrument_name=None, instrument_serial=None, instrument_case=None
):
    """
    Create a new student record with optional equipment assignments.
    
    This function handles the complete student enrollment process:
    1. Creates the basic student record
    2. Optionally assigns uniform components if provided
    3. Optionally assigns an instrument if details provided
    
    Args:
        Required Student Info:
        - student_id (str): Unique identifier
        - first_name (str): Student's first name
        - last_name (str): Student's last name
        - phone (str): Contact number
        - email (str): Email address
        - year_came_up (str): Year joined
        - status (str): Must be 'Student', 'Former', or 'Alumni'
        - guardian_name (str): Parent/guardian name
        - guardian_phone (str): Parent/guardian contact
        - section (str): Must match predefined sections
        
        Optional Equipment (all default to None):
        Uniform Components:
        - shako_num (int): Hat number
        - hanger_num (int): Uniform hanger ID
        - garment_bag (str): Garment bag ID
        - coat_num (int): Coat number
        - pants_num (int): Pants number
        
        Instrument Details:
        - instrument_name (str): Type of instrument
        - instrument_serial (str): Serial number
        - instrument_case (str): Case identifier
    
    Note:
        - All equipment numbers must exist in inventory
        - Status constraints enforced by schema
        - Section must be valid per schema
        - Transaction ensures all or nothing completes
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
                student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num,
            "Assigned" if student_id else "Available"
        ))

    # Add instrument assignment if any instrument fields are provided
    if any(x not in (None, "") for x in [instrument_name, instrument_serial, instrument_case]):
        cursor.execute('''
            INSERT INTO instruments (
                student_id, instrument_name, instrument_serial, instrument_case, status
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            student_id, instrument_name, instrument_serial, instrument_case,
            "Assigned" if student_id else "Available"
        ))

    conn.commit()
    conn.close()

def add_or_update_student(student_id, first_name, last_name, status, section,
                          phone, email, guardian_name, guardian_phone, year_came_up):
    """
    Create or update a student record using an UPSERT operation.
    
    This function uses SQLite's INSERT OR REPLACE functionality to:
    1. Create a new student record if the ID doesn't exist
    2. Update all fields if the student ID already exists
    
    This is particularly useful for:
    - Batch imports from external systems
    - Mass updates of student information
    - Conflict-free data synchronization
    
    Args:
        student_id (str): Primary key - determines create vs update
        first_name (str): Student's first name
        last_name (str): Student's last name
        status (str): Must be 'Student', 'Former', or 'Alumni'
        section (str): Must match predefined sections
        phone (str): Student's contact number
        email (str): Student's email address
        guardian_name (str): Parent/guardian name
        guardian_phone (str): Parent/guardian contact
        year_came_up (str): Year student joined
    
    Note:
        - Does NOT handle equipment assignments
        - Use add_student() for new students needing equipment
        - All fields are required (no optional parameters)
        - Validates section and status via schema constraints
    """
    conn, cursor = connect_db()
    cursor.execute("""
        INSERT INTO students (student_id, first_name, last_name, status, section,
                              phone, email, guardian_name, guardian_phone, year_came_up)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(student_id) DO UPDATE SET
            first_name=excluded.first_name,
            last_name=excluded.last_name,
            status=excluded.status,
            section=excluded.section,
            phone=excluded.phone,
            email=excluded.email,
            guardian_name=excluded.guardian_name,
            guardian_phone=excluded.guardian_phone,
            year_came_up=excluded.year_came_up
    """, (student_id, first_name, last_name, status, section,
          phone, email, guardian_name, guardian_phone, year_came_up))
    conn.commit()
    conn.close()

def update_student(student_id, field, new_value):
    """
    Update a single field in a student's record with validation.
    
    This function provides targeted updates to student records with
    built-in validation for data integrity. It's designed for:
    - Single field updates via the UI
    - Quick corrections to student data
    - Enforcing data validation rules
    
    Args:
        student_id (str): The student's unique identifier
        field (str): The field to update. Must be one of:
            - first_name: Student's first name
            - last_name: Student's last name
            - phone: Contact number (length validated)
            - email: Email address
            - year_came_up: Year joined
            - status: Must be Student/Former/Alumni
            - guardian_name: Parent/guardian name
            - guardian_phone: Parent/guardian contact (length validated)
            - section: Must be valid band section
            
        new_value (str): The new value to set for the field
    
    Raises:
        ValueError: If field is invalid or new_value fails validation
        
    Validation Rules:
    - Phone numbers: Length and format checked
    - Status: Must be Student, Former, or Alumni
    - Section: Must be one of the predefined band sections
    - Other fields: Basic presence validation
    
    Note:
        This is for single field updates only. For updating multiple
        fields, use add_or_update_student() instead.
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
    Remove a student from the system and properly handle all equipment.
    
    This function performs a complete student removal process:
    1. Verifies student exists
    2. Unassigns all equipment pieces:
       - Uniform components (shako, coat, pants, garment bag)
       - Complete uniform sets
       - Instruments
    3. Marks all equipment as 'Available'
    4. Deletes the student record
    
    Args:
        student_id (str): The ID of the student to remove
        
    Process:
    1. Equipment Release:
       - Updates all equipment tables
       - Clears student_id references
       - Changes status to 'Available'
       
    2. Data Integrity:
       - Uses transactions for all-or-nothing completion
       - Maintains referential integrity
       - Preserves equipment records for reuse
       
    3. Error Handling:
       - Validates student existence
       - Reports errors without partial deletions
       - Rolls back on failure
    
    Note:
        This is a permanent deletion. For temporary removal,
        consider updating student status to 'Former' instead.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT 1 FROM students WHERE student_id = ?", (student_id,))
    if cursor.fetchone() is None:
        print("Error: Student ID not found.")
        conn.close()
        return

    # Before deleting the student, unassign any related equipment:
    try:
        # Unassign uniforms
        cursor.execute("""
            UPDATE uniforms
               SET student_id = NULL,
                   status = 'Available'
             WHERE student_id = ?
        """, (student_id,))

        # Unassign instruments
        cursor.execute("""
            UPDATE instruments
               SET student_id = NULL,
                   status = 'Available'
             WHERE student_id = ?
        """, (student_id,))

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
# This section contains all functions for managing uniform components and
# complete uniform sets. Key features include:
#
# - Individual component tracking (shakos, coats, pants, garment bags)
# - Complete uniform set management
# - Status tracking across all pieces
# - Assignment and return processing
# - Inventory management
# - Maintenance tracking
# ------------------------------------------------------------------------------

def get_all_shakos():
    """
    Retrieve a complete inventory list of all marching band shakos/hats.
    
    This function returns all shako records sorted by number for easy
    inventory management and status checking. Useful for:
    - Annual inventory counts
    - Finding available shakos
    - Maintenance scheduling
    - Assignment planning
    
    Returns:
        list of tuples: Each tuple contains:
        - id (int): Internal database ID
        - shako_num (int): Visible shako number
        - status (str): Current state (Available/Assigned/Maintenance/Retired)
        - student_id (str): ID of assigned student, or NULL
        - notes (str): Condition and maintenance notes
        
    Note:
        Results are ordered by shako_num for easy reference
        during physical inventory checks.
    """
    conn, cursor = connect_db()
    # Order by shako number for easy inventory matching
    cursor.execute("SELECT id, shako_num, status, student_id, notes FROM shakos ORDER BY shako_num")
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_coats():
    """
    Retrieve a complete inventory of all uniform coats/jackets.
    
    Returns all coat records sorted by number, including their
    assigned hangers and current status. Essential for:
    - Uniform room organization
    - Hanger tracking
    - Assignment management
    - Maintenance scheduling
    
    Returns:
        list of tuples: Each tuple contains:
        - id (int): Internal database ID
        - coat_num (int): Visible coat number
        - hanger_num (int): Associated storage hanger
        - status (str): Current state (Available/Assigned/Maintenance/Retired)
        - student_id (str): ID of assigned student, or NULL
        - notes (str): Size, condition, and maintenance notes
        
    Note:
        Results are ordered by coat_num for easy reference
        when working in the uniform storage area.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT id, coat_num, hanger_num, status, student_id, notes FROM coats ORDER BY coat_num")
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_pants():
    """
    Retrieve a complete inventory of all uniform pants/trousers.
    
    Lists all pants records ordered by number for efficient:
    - Inventory management
    - Size tracking
    - Assignment planning
    - Maintenance scheduling
    
    Returns:
        list of tuples: Each tuple contains:
        - id (int): Internal database ID
        - pants_num (int): Visible pants number
        - status (str): Current state (Available/Assigned/Maintenance/Retired)
        - student_id (str): ID of assigned student, or NULL
        - notes (str): Size, condition, and maintenance notes
        
    Note:
        Ordered by pants_num for easy matching with
        physical inventory and efficient assignment process.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT id, pants_num, status, student_id, notes FROM pants ORDER BY pants_num")
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_garment_bags():
    """
    Retrieve a complete inventory of all uniform garment bags.
    
    Lists all storage bags that protect uniforms when not in use.
    Critical for:
    - Uniform protection tracking
    - Student accountability
    - Loss prevention
    - Storage management
    
    Returns:
        list of tuples: Each tuple contains:
        - id (int): Internal database ID
        - bag_num (str): Bag identifier number/code
        - status (str): Current state (Available/Assigned/Maintenance/Retired)
        - student_id (str): ID of assigned student, or NULL
        - notes (str): Condition and maintenance notes
        
    Note:
        Results ordered by bag_num for easy visual matching
        during uniform distribution and collection.
        Garment bags are essential for proper uniform care
        and longevity.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT id, bag_num, status, student_id, notes FROM garment_bags ORDER BY bag_num")
    results = cursor.fetchall()
    conn.close()
    return results

def get_students_with_outstanding_uniforms():
    """
    Retrieve a list of all students with currently assigned uniforms.
    
    This function performs a complex join to match students with their
    current uniform assignments. It's crucial for:
    - End-of-season uniform collection
    - Inventory audits
    - Student accountability tracking
    - Lost uniform prevention
    
    Returns:
        list of tuples: Each tuple contains:
        - first_name (str): Student's first name
        - last_name (str): Student's last name
        - shako_num (int): Assigned hat number
        - hanger_num (int): Assigned hanger number
        - garment_bag (str): Assigned bag ID
        - coat_num (int): Assigned coat number
        - pants_num (int): Assigned pants number
    
    Note:
        - Only shows 'Assigned' status uniforms
        - Uses subquery to get only the most recent assignment
          if a student has multiple uniform records
        - Joined with students table to get current names
    """
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT s.first_name, s.last_name,
               u.shako_num, u.hanger_num, u.garment_bag, u.coat_num, u.pants_num
        FROM students s
        JOIN uniforms u ON s.student_id = u.student_id
        WHERE u.status = 'Assigned'
          AND u.id = (
              SELECT MAX(id) FROM uniforms
              WHERE student_id = s.student_id AND status = 'Assigned'
          )
    ''')
    results = cursor.fetchall()
    conn.close()
    return results

def get_students_with_outstanding_uniforms_by_section(section):
    """
    List all students in a specific section with assigned uniforms.
    
    Similar to get_students_with_outstanding_uniforms() but filters
    by section. Essential for:
    - Section-specific uniform collection
    - Section leader inventory management
    - Targeted uniform audits
    - Section-based accountability
    
    Args:
        section (str): Band section to filter by (e.g., 'Trumpet', 'Flags')
                      Must match predefined section values
    
    Returns:
        list of tuples: Each tuple contains:
        - first_name (str): Student's first name
        - last_name (str): Student's last name
        - shako_num (int): Assigned hat number
        - hanger_num (int): Assigned hanger number
        - garment_bag (str): Assigned bag ID
        - coat_num (int): Assigned coat number
        - pants_num (int): Assigned pants number
        
    Note:
        - Filters on student's assigned section
        - Only shows current assignments (status = 'Assigned')
        - Handles case where section has no uniforms out
    """
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT s.first_name, s.last_name,
               u.shako_num, u.hanger_num, u.garment_bag, u.coat_num, u.pants_num
        FROM students s
        JOIN uniforms u ON s.student_id = u.student_id
        WHERE u.status = 'Assigned'
          AND s.section = ?
          AND u.id = (
              SELECT MAX(id) FROM uniforms
              WHERE student_id = s.student_id AND status = 'Assigned'
          )
    ''', (section,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_uniform_id_by_student(student_id):
    """
    Find the database ID of a student's assigned uniform.
    
    Quick lookup function to get the internal uniform record ID
    for a specific student. Used for:
    - Record updates
    - Assignment verification
    - Database integrity checks
    
    Args:
        student_id (str): Student's unique identifier
        
    Returns:
        int or None: Database ID of the uniform record if found,
                    None if student has no uniform assigned
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT id FROM uniforms WHERE student_id=?", (student_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_uniforms():
    """
    Retrieve all uniform records with prioritized status ordering.
    
    Provides a complete view of the uniform inventory sorted by
    status priority and ID. Essential for:
    - Complete inventory audits
    - Maintenance scheduling
    - Assignment planning
    - Uniform room organization
    
    Returns:
        list of tuples: Each tuple contains:
        - id (int): Database record ID
        - student_id (str): Assigned student's ID or NULL
        - shako_num (int): Hat number
        - hanger_num (int): Storage hanger number
        - garment_bag (str): Garment bag identifier
        - coat_num (int): Coat number
        - pants_num (int): Pants number
        - status (str): Current state with priority ordering:
            1. Assigned - Currently with students
            2. Available - Ready for assignment
            3. Maintenance - Under repair/cleaning
            4. Retired - Out of service
        - notes (str): Condition and history notes
        
    Note:
        Status ordering helps prioritize attention to
        active assignments and available uniforms first.
    """
    conn, cursor = connect_db()
    cursor.execute("""
        SELECT id, student_id, shako_num, hanger_num, garment_bag,
               coat_num, pants_num, status, notes
        FROM uniforms
        ORDER BY 
            CASE status 
                WHEN 'Assigned'   THEN 1
                WHEN 'Available'  THEN 2
                WHEN 'Maintenance' THEN 3
                WHEN 'Retired'    THEN 4
            END,
            id
    """)
    results = cursor.fetchall()
    conn.close()
    return results

def find_shako_by_number(shako_num):
    """
    Look up a specific shako/hat by its identifying number.
    
    Quick lookup function for finding details about a specific
    shako during:
    - Assignment process
    - Returns processing
    - Maintenance tracking
    - Lost item verification
    
    Args:
        shako_num (int): The visible number on the shako
        
    Returns:
        tuple or None: If found, returns:
        - id (int): Database record ID
        - shako_num (int): Matching shako number
        - status (str): Current status
        - student_id (str): Assigned student's ID or NULL
        - notes (str): Condition and maintenance notes
        Returns None if no shako matches the number
        
    Note:
        Shako numbers are unique across the inventory
        for precise tracking of each hat.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT id, shako_num, status, student_id, notes FROM shakos WHERE shako_num = ?", (shako_num,))
    res = cursor.fetchone()
    conn.close()
    return res

def find_coat_by_number(coat_num):
    """
    Look up a specific uniform coat by its number.
    
    Retrieves complete details for a coat, including its
    storage hanger assignment. Used during:
    - Uniform assignments
    - Returns processing
    - Inventory verification
    - Storage management
    
    Args:
        coat_num (int): The identifying number on the coat
        
    Returns:
        tuple or None: If found, returns:
        - id (int): Database record ID
        - coat_num (int): Matching coat number
        - hanger_num (int): Storage hanger identifier
        - status (str): Current status
        - student_id (str): Assigned student's ID or NULL
        - notes (str): Size, condition, and maintenance notes
        Returns None if no coat matches the number
        
    Note:
        Includes hanger number for accurate storage location
        tracking in the uniform room.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT id, coat_num, hanger_num, status, student_id, notes FROM coats WHERE coat_num = ?", (coat_num,))
    res = cursor.fetchone()
    conn.close()
    return res

def find_pants_by_number(pants_num):
    """
    Look up specific uniform pants by their number.
    
    Quick lookup for individual pants tracking during:
    - Uniform fitting sessions
    - Returns processing
    - Inventory counts
    - Size matching
    
    Args:
        pants_num (int): The identifying number on the pants
        
    Returns:
        tuple or None: If found, returns:
        - id (int): Database record ID
        - pants_num (int): Matching pants number
        - status (str): Current status
        - student_id (str): Assigned student's ID or NULL
        - notes (str): Size, condition, and maintenance notes
        Returns None if no pants match the number
        
    Note:
        Notes field often contains waist and length
        measurements for size matching.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT id, pants_num, status, student_id, notes FROM pants WHERE pants_num = ?", (pants_num,))
    res = cursor.fetchone()
    conn.close()
    return res

def find_bag_by_number(bag_num):
    """
    Look up a specific garment bag by its identifier.
    
    Used to track protective uniform storage bags during:
    - Initial uniform distribution
    - Returns collection
    - Lost bag tracking
    - Condition assessment
    
    Args:
        bag_num (str): The identifier on the garment bag
        
    Returns:
        tuple or None: If found, returns:
        - id (int): Database record ID
        - bag_num (str): Matching bag identifier
        - status (str): Current status
        - student_id (str): Assigned student's ID or NULL
        - notes (str): Condition and repair notes
        Returns None if no bag matches the number
        
    Note:
        Garment bags are critical for uniform protection
        and proper storage between performances.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT id, bag_num, status, student_id, notes FROM garment_bags WHERE bag_num = ?", (bag_num,))
    res = cursor.fetchone()
    conn.close()
    return res

def return_uniform_piece(student_id):
    """
    Process the return of all uniform components from a student.
    
    This function handles the complete uniform return process:
    1. Locates all assigned uniform pieces
    2. Updates individual component status to 'Available'
    3. Removes the composite uniform record
    4. Maintains the component history
    
    Args:
        student_id (str): ID of student returning uniform
        
    Process Steps:
    1. Query assigned uniform components
    2. Update status in component tables:
       - shakos
       - coats (and hangers)
       - pants
       - garment bags
    3. Clear student_id assignments
    4. Remove unified uniform record
    
    Note:
        - All components are marked 'Available' for reassignment
        - Individual pieces maintain their condition/notes
        - Transaction ensures all updates complete together
        - Component history is preserved for tracking
    """
    conn, cursor = connect_db()
    cursor.execute("""
        SELECT id, shako_num, coat_num, pants_num, garment_bag, hanger_num
        FROM uniforms
        WHERE student_id = ?
    """, (student_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return  # no assignments to clear

    uniform_id, shako_num, coat_num, pants_num, bag_num, hanger_num = row

    # Delete the student's row from uniforms
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM uniforms WHERE id = ?", (uniform_id,))
    conn.commit()
    conn.close()

    # Free up inventory items
    if shako_num:
        update_shako(shako_num, student_id=None, status="Available")
    if coat_num:
        update_coat(coat_num, student_id=None, status="Available", hanger_num=None)
    if pants_num:
        update_pants(pants_num, student_id=None, status="Available")
    if bag_num:
        update_bag(bag_num, student_id=None, status="Available")

'''
def assign_shako_to_student(shako_num, student_id):
    """
    Assign a specific shako (hat) to a student.
    
    Updates the shako's status and ownership in one operation.
    Used during:
    - Initial uniform distribution
    - Replacement of lost/damaged items
    - Mid-season reassignments
    
    Args:
        shako_num (int): The number of the shako to assign
        student_id (str): ID of student receiving the shako
        
    Effects:
        - Sets status to 'Assigned'
        - Links shako to student via student_id
        - Maintains assignment history
        
    Note:
        Assumes shako exists and is available for assignment.
        For bulk assignments, use the unified uniform assignment
        functions instead.
    """
    conn, cursor = connect_db()
    cursor.execute("UPDATE shakos SET status='Assigned', student_id=? WHERE shako_num=?",
                   (student_id, shako_num))
    conn.commit()
    conn.close()

def assign_coat_to_student(coat_num, student_id):
    """
    Assign a specific uniform coat to a student.
    
    Updates a coat's assignment status and ownership.
    Critical for:
    - Individual coat assignments
    - Replacement issuance
    - Size adjustments
    - Uniform modifications
    
    Args:
        coat_num (int): The number of the coat to assign
        student_id (str): ID of student receiving the coat
        
    Effects:
        - Updates status to 'Assigned'
        - Associates coat with student
        - Maintains assignment record
        
    Note:
        For complete uniform assignments including coat,
        prefer using the unified uniform assignment
        functions instead of this individual piece
        assignment.
    """
    conn, cursor = connect_db()
    cursor.execute("UPDATE coats SET status='Assigned', student_id=? WHERE coat_num=?",
                   (student_id, coat_num))
    conn.commit()
    conn.close()

def assign_pants_to_student(pants_num, student_id):
    """
    Assign specific uniform pants to a student.
    
    Updates pants assignment status and student ownership.
    Used for:
    - Individual pants assignments
    - Size adjustments
    - Replacement of damaged pieces
    - Uniform modifications
    
    Args:
        pants_num (int): The number of the pants to assign
        student_id (str): ID of student receiving the pants
        
    Effects:
        - Sets status to 'Assigned'
        - Links pants to student
        - Records assignment in database
        
    Note:
        For full uniform assignments, use the unified
        uniform assignment functions rather than this
        individual piece assignment. This function is
        primarily for replacement or adjustment purposes.
    """
    conn, cursor = connect_db()
    cursor.execute("UPDATE pants SET status='Assigned', student_id=? WHERE pants_num=?",
                   (student_id, pants_num))
    conn.commit()
    conn.close()

def assign_bag_to_student(bag_num, student_id):
    """
    Assign a specific garment bag to a student.
    
    Updates a garment bag's assignment and links it to a student.
    Important for:
    - Uniform protection tracking
    - Student accountability
    - Replacement assignments
    - Lost bag handling
    
    Args:
        bag_num (str): The identifier of the bag to assign
        student_id (str): ID of student receiving the bag
        
    Effects:
        - Updates status to 'Assigned'
        - Links bag to student
        - Maintains assignment record
        
    Note:
        Garment bags are critical for uniform protection.
        For complete uniform assignments, use the unified
        assignment functions instead of this individual
        piece assignment.
    """
    conn, cursor = connect_db()
    cursor.execute("UPDATE garment_bags SET status='Assigned', student_id=? WHERE bag_num=?",
                   (student_id, bag_num))
    conn.commit()
    conn.close()
'''
def assign_uniform_piece(student_id, **pieces):
    """
    Assign or update multiple uniform components for a student.
    
    This is a flexible uniform assignment function that:
    1. Creates or updates a student's uniform record
    2. Handles any combination of uniform pieces
    3. Maintains consistency across all inventory tables
    
    Args:
        student_id (str): ID of student receiving pieces
        **pieces: Keyword arguments for uniform components:
            - shako_num (int): Hat number
            - hanger_num (int): Hanger identifier
            - garment_bag (str): Bag identifier
            - coat_num (int): Coat number
            - pants_num (int): Pants number
            
    Process:
    1. Finds or creates uniform record for student
    2. Updates provided pieces in unified record
    3. Syncs individual inventory tables
    4. Ensures consistent 'Assigned' status
    
    Note:
        - Creates new uniform record if none exists
        - Updates only provided pieces
        - Maintains existing assignments for unspecified pieces
        - Handles partial uniform assignments
    """
    uniform_id = get_uniform_id_by_student(student_id)

    # If no row exists yet, create an empty one for this student
    if not uniform_id:
        conn, cursor = connect_db()
        cursor.execute("""
            INSERT INTO uniforms (student_id, status)
            VALUES (?, ?)
        """, (student_id, "Available"))
        conn.commit()
        conn.close()
        uniform_id = get_uniform_id_by_student(student_id)

    # Always enforce status = Assigned if we’re giving them pieces
    pieces["status"] = "Assigned"
    pieces["student_id"] = student_id

    # Build dynamic SET clause
    set_clause = ", ".join(f"{col} = ?" for col in pieces.keys())
    values = list(pieces.values()) + [uniform_id]

    conn, cursor = connect_db()
    cursor.execute(f"UPDATE uniforms SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()

    # Auto-sync inventory tables
    if "shako_num" in pieces and pieces["shako_num"] is not None:
        update_shako(pieces["shako_num"], student_id=student_id, status="Assigned")
    if "coat_num" in pieces and pieces["coat_num"] is not None:
        update_coat(pieces["coat_num"], student_id=student_id, status="Assigned",
                    hanger_num=pieces.get("hanger_num"))
    if "pants_num" in pieces and pieces["pants_num"] is not None:
        update_pants(pieces["pants_num"], student_id=student_id, status="Assigned")
    if "garment_bag" in pieces and pieces["garment_bag"]:
        update_bag(pieces["garment_bag"], student_id=student_id, status="Assigned")

def is_shako_available(shako_num):
    """
    Check if a specific shako is available for assignment.
    
    Quick validation function used during:
    - New uniform assignments
    - Uniform exchanges
    - Availability checks
    - Inventory planning
    
    Args:
        shako_num (int): The number of the shako to check
        
    Returns:
        bool: True if shako exists and status is 'Available'
              False if not found or status is anything else
              
    Note:
        'Available' status means:
        - Not currently assigned
        - Not in maintenance
        - Not retired
        - Ready for immediate assignment
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT status FROM shakos WHERE shako_num = ?", (shako_num,))
    r = cursor.fetchone()
    conn.close()
    return (r is not None) and (r[0] == 'Available')

def is_coat_available(coat_num):
    """
    Check if a specific uniform coat is available for assignment.
    
    Validation function used during:
    - Uniform assignments
    - Size exchanges
    - Inventory checks
    - Assignment planning
    
    Args:
        coat_num (int): The number of the coat to check
        
    Returns:
        bool: True if coat exists and status is 'Available'
              False if not found or has another status
              
    Note:
        Only returns True if coat is ready for immediate
        assignment (status = 'Available'). Any other status
        (Assigned, Maintenance, Retired) returns False.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT status FROM coats WHERE coat_num = ?", (coat_num,))
    r = cursor.fetchone()
    conn.close()
    return (r is not None) and (r[0] == 'Available')

def is_pants_available(pants_num):
    """
    Check if specific uniform pants are available for assignment.
    
    Validation function used during:
    - Initial uniform assignments
    - Size adjustments
    - Inventory management
    - Assignment planning
    
    Args:
        pants_num (int): The number of the pants to check
        
    Returns:
        bool: True if pants exist and status is 'Available'
              False if not found or status is different
              
    Note:
        Verifies both existence and 'Available' status.
        Used before attempting assignments to prevent
        conflicts or double-assignments.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT status FROM pants WHERE pants_num = ?", (pants_num,))
    r = cursor.fetchone()
    conn.close()
    return (r is not None) and (r[0] == 'Available')

def is_bag_available(bag_num):
    """
    Check if a specific garment bag is available for assignment.
    
    Validation function used for:
    - New uniform assignments
    - Bag replacements
    - Storage planning
    - Inventory checks
    
    Args:
        bag_num (str): The identifier of the bag to check
        
    Returns:
        bool: True if bag exists and status is 'Available'
              False if not found or has different status
              
    Note:
        Garment bags are essential for uniform protection.
        This check ensures bags aren't double-assigned and
        are ready for immediate use.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT status FROM garment_bags WHERE bag_num = ?", (bag_num,))
    r = cursor.fetchone()
    conn.close()
    return (r is not None) and (r[0] == 'Available')

def update_shako(shako_num, student_id=None, status=None, notes=None):
    """
    Update the assignment, status, and/or notes for a specific shako.
    
    This function provides flexible updating of shako records by allowing
    partial updates of specific fields. The student_id will always be
    updated (can be set to NULL by passing None), while status and notes
    are only updated if explicitly provided.
    
    Common Use Cases:
    - Assigning/unassigning shakos to students
    - Updating maintenance status
    - Adding condition notes
    - Tracking repairs or replacements
    
    Args:
        shako_num (str): The unique identifier of the shako to update
        student_id (int, optional): The ID of student to assign shako to, 
            or None to unassign
        status (str, optional): New status for the shako 
            (e.g., 'Available', 'Assigned', 'Maintenance')
        notes (str, optional): Additional notes about condition, 
            repairs, or other relevant information
    
    Note:
        - The student_id field is always updated, even if None
        - Status and notes are only updated if not None
        - Updates are atomic - either all specified fields are updated
          or none are
    """
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
    """
    Update the assignment, status, hanger number, and/or notes for a specific coat.
    
    This function provides flexible updating of coat records by allowing
    partial updates of specific fields. The student_id will always be
    updated (can be set to NULL by passing None), while status, hanger_num,
    and notes are only updated if explicitly provided.
    
    Common Use Cases:
    - Assigning/unassigning coats to students
    - Updating maintenance status
    - Changing hanger assignments
    - Recording condition notes
    - Tracking repairs or replacements
    
    Args:
        coat_num (str): The unique identifier of the coat to update
        student_id (int, optional): The ID of student to assign coat to, 
            or None to unassign
        status (str, optional): New status for the coat 
            (e.g., 'Available', 'Assigned', 'Maintenance')
        hanger_num (str, optional): The identifier of the hanger 
            assigned to this coat
        notes (str, optional): Additional notes about condition, 
            repairs, or other relevant information
    
    Note:
        - The student_id field is always updated, even if None
        - Status, hanger_num, and notes are only updated if not None
        - Updates are atomic - either all specified fields are updated
          or none are
        - Proper hanger assignment helps with uniform organization and
          preservation
    """
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
    """
    Update the assignment, status, and/or notes for a specific pair of pants.
    
    This function provides flexible updating of pants records by allowing
    partial updates of specific fields. The student_id will always be
    updated (can be set to NULL by passing None), while status and notes
    are only updated if explicitly provided.
    
    Common Use Cases:
    - Assigning/unassigning pants to students
    - Updating maintenance status
    - Recording alterations
    - Tracking repairs or replacements
    - Documenting fit adjustments
    
    Args:
        pants_num (str): The unique identifier of the pants to update
        student_id (int, optional): The ID of student to assign pants to, 
            or None to unassign
        status (str, optional): New status for the pants 
            (e.g., 'Available', 'Assigned', 'Maintenance', 'Alteration')
        notes (str, optional): Additional notes about condition, 
            alterations, repairs, or other relevant information
    
    Note:
        - The student_id field is always updated, even if None
        - Status and notes are only updated if not None
        - Updates are atomic - either all specified fields are updated
          or none are
        - Notes field is particularly important for tracking alterations
          and fit adjustments
    """
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
    """
    Update the assignment, status, and/or notes for a specific garment bag.
    
    This function provides flexible updating of garment bag records by allowing
    partial updates of specific fields. The student_id will always be
    updated (can be set to NULL by passing None), while status and notes
    are only updated if explicitly provided.
    
    Common Use Cases:
    - Assigning/unassigning bags to students
    - Updating bag condition status
    - Recording damage or repairs
    - Tracking bag replacements
    - Documenting special storage requirements
    
    Args:
        bag_num (str): The unique identifier of the garment bag to update
        student_id (int, optional): The ID of student to assign bag to, 
            or None to unassign
        status (str, optional): New status for the bag 
            (e.g., 'Available', 'Assigned', 'Damaged', 'Replacement Needed')
        notes (str, optional): Additional notes about condition, 
            repairs, or other relevant information
    
    Note:
        - The student_id field is always updated, even if None
        - Status and notes are only updated if not None
        - Updates are atomic - either all specified fields are updated
          or none are
        - Proper garment bag maintenance is crucial for uniform protection
          and longevity
    """
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

def add_uniform(id, student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num,
                status=None, notes=None):
    """
    Manually insert a complete uniform record into the database.
    
    This function is primarily used for administrative purposes or during
    data migration. It creates a new uniform record with all its component
    parts (shako, coat, pants, garment bag, and hanger) as a single unit.
    
    Administrative Uses:
    - Initial uniform inventory setup
    - Data migration from legacy systems
    - Batch uniform imports
    - Manual record corrections
    - Historical record restoration
    
    Args:
        id (int): Unique identifier for the uniform record
        student_id (int, optional): ID of student assigned to uniform
        shako_num (str): Identifier for the shako component
        hanger_num (str): Identifier for the hanger
        garment_bag (str): Identifier for the garment bag
        coat_num (str): Identifier for the coat
        pants_num (str): Identifier for the pants
        status (str, optional): Status of the uniform set
            (defaults to "Assigned" if student_id present, else "Available")
        notes (str, optional): Additional notes about the uniform set
    
    Note:
        - This is a low-level function that bypasses normal assignment logic
        - Use with caution as it does not perform availability checks
        - Primarily intended for administrative use
        - Does not update individual component records automatically
    """
    conn, cursor = connect_db()

    # Normalize
    student_id = None if not student_id else student_id
    status = status or ("Assigned" if student_id else "Available")

    cursor.execute('''
        INSERT INTO uniforms (
            id, student_id, shako_num, hanger_num, garment_bag,
            coat_num, pants_num, status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        id, student_id, shako_num, hanger_num, garment_bag,
        coat_num, pants_num, status, notes
    ))

    conn.commit()
    conn.close()

def add_or_update_uniform(
    id=None,
    student_id=None,
    shako_num=None,
    hanger_num=None,
    garment_bag=None,
    coat_num=None,
    pants_num=None,
    status=None,
    notes=None
):
    """
    Create a new uniform record or update an existing one.
    
    This is the primary function for managing uniform records in the system.
    It handles both creation of new uniforms and updates to existing ones
    with intelligent handling of partial updates and status management.
    
    Key Features:
    - Automatic status management based on student assignment
    - Flexible partial updates
    - Intelligent record lookup
    - Data normalization
    - Atomic operations
    
    Args:
        id (int, optional): Unique identifier for existing uniform
        student_id (int, optional): ID of student to assign uniform to
        shako_num (str, optional): Identifier for the shako
        hanger_num (str, optional): Identifier for the hanger
        garment_bag (str, optional): Identifier for the garment bag
        coat_num (str, optional): Identifier for the coat
        pants_num (str, optional): Identifier for the pants
        status (str, optional): Override for automatic status
        notes (str, optional): Additional notes about the uniform
    
    Business Rules:
    - If student_id is provided, status is forced to "Assigned"
    - If no student_id and no status, defaults to "Available"
    - Empty string values are normalized to None
    - Updates are performed atomically
    - Lookup prioritizes ID match
    
    Note:
        This is the preferred method for uniform record management as it
        handles all edge cases and maintains data consistency
    """
    conn, cursor = connect_db()
    try:
        # Normalize
        student_id = None if not student_id else student_id
        notes = None if not notes else notes

        # Force status
        if student_id:
            status = "Assigned"
        elif not status:
            status = "Available"

        # Try lookup by id first
        existing = None
        if id:
            cursor.execute("SELECT id FROM uniforms WHERE id=?", (id,))
            existing = cursor.fetchone()

        # If no id, try lookup by student_id (but only if unique)
        if not existing and student_id:
            cursor.execute("SELECT id FROM uniforms WHERE student_id=?", (student_id,))
            rows = cursor.fetchall()
            if len(rows) == 1:
                existing = rows[0]

        if existing:
            cursor.execute('''
                UPDATE uniforms
                   SET shako_num   = COALESCE(NULLIF(?, ''), shako_num),
                       hanger_num  = COALESCE(NULLIF(?, ''), hanger_num),
                       garment_bag = COALESCE(NULLIF(?, ''), garment_bag),
                       coat_num    = COALESCE(NULLIF(?, ''), coat_num),
                       pants_num   = COALESCE(NULLIF(?, ''), pants_num),
                       status      = ?,
                       student_id  = COALESCE(NULLIF(?, ''), student_id),
                       notes       = COALESCE(NULLIF(?, ''), notes)
                 WHERE id = ?
            ''', (shako_num, hanger_num, garment_bag, coat_num, pants_num,
                  status, student_id, notes, existing[0]))
        else:
            cursor.execute('''
                INSERT INTO uniforms (
                    student_id, shako_num, hanger_num, garment_bag,
                    coat_num, pants_num, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (student_id, shako_num, hanger_num, garment_bag,
                  coat_num, pants_num, status, notes))

        conn.commit()
    finally:
        conn.close()

# ------------------------------------------------------------------------------
# Instrument functions
# ------------------------------------------------------------------------------

# Retrieves all students who have instruments currently checked out
# Uses a JOIN between students and instruments tables to get complete information
# The subquery ensures we only get the most recent instrument assignment per student
def get_students_with_outstanding_instruments():
    """
    Returns a list of students who currently have instruments checked out (status = 'Assigned').
    Each row includes student name, student section, and instrument details.
    """
    conn, cursor = connect_db()
    
    cursor.execute('''
        SELECT s.first_name, s.last_name, s.section,
               i.instrument_name, i.instrument_serial, i.instrument_case
        FROM students s
        JOIN instruments i ON s.student_id = i.student_id
        WHERE i.status = 'Assigned'
        ORDER BY s.last_name, s.first_name, i.instrument_name
    ''')

    results = cursor.fetchall()
    conn.close()
    return results

def get_students_with_outstanding_instruments_by_section(section):
    """
    Returns a list of students in a specific section (e.g., 'Trumpet', 'Flags')
    who currently have instruments checked out (status = 'Assigned').

    Note:
    - The section filter applies to the student's section (s.section), not the instrument.
    - instrument_name now represents both instrument type and section, so no need to filter it separately.
    """
    conn, cursor = connect_db()

    cursor.execute('''
        SELECT s.first_name, s.last_name, s.section,
               i.instrument_name, i.instrument_serial, i.instrument_case
        FROM students s
        JOIN instruments i ON s.student_id = i.student_id
        WHERE i.status = 'Assigned'
          AND s.section = ?
        ORDER BY s.last_name, s.first_name, i.instrument_name
    ''', (section,))

    results = cursor.fetchall()
    conn.close()
    return results

def get_all_instruments():
    """
    Fetch all instrument records from the database.
    Includes assignment status, condition, and metadata.
    Results are sorted by status priority, then instrument name, then ID.
    """
    conn, cursor = connect_db()

    cursor.execute("""
        SELECT id, student_id, instrument_name, instrument_serial,
               instrument_case, model, condition, status, notes
        FROM instruments
        ORDER BY 
            CASE status 
                WHEN 'Assigned'   THEN 1   -- Show assigned instruments first
                WHEN 'Available'  THEN 2   -- Then available
                WHEN 'Maintenance' THEN 3  -- Then under maintenance
                WHEN 'Retired'    THEN 4   -- Retired instruments last
            END,
            instrument_name,                -- Alphabetical within status
            id                              -- Stable ordering by ID
    """)

    results = cursor.fetchall()
    conn.close()
    return results

def find_instrument_by_serial(serial):
    """
    Locate an instrument in the database using its serial number.
    
    This function is commonly used for:
    - Instrument checkout verification
    - Inventory audits
    - Maintenance tracking
    - Assignment validation
    
    Args:
        serial (str): The serial number of the instrument to find
        
    Returns:
        tuple: A row containing (id, student_id, instrument_name, 
               instrument_serial, instrument_case, status, notes) if found,
               None if no matching instrument exists
               
    Note:
        Serial numbers should be unique across all instruments. This
        function expects to find at most one matching record.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT id, student_id, instrument_name, instrument_serial, instrument_case, status, notes FROM instruments WHERE instrument_serial = ?", (serial,))
    res = cursor.fetchone()
    conn.close()
    return res

def update_instrument_by_id(inst_id, student_id=None, status=None, notes=None, case=None, name=None, model=None, condition=None):
    """
    Update an instrument record with new information.
    
    This function provides flexible updating of instrument records by allowing
    partial updates of specific fields. The student_id will always be
    updated (can be set to NULL by passing None), while other fields
    are only updated if explicitly provided.
    
    Common Use Cases:
    - Assigning/unassigning instruments to students
    - Updating instrument condition
    - Recording maintenance or repairs
    - Changing case assignments
    - Updating model information
    - Recording status changes
    
    Args:
        inst_id (int): The unique identifier of the instrument to update
        student_id (int, optional): The ID of student to assign instrument to,
            or None to unassign
        status (str, optional): New status for the instrument
            (e.g., 'Available', 'Assigned', 'Maintenance', 'Retired')
        notes (str, optional): Additional notes about condition,
            repairs, or other relevant information
        case (str, optional): Updated case identifier/number
        name (str, optional): Updated instrument name/type
        model (str, optional): Updated instrument model
        condition (str, optional): Updated condition assessment
    
    Business Rules:
    - student_id is always updated, even if None
    - Other fields are only updated when explicitly provided
    - Updates are atomic - either all specified changes succeed or none do
    - Maintains complete instrument history through notes
    
    Note:
        This is the primary method for updating instrument records and
        should be used in preference to direct database modifications
        to ensure data consistency and proper tracking.
    """
    conn, cursor = connect_db()
    fields = []  # Will hold the SQL field=value pairs
    params = []  # Will hold the parameter values for SQL query
    
    # Always update student_id, even if None (set to NULL)
    # This ensures consistent behavior when unassigning instruments
    fields.append("student_id = ?")
    params.append(student_id)
    
    # Only add fields to update if they have non-None values
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
    
    # If no fields to update (shouldn't happen due to student_id), exit early
    if not fields:
        conn.close()
        return
        
    # Add the ID as the last parameter for the WHERE clause
    params.append(inst_id)
    
    # Build and execute the dynamic UPDATE query
    cursor.execute(f"UPDATE instruments SET {', '.join(fields)} WHERE id = ?", tuple(params))
    conn.commit()
    conn.close()

# Creates a new instrument record and assigns it to a student in one step
# The status is automatically set to 'Assigned' since this is a checkout operation
def assign_instrument(student_id, instrument_name, instrument_serial, instrument_case,
                      model=None, condition=None, notes=None):
    """
    Create and assign a new instrument record to a student.
    
    This function streamlines the instrument checkout process by creating
    a new instrument record and assigning it to a student in one atomic
    operation. The status is automatically set to 'Assigned'.
    
    Common Use Cases:
    - Initial instrument checkout
    - New semester assignments
    - Replacement instrument assignments
    - Instrument upgrades
    
    Args:
        student_id (int): ID of the student receiving the instrument
        instrument_name (str): Type/name of the instrument (e.g., 'Trumpet', 'Clarinet')
        instrument_serial (str): Unique serial number of the instrument
        instrument_case (str): Identifier for the instrument's case
        model (str, optional): Specific model of the instrument
        condition (str, optional): Current condition assessment
        notes (str, optional): Additional notes about the instrument or assignment
    
    Note:
        - Creates a new instrument record rather than modifying existing ones
        - Automatically sets status to 'Assigned'
        - Ensures atomic creation and assignment
        - Use update_instrument_by_id() for existing instruments
    """
    conn, cursor = connect_db()

    # Insert a new record with all instrument details
    # Required fields: student_id, name, serial, case
    # Optional fields: model, condition, notes
    # Status is forced to "Assigned" since this is a checkout
    cursor.execute('''
        INSERT INTO instruments (
            student_id, instrument_name, instrument_serial, instrument_case,
            model, condition, status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        student_id,
        instrument_name,
        instrument_serial,
        instrument_case,
        model,
        condition,
        "Assigned",   # <-- status is now the only flag
        notes
    ))

    conn.commit()
    conn.close()

def return_instrument(student_id):
    """
    Mark the currently assigned instrument for a student as returned.
    Clears the student_id and sets status back to 'Available'.
    """
    conn, cursor = connect_db()
    cursor.execute("""
        UPDATE instruments
           SET student_id = NULL,
               status = 'Available'
         WHERE student_id = ? AND status = 'Assigned'
    """, (student_id,))
    conn.commit()
    conn.close()

def add_instrument(id, student_id, instrument_name, instrument_serial, instrument_case,
                   model=None, condition=None, status=None, notes=None):
    """
    Manually insert an instrument record with a specific ID.
    
    This is an administrative function primarily used for:
    - Data migration from legacy systems
    - Database restoration
    - Batch imports
    - System initialization
    - Manual record corrections
    
    Unlike assign_instrument(), this function:
    - Allows specification of record ID
    - Provides full control over status
    - Does not enforce assignment rules
    - Supports batch operations
    
    Args:
        id (int): Specific ID for the instrument record
        student_id (int, optional): ID of assigned student, if any
        instrument_name (str): Type/name of the instrument
        instrument_serial (str): Unique serial number
        instrument_case (str): Case identifier
        model (str, optional): Instrument model information
        condition (str, optional): Current condition assessment
        status (str, optional): Explicit status setting
            (defaults based on student_id)
        notes (str, optional): Additional record information
    
    Note:
        This is a low-level function that bypasses normal assignment
        logic. For regular instrument assignments, prefer using
        assign_instrument() instead.
    """
    """
    Manually insert a new instrument record into the database.
    Typically used for admin tools, migrations, or bulk imports.
    Only essential fields are included — others default to NULL or 'Available'.
    """
    conn, cursor = connect_db()

    # Normalize inputs
    student_id = student_id if student_id not in ("", None) else None
    status = status or ("Assigned" if student_id else "Available")

    cursor.execute('''
        INSERT INTO instruments (
            id, student_id, instrument_name, instrument_serial,
            instrument_case, model, condition, status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        id,
        student_id,
        instrument_name,
        instrument_serial,
        instrument_case,
        model,
        condition,
        status,
        notes
    ))

    conn.commit()
    conn.close()

def add_or_update_instrument(
    id, student_id, name, serial, case,
    model, condition, status, notes
):
    """
    Create a new instrument record or update an existing one.
    
    This is the primary function for managing instrument records in the system.
    It provides intelligent handling of both new and existing records with
    automatic status management and data consistency rules.
    
    Key Features:
    - Smart record lookup and creation
    - Automatic status management
    - Data normalization
    - Atomic operations
    - Consistent state handling
    
    Args:
        id (int): Unique identifier for existing instrument (or new one)
        student_id (int, optional): ID of student to assign instrument to
        name (str): Instrument name/type
        serial (str): Unique serial number
        case (str): Case identifier
        model (str): Instrument model information
        condition (str): Current condition assessment
        status (str, optional): Override for automatic status
        notes (str, optional): Additional notes about the instrument
    
    Business Rules:
    - If student_id is provided, status is forced to 'Assigned'
    - If no student_id and no status, defaults to 'Available'
    - Empty strings are normalized to None
    - Updates are atomic
    - Existing records are updated, new ones created
    
    Note:
        This is the preferred method for instrument record management as it
        handles all edge cases and maintains data consistency
    """
    conn, cursor = connect_db()
    try:
        # 1) fetch existing
        cursor.execute("SELECT student_id, status FROM instruments WHERE id = ?", (id,))
        existing = cursor.fetchone()

        # 2) normalize incoming values
        incoming_student = student_id if student_id not in (None, "") else None
        incoming_status  = status     if status     not in (None, "") else None

        # 3) preserve or infer
        if existing:
            preserved_student = incoming_student if incoming_student is not None else existing[0]
            preserved_status  = incoming_status  if incoming_status  is not None else existing[1]
        else:
            preserved_student = incoming_student
            preserved_status  = incoming_status

        # 4) enforce consistency
        if preserved_student is not None:
            preserved_status = "Assigned"
        if preserved_status is None:
            preserved_status = "Available"

        # 5) perform upsert
        if existing:
            cursor.execute(
                """
                UPDATE instruments
                   SET student_id=?,
                       instrument_name=?, instrument_serial=?,
                       instrument_case=?, model=?, condition=?,
                       status=?, notes=?
                 WHERE id=?
                """,
                (
                    preserved_student,
                    name or None, serial or None,
                    case or None, model or None, condition or None,
                    preserved_status, notes or None,
                    id,
                )
            )
        else:
            cursor.execute(
                """
                INSERT INTO instruments (
                    id, student_id, instrument_name, instrument_serial,
                    instrument_case, model, condition, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    id, preserved_student,
                    name or None, serial or None,
                    case or None, model or None, condition or None,
                    preserved_status, notes or None,
                )
            )
        conn.commit()

    finally:
        conn.close()

    return existing is None
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