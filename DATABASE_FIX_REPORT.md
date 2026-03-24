# Equipment Management - Database Stability Fix Report

## Critical Issues Identified

### Issue #1: Database Stored in Read-Only PyInstaller Temporary Directory ⚠️ CRITICAL

**Problem:**
When your application is packaged with PyInstaller as an .exe, the `students.db` file gets extracted to a temporary read-only directory (`sys._MEIPASS`). SQLite cannot write persistent data to read-only locations, causing:
- New student entries to disappear
- Changes not being saved to disk
- Data loss when minimizing window or closing app
- Silent failures (no error shown to user)

**Root Cause:**
```python
# OLD CODE (BROKEN):
DB_NAME = resource_path("Database/students.db")
# When running from .exe, this points to:
# C:\Users\{user}\AppData\Local\Temp\_MEI{xxxxx}\Database\students.db
# This directory is READ-ONLY!
```

**Why This Happens:**
1. PyInstaller bundles your Database/students.db file
2. When the .exe runs, PyInstaller extracts everything to a temporary directory
3. SQLite attempts to write to this temp directory
4. Writes fail silently because the directory is read-only
5. Each time the app restarts, it extracts fresh files, losing all previous changes

### Issue #2: No Proper Database Path for Packaged Applications

The codebase had a commented-out alternative path suggestion:
```python
# For deployment: Database alongside the executable (uncomment when packaging)
#DB_NAME = os.path.join(os.path.dirname(sys.executable), "Database", "students.db")
```

This wasn't the proper solution because it would still try to write alongside the .exe in Program Files (if installed there), which also has permission restrictions.

### Issue #3: Database Connection Missing Timeout and Isolation Configuration

Without proper timeout and isolation settings:
- Application could freeze if database gets locked
- Multiple processes writing simultaneously could corrupt data
- No protection against concurrent access issues

---

## Solutions Implemented

### Fix #1: Use Persistent User-Writable Directory

**New Behavior:**
```python
# NEW CODE (FIXED):
def get_persistent_db_path():
    if hasattr(sys, '_MEIPASS'):  # Running from PyInstaller
        # Use Windows AppData (always user-writable)
        app_data = os.getenv('LOCALAPPDATA')
        db_dir = os.path.join(app_data, 'EquipmentManagement')
        # e.g., C:\Users\{user}\AppData\Local\EquipmentManagement\students.db
        
        # Create directory if needed
        os.makedirs(db_dir, exist_ok=True)
        
        # Copy bundled database on first run
        if not os.path.exists(db_file):
            shutil.copy2(bundled_db, db_file)
        
        return db_file
    else:  # Running from source
        # Use local Database directory (development)
        return resource_path("Database/students.db")
```

**What This Does:**
1. **Detects PyInstaller Mode:** Uses `sys._MEIPASS` to determine if running from .exe
2. **Uses User's AppData:** Stores database in `%LOCALAPPDATA%\EquipmentManagement\` (always writable)
3. **Creates Directory:** Automatically creates the directory if it doesn't exist
4. **First-Run Migration:** Copies the bundled database on first run (preserves initial schema)
5. **Persistent Data:** All subsequent changes are saved to the user-writable location

**Where Database Will Be Stored:**
- **Development:** `{ProjectRoot}/Database/students.db` (unchanged)
- **Packaged .exe:** `C:\Users\{username}\AppData\Local\EquipmentManagement\students.db`

### Fix #2: Enhanced Database Connection with Timeout & Isolation

**New Configuration:**
```python
def connect_db():
    conn = sqlite3.connect(
        DB_NAME, 
        timeout=10.0,              # 10-second timeout prevents freezing
        check_same_thread=False    # Allows connection flexibility
    )
    conn.isolation_level = 'DEFERRED'  # Only locks when writing, not reading
    return conn, cursor
```

**Benefits:**
- **10-Second Timeout:** If database is locked, waits up to 10 seconds instead of blocking indefinitely
- **DEFERRED Isolation:** Minimizes lock contention for concurrent operations
- **Prevents Freezing:** App won't hang when database is in use

### Fix #3: Added Debug Logging

**In main.py:**
```python
print(f"Database file location: {db.DB_NAME}")
```

When users run the application, they'll see output like:
```
Database file location: C:\Users\benny\AppData\Local\EquipmentManagement\students.db
```

This helps verify the database is in the correct location.

---

## Testing the Fix

### For Development:
```bash
python src/main.py
# Database location should print to console
# Should use: {ProjectRoot}/Database/students.db
```

### For Packaged Application:
1. **Build the .exe:**
   ```powershell
   python -m PyInstaller src/main.py --onefile --windowed `
     --add-data "Database/students.db;Database" `
     --add-data "styles.qss;."
   ```

2. **Run the .exe from dist/main.exe**
3. **Check console output** for database location (should show AppData path)
4. **Add several students** and verify they persist after:
   - Minimizing window
   - Closing and reopening app
   - Restarting computer

### Verify Persistence:
1. Run dist/main.exe
2. Add a student (e.g., "Test Student")
3. Close the application
4. Run dist/main.exe again
5. Find Student should show "Test Student" still in database

---

## Migration for Existing Users

**If users already have data in the wrong location:**

1. Their data might be in: `C:\Users\{user}\AppData\Local\Temp\_MEI{xxxxx}\Database\students.db`
2. This directory is temporary and gets deleted
3. On first run with the fixed version:
   - Check if bundled database has data → copy it as initial data
   - If not, start fresh with empty database

**Recommendation:** Provide users with a backup/restore mechanism (you already have this in the code):
- Ask them to export their data as CSV before updating
- After updating, import the CSV into the new application

---

## Why This Happened

1. **Development Testing:** The app was tested only in development mode where the local `Database/students.db` is user-writable
2. **PyInstaller Assumption:** The bundled database path works for reading initial schema, but SQLite writes fail silently to read-only directories
3. **Silent Failures:** SQLite doesn't throw obvious exceptions when writes fail on read-only media; they just disappear
4. **Minimize/Close Behavior:** Data loss becomes apparent when app restarts, which happens after minimize/close

---

## Files Modified

1. **src/db.py**
   - Added `get_persistent_db_path()` function
   - Updated `DB_NAME` initialization
   - Enhanced `connect_db()` with timeout and isolation settings

2. **src/main.py**
   - Added debug print statement for database location

---
