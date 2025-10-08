# EquipmentManagement

A desktop application for managing student equipment—uniforms, instruments, and related inventory—built with Python, PyQt, and SQLite. It provides a full-screen UI for viewing and assigning items, prevents double-assignments, and offers status-based sorting (Assigned → Available → Maintenance → Retired).

Table of Contents
- Features
- Prerequisites
- Installation
- Project Structure
- Database Schema
- Running the Application
- Usage
- Extending & Contributing
- License

## Features
- Student management (lookup by 9-digit ID)
- Inventory tracking for:
- Instruments (type, serial, case, status)
- Uniform components (shakos, coats, pants, bags)
- Double-booking protection on assignments
- Status-view tables (Assigned → Available → Maintenance → Retired)
- Full-screen, collapsible groups per component
- Real-time UI refresh after any change

## Prerequisites
- Python 3.13
- PyQt6 (or PySide6)
- SQLite3 (bundled with Python)

## Installation
- Clone the repository
git clone https://github.com/benny/EquipmentManagement.git
cd EquipmentManagement
- Create a virtual environment
python -m venv venv
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows
- Install dependencies
pip install PyQt6
pip install qrcode
pip install python-barcode[images]   # brings in `barcode` and `ImageWriter`
pip install pillow                  # for PIL Image support



## Project Structure

EquipmentManagement/

├─ .idea/                         # IDE settings

├─ .vscode/                       # VSCode workspace settings

├─ build/                         # Build output (PyInstaller)

├─ dist/                          # Distribution artifacts

├─ Database/

│  └─ students.db                 # SQLite database file

├─ node_modules/                  # If packaging web assets

├─ src/

│  ├─ __pycache__/                # Compiled bytecode

│  ├─ add_instrument_dialog.py    # Instrument-assignment popup

│  ├─ add_student_dialog.py       # Student-creation popup

│  ├─ add_uniform_dialog.py       # Uniform-assignment popup

│  ├─ db.py                       # SQLite connection & queries

│  ├─ edit_student_dialog.py      # Student-edit popup

│  ├─ main.py                     # Application entry point

│  ├─ ui.py                       # Main Qt UI logic

│  └─ utils.py                    # Helper functions

├─ main.spec                      # PyInstaller spec file

├─ package.json                   # Node/web config (if any)

├─ package-lock.json              # Locked Node modules

├─ requirements.txt               # Python dependencies

├─ README.md                      # This file

└─ styles.qss                     # Qt stylesheet




- main.py
Initializes the Qt application, loads the main window, and connects to the database.
- db.py
- connect_db()
- CRUD helpers for students, uniforms, instruments, shakos, coats, pants, garment_bags
- Query functions with ORDER BY CASE status sorting
- get_uniforms_by_student_id() and get_instrument_by_student_id()
- ui.py
- show_uniform_table_screen(), show_instrument_table_screen()
- Assign-popup dialogs with double-booking checks
- Table-refresh logic

## Database Schema
All tables live in an SQLite database (equipment.db by default). Core tables:
### students
- student_id (PK), first_name, last_name, glove_size, spat_size
### uniforms
- id (PK), student_id (FK → students),
shako_num, coat_num, pants_num, garment_bag, hanger_num,
status, notes
### shakos, coats, pants, garment_bags
- Each has id (PK), part-specific fields (e.g. shako_num or coat_num),
status, student_id (FK → students), notes
### instruments
- id (PK), student_id (FK → students), type, serial, instrument_case,
status, notes

[Student Database ERD](https://github.com/BenitoReyes/EquipmentManagement/blob/main/Database%20ERD.md)

## Running the Application
Use your Python interpreter to launch the main module. For example, from PowerShell:
PS C:\Users\benny\Documents\GitHub\EquipmentManagement> `
  & 'c:\Python313\python.exe' `
    'c:\Users\benny\.vscode\extensions\ms-python.debugpy-2025.10.0-win32-x64\bundled\libs\debugpy\launcher' `
    '51444' '--' `
    'C:\Users\benny\Documents\GitHub\EquipmentManagement\src\main.py'
    
Or simply:
python src/main.py



## Usage
- Uniform Screen
- Collapsible groups for Shakos, Coats, Pants, Garment Bags
- Assign via “Assign Uniform” popup (9-digit ID + parts)
- Double-assignment blocked at UI and DB level
- Instrument Screen
- View all instruments, sorted by status
- Assign via serial-lookup popup (with case prompt)
- Prevents double-booking per student
- Automatic Refresh
- After any assignment or update, the active table reloads
- “Outstanding Instruments” and “Outstanding Uniforms” printouts

Extending & Contributing
- Pull Requests welcome! Please fork, work on a feature branch, and submit against main.

## License

© 2025 Benito Reyes 
Licensed under CC BY-NC-SA 4.0. See [LICENSE](LICENSE) for full terms.
