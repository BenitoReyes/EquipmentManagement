"""
This module defines the EquipmentManagementUI class, which provides
a Qt-based graphical interface for managing students, uniforms, and instruments.
It features menus for CRUD operations, CSV import/export, code generation,
printing support, and backup/restore functionality.
"""
# --- PyQt6 Widgets and Layouts for building the UI ---
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QInputDialog, QToolButton, QMenu, QHBoxLayout, QDialog, QListWidget, QFileDialog, QTextEdit
# --- Qt GUI classes for icons, images, and painting operations ---
from PyQt6.QtGui import QAction, QPixmap, QImage, QPainter, QIcon
# --- Core Qt constants for alignment, sizing, and text flags ---
from PyQt6.QtCore import Qt, QSize
# --- Qt printing support classes ---
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
# Third-party libraries for QR/barcode generation and image manipulation
import qrcode
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import io
import csv
# Application-specific dialogs for adding/editing students
from add_student_dialog import AddStudentDialog
from edit_student_dialog import EditStudentDialog
# Database module providing CRUD methods for students, uniforms, instruments
import db
import sys, os

def resource_path(relative_path):
    """
    Resolve a path to an embedded resource file, whether running as a script
    or as a frozen executable (e.g., PyInstaller).
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def load_stylesheet():
    path = resource_path("styles.qss")
    with open(path, "r") as f:
        return f.read()


def desanitize(value):
    """
    Convert a raw CSV or database field to None if its empty or the literal "none".
    This ensures optional fields are stored as Python None, not empty strings.
    """
    return None if value.strip().lower() == "none" or value.strip() == "" else value.strip()

class EquipmentManagementUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Equipment Management")
        self.setGeometry(200, 200, 900, 700)
        self.setStyleSheet(load_stylesheet())

        # Main vertical layout to stack widgets
        layout = QVBoxLayout()

        # Title label at top of the window
        self.title_label = QLabel("Equipment Management System")
        layout.addWidget(self.title_label)

        # --- Button bar: horizontal layout of tool buttons & info icon ---
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        # Student operations menu and toolbutton
        student_menu = QMenu()
        student_menu.addAction("Add Student", self.open_add_student_popup)
        student_menu.addAction("Update Student", self.update_student)
        student_menu.addAction("Delete Student", self.delete_student)
        student_menu.addAction("Find Student", self.find_student_popup)
        student_menu.addAction("Student to Bar/QR code", self.student_to_code_popup)
        student_menu.addAction("Import Students from CSV", self.import_students_from_csv)
        student_ops = QToolButton()
        student_ops.setText("Student Operations")
        student_ops.setMenu(student_menu)
        student_ops.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        button_layout.addWidget(student_ops)

        # Equipment operations menu and toolbutton
        equipment_menu = QMenu()
        equipment_menu.addAction("Assign Uniform", self.assign_uniform_popup)
        equipment_menu.addAction("Return Uniform", self.return_uniform_popup)
        equipment_menu.addAction("View Outstanding Uniforms", self.show_outstanding_uniforms)
        equipment_menu.addSeparator()
        equipment_menu.addAction("Assign Instrument", self.assign_instrument_popup)
        equipment_menu.addAction("Return Instrument", self.return_instrument_popup)
        equipment_menu.addAction("View Outstanding Instruments", self.show_outstanding_instruments)
        equipment_ops = QToolButton()
        equipment_ops.setText("Equipment Operations")
        equipment_ops.setMenu(equipment_menu)
        equipment_ops.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        button_layout.addWidget(equipment_ops)

        # Administrative operations menu and toolbutton
        admin_menu = QMenu()
        admin_menu.addAction("Delete ALL Students", self.delete_all_students)
        admin_menu.addSeparator()
        admin_menu.addAction("Create Backup", self.create_backup)
        admin_menu.addAction("Use Backup", self.use_backup)
        admin_ops = QToolButton()
        admin_ops.setText("Administrative Operations")
        admin_ops.setMenu(admin_menu)
        admin_ops.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        button_layout.addWidget(admin_ops)

        # Info button with help icon to show an About dialog
        info_button = QPushButton()
        info_button.setIcon(QIcon.fromTheme("system-help"))  # Uses system icon if available
        info_button.setToolTip("About this app")
        info_button.clicked.connect(self.show_about_dialog)
        info_button.setIconSize(QSize(19, 19))  # Adjust size to fit nicely
        button_layout.addWidget(info_button)
        button_layout.setContentsMargins(5, 5, 5, 5)
        button_layout.addStretch(1)
        layout.addLayout(button_layout)
        # --- End Button Layout ---

        # Table widget to display student records and their assigned items
        self.student_table = QTableWidget()

        # 19 columns for all student and equipment fields
        self.student_table.setColumnCount(19)
        self.student_table.setHorizontalHeaderLabels([
            "Student ID", "Last Name", "First Name", "Section", "Phone", "Email",
            "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #",
            "Spats Size", "Gloves Size", "Guardian Name", "Guardian Phone",
            "Instrument Name", "Instrument Serial", "Instrument Case", "Year Came Up"
        ])
        layout.addWidget(self.student_table)

        # Finalize layout
        self.setLayout(layout)

        # Populate table initially and sort by last name
        self.student_table.clearContents()
        self.refresh_table()
        self.student_table.sortItems(1)

    def show_about_dialog(self):
        QMessageBox.information(
            self,
            "About This App",
            "Made by: Benito Reyes \n(Fall 2021 Trumpet and Spring 2024 DI,, Ace) in 2025.\n\n"
            "Code can be found at:\nhttps://github.com/BenitoReyes/EquipmentManagement"
        )

    def sanitize(self, value):
        """
        Convert None or "none" (case-insensitive) to empty string before writing to CSV.
        Ensures all fields serialize cleanly.
        """
        return "" if value is None or str(value).strip().lower() == "none" else str(value)

    def refresh_table(self):
        """
        Clear and reload all student rows from the database,
        including their current uniform and instrument assignments.
        Called after any CRUD operation to reflect changes.
        """
        self.student_table.setRowCount(0)
        students = db.get_students_with_uniforms_and_instruments()
        for row_idx, student in enumerate(students):
            self.student_table.insertRow(row_idx)
            for col_idx, value in enumerate(student):
                display_value = "" if value is None else str(value)
                self.student_table.setItem(row_idx, col_idx, QTableWidgetItem(display_value))

        # Always re-sort by last name after refresh
        self.student_table.sortItems(1)

    def open_add_student_popup(self):
        """
        Launch the custom AddStudentDialog.
        On successful exec(), automatically refresh the table.
        """
        dialog = AddStudentDialog()
        if dialog.exec():
            self.refresh_table()

    def update_student(self):
        """
        Allow updating of an existing student record.
        1. Prompt for Student ID or fall back to last name search.
        2. Validate ID format.
        3. Fetch student, then open EditStudentDialog.
        4. Refresh table on success.
        """
        """Step 1: Ask user for Student ID before updating."""
        student_id, ok = QInputDialog.getText(self, "Update Student", "Enter Student ID: \n(Or leave empty to search by name):")
        if not ok or not student_id.strip():
            QMessageBox.information(self, "Message", "Student ID left empty, searching by last name.")
            last_name, ok_last = QInputDialog.getText(self, "Update Student", "Enter Last Name:")
            if not ok_last or not last_name.strip():
                return
            students = db.get_students_by_last_name(last_name.strip())
            if not students:
                QMessageBox.information(self, "Not Found", "No students found with that last name.")
                return
            
            # Build a selection dialog to choose among matches
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Student")
            layout = QVBoxLayout()
            label = QLabel("Select a student to edit:")
            layout.addWidget(label)
            list_widget = QListWidget()
            for student in students:
                list_widget.addItem(f"{student[2]}, {student[1]} (ID: {student[0]})")
            layout.addWidget(list_widget)
            button = QPushButton("Edit")
            layout.addWidget(button)
            dialog.setLayout(layout)
            def handle_edit():
                idx = list_widget.currentRow()
                if idx >= 0:
                    edit_dialog = EditStudentDialog(students[idx])
                    edit_dialog.exec()
                    self.refresh_table()
                    dialog.accept()
            button.clicked.connect(handle_edit)
            dialog.exec()
            return
        
        # Step 2: Validate Student ID format
        if not student_id.isdigit() or len(student_id) != 9:
            QMessageBox.warning(self, "Error", "Student ID must be exactly 9 digits.")
            return
        
        # Step 3: Fetch existing data
        student_data = db.get_student_by_id(student_id.strip())
        if not student_data:
            QMessageBox.warning(self, "Error", "No student found with that ID.")
            return
        
        # Step 4: Launch edit dialog with pre-loaded data
        dialog = EditStudentDialog(student_data)
        if dialog.exec():  # If user confirms update
            self.refresh_table()


    def delete_student(self):
        """
        Prompt for Student ID, validate, confirm deletion,
        remove from database, and refresh table.
        """
        student_id, ok = QInputDialog.getText(self, "Delete Student", "Enter Student ID:")
        if not ok or not student_id.strip():
            return

        # Add validation for Student ID
        if not student_id.isdigit() or len(student_id) != 9:
            QMessageBox.warning(self, "Error", "Student ID must be exactly 9 digits.")
            return

        # Step 2: Check if the student exists before deleting
        student_data = db.get_student_by_id(student_id.strip())
        if not student_data:
            QMessageBox.warning(self, "Error", "No student found with that ID.")
            return

        # Step 3: Confirm deletion
        # build a full name separately
        full_name = f"{student_data[1]} {student_data[2]}"

        confirm = QMessageBox.question(self, "Confirm Delete",
                               f"Are you sure you want to delete {full_name} (ID: {student_data[0]})?",
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm != QMessageBox.StandardButton.Yes:
            return  # User canceled deletion

        db.delete_student(student_id)
        QMessageBox.information(self, "Success", "Student deleted!")

        self.refresh_table()



    def delete_all_students(self):
        """
        Permanently delete ALL student, uniform, and instrument records
        after a two-step confirmation (dialog + typed confirmation).
        """
        # Combined first and second confirmation
        reply = QMessageBox.question(
            self,
            "Confirm Delete All",
            "Are you absolutely sure you want to delete ALL students? This will permanently remove ALL student records, uniforms, and instruments. This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Second confirmation: require typing "DELETE ALL"
        text, ok = QInputDialog.getText(
            self,
            "Final Confirmation",
            'Type "DELETE ALL" (all caps, no quotes) to confirm:'
        )
        if not ok or text.strip() != "DELETE ALL":
            QMessageBox.information(self, "Cancelled", "Operation cancelled.")
            return

        # Perform deletion
        db.delete_all_students()
        QMessageBox.information(self, "Deleted", "All students have been deleted.")
        self.refresh_table()

    def find_student_popup(self):
        """
        Search for a student either by ID or Section.
        Presents a dialog to view or edit selected student(s).
        """
        # Ask user which search type to use
        search_type, ok = QInputDialog.getItem(
            self, "Find Student", "Search by:", ["Student ID", "Section"], 0, False
        )
        if not ok:
            return

         # --- Search by ID flow ---
        if search_type == "Student ID":
            student_id, ok = QInputDialog.getText(self, "Find Student", "Enter Student ID:")
            if not ok or not student_id.strip():
                return
            if not student_id.isdigit() or len(student_id) != 9:
                QMessageBox.warning(self, "Error", "Student ID must be exactly 9 digits.")
                return

            student = db.get_student_by_id(student_id.strip())
            if not student:
                QMessageBox.information(self, "Not Found", "No student found with that ID.")
                return

            # Build a simple dialog with View/Edit buttons
            dialog = QDialog(self)
            dialog.setWindowTitle("Student Found")
            layout = QVBoxLayout()
            label = QLabel(f"Student: {student[2]}, {student[1]} (ID: {student[0]})")
            layout.addWidget(label)

            # Buttons for viewing printable info or editing
            button_layout = QHBoxLayout()
            view_button = QPushButton("View")
            edit_button = QPushButton("Edit")
            button_layout.addWidget(view_button)
            button_layout.addWidget(edit_button)
            layout.addLayout(button_layout)

            dialog.setLayout(layout)

            def handle_view():

                # Assemble a full text dump with headers for printing
                headers = [
                    "Student ID", "First Name", "Last Name", "Section", "Phone", "Email",
                    "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #",
                    "Spats Size", "Gloves Size", "Guardian Name", "Guardian Phone",
                    "Instrument Name", "Instrument Serial", "Instrument Case", "Year Came up"
                ]
                info = "\n".join(f"{header}: {str(value) if value is not None else ''}" for header, value in zip(headers, student))
                self.show_printable_results("Student Info", info)
                dialog.accept()

            def handle_edit():
                edit_dialog = EditStudentDialog(student)
                edit_dialog.exec()
                self.refresh_table()
                dialog.accept()

            view_button.clicked.connect(handle_view)
            edit_button.clicked.connect(handle_edit)

            dialog.exec()
        
        # --- Search by Section flow ---
        elif search_type == "Section":
            section, ok = QInputDialog.getText(self, "Find Student", "Enter Section Name:")
            if not ok or not section.strip():
                return
            students = db.get_students_by_section(section.strip())
            if not students:
                QMessageBox.information(self, "Not Found", "No students found in that section.")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle("Select Student")
            layout = QVBoxLayout()
            label = QLabel("Select a student:")
            layout.addWidget(label)
            list_widget = QListWidget()
            for student in students:
                list_widget.addItem(f"{student[2]}, {student[1]} (ID: {student[0]})")
            layout.addWidget(list_widget)

            button_layout = QHBoxLayout()
            view_button = QPushButton("View All")
            edit_button = QPushButton("Edit Selected")
            button_layout.addWidget(view_button)
            button_layout.addWidget(edit_button)
            layout.addLayout(button_layout)

            dialog.setLayout(layout)

            def handle_view():
                headers = [
                    "Student ID", "First Name", "Last Name", "Section", "Phone", "Email",
                    "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #",
                    "Spats Size", "Gloves Size", "Guardian Name", "Guardian Phone",
                    "Instrument Name", "Instrument Serial", "Instrument Case", "Year Came up"
                ]

                # Concatenate info for all students in this section
                info = ""
                for student in students:
                    student_info = "\n".join(
                        f"{header}: {str(value) if value is not None else ''}"
                        for header, value in zip(headers, student)
                    )
                    info += student_info + "\n" + "-" * 40 + "\n"
                self.show_printable_results(f"Students in Section: {section.strip()}", info)
                dialog.accept()

            def handle_edit():
                idx = list_widget.currentRow()
                if idx >= 0:
                    edit_dialog = EditStudentDialog(students[idx])
                    edit_dialog.exec()
                    self.refresh_table()
                    dialog.accept()

            view_button.clicked.connect(handle_view)
            edit_button.clicked.connect(handle_edit)

            dialog.exec()
        


    def show_student_info(self, student):
        """
        Quick info dialog for a single student record.
        Not used in main flows but available for direct calls.
        """
        headers = [
            "Student ID", "First Name", "Last Name", "Section", "Phone", "Email",
            "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #",
            "Spats Size", "Gloves Size", "Guardian Name", "Guardian Phone",
            "Instrument Name", "Instrument Serial", "Instrument Case"
        ]
        info = "\n".join(f"{header}: {str(value) if value is not None else ''}" for header, value in zip(headers, student))
        QMessageBox.information(self, "Student Info", info)

    def assign_uniform_popup(self):
        """
        Prompt for Student ID, validate, then ask for each uniform component:
        shako, hanger, garment bag, coat, pants. Update DB and refresh.
        """
        student_id, ok = QInputDialog.getText(self, "Assign Uniform", "Enter Student ID:")
        if not ok or not student_id.strip():
            return
        if not student_id.isdigit() or len(student_id) != 9:
            QMessageBox.warning(self, "Error", "Student ID must be exactly 9 digits.")
            return
        student_data = db.get_student_by_id(student_id.strip())
        if not student_data:
            QMessageBox.warning(self, "Error", "No student found with that ID.")
            return
        # Get all uniform fields 
        shako_num, ok1 = QInputDialog.getInt(self, "Assign Uniform", "Enter Shako Number:")
        if not ok1:
            return
        hanger_num, ok2 = QInputDialog.getInt(self, "Assign Uniform", "Enter Hanger Number:")
        if not ok2:
            return
        garment_bag, ok3 = QInputDialog.getText(self, "Assign Uniform", "Enter Garment Bag:")
        if not ok3 or not garment_bag.strip():
            return
        coat_num, ok4 = QInputDialog.getInt(self, "Assign Uniform", "Enter Coat Number:")
        if not ok4:
            return
        pants_num, ok5 = QInputDialog.getInt(self, "Assign Uniform", "Enter Pants Number:")
        if not ok5:
            return

        # Assign uniform with all fields
        db.assign_uniform(student_id.strip(), shako_num, hanger_num, garment_bag.strip(), coat_num, pants_num)
        QMessageBox.information(self, "Success", "Uniform assigned!")
        self.refresh_table()


    def return_uniform_popup(self):
        """
        Mark uniform as returned for a given student.
        """
        student_id, ok = QInputDialog.getText(self, "Return Uniform", "Enter Student ID:")
        if not ok or not student_id.strip():
            return
        if not student_id.isdigit() or len(student_id) != 9:
            QMessageBox.warning(self, "Error", "Student ID must be exactly 9 digits.")
            return
        if not db.get_student_by_id(student_id.strip()):
            QMessageBox.warning(self, "Error", "No student found with that ID.")
            return
        db.return_uniform(student_id.strip())
        QMessageBox.information(self, "Success", "Uniform marked as returned.")
        self.refresh_table()


    def show_outstanding_uniforms(self):
        """
        Show all students who have not returned their uniforms.
        Optional filter by section name.
        """
        # Ask if user wants to filter by section
        filter_section, ok = QInputDialog.getText(self, "Outstanding Uniforms", "Enter section to filter (leave blank for all):")
        if ok and filter_section.strip():
            outstanding = db.get_students_with_outstanding_uniforms_by_section(filter_section.strip())
        else:
            outstanding = db.get_students_with_outstanding_uniforms()
        if not outstanding:
            QMessageBox.information(self, "Info", "All uniforms are accounted for.")
        else:

            # Build a printable message listing each student’s outstanding items
            message = "\n".join([
                f"{row[0]} {row[1]}: Shako: {row[2]}, Hanger: {row[3]}, Garment: {row[4]}, Coat: {row[5]}, Pants: {row[6]}"
                for row in outstanding
            ])
            self.show_printable_results("Outstanding Uniforms", message)


    def assign_instrument_popup(self):
        """
        Prompt for Student ID, validate, then ask for instrument name,
        serial number, and case. Update DB and refresh.
        """
        student_id, ok = QInputDialog.getText(self, "Assign Instrument", "Enter Student ID:")
        if not ok or not student_id.strip():
            return
        if not student_id.isdigit() or len(student_id) != 9:
            QMessageBox.warning(self, "Error", "Student ID must be exactly 9 digits.")
            return
        if not db.get_student_by_id(student_id.strip()):
            QMessageBox.warning(self, "Error", "No student found with that ID.")
            return
        instrument_name, ok1 = QInputDialog.getText(self, "Assign Instrument", "Instrument Name:")
        if not ok1 or not instrument_name.strip():
            return
        instrument_serial, ok2 = QInputDialog.getText(self, "Assign Instrument", "Instrument Serial:")
        if not ok2 or not instrument_serial.strip():
            return
        instrument_case, ok3 = QInputDialog.getText(self, "Assign Instrument", "Instrument Case:")
        if not ok3 or not instrument_case.strip():
            return

        db.assign_instrument(student_id.strip(), instrument_name.strip(), instrument_serial.strip(), instrument_case.strip())
        QMessageBox.information(self, "Success", "Instrument assigned!")
        self.refresh_table()

    def return_instrument_popup(self):
        """
        Mark an instrument as returned for the given student ID.
        """
        student_id, ok = QInputDialog.getText(self, "Return Instrument", "Enter Student ID:")
        if not ok or not student_id.strip():
            return
        if not student_id.isdigit() or len(student_id) != 9:
            QMessageBox.warning(self, "Error", "Student ID must be exactly 9 digits.")
            return
        if not db.get_student_by_id(student_id.strip()):
            QMessageBox.warning(self, "Error", "No student found with that ID.")
            return
        db.return_instrument(student_id.strip())
        QMessageBox.information(self, "Success", "Instrument marked as returned.")
        self.refresh_table()

    def show_outstanding_instruments(self):
        """
        Show all students who have not returned their instruments.
        Optional filter by section name.
        """
        # Ask if user wants to filter by section
        filter_section, ok = QInputDialog.getText(self, "Outstanding Instruments", "Enter section to filter (leave blank for all):")
        if ok and filter_section.strip():
            outstanding = db.get_students_with_outstanding_instruments_by_section(filter_section.strip())
        else:
            outstanding = db.get_students_with_outstanding_instruments()
        if not outstanding:
            QMessageBox.information(self, "Info", "All instruments are accounted for.")
        else:
            message = "\n".join([
                f"{row[0]} {row[1]}: {row[2]} (Serial: {row[3]}, Case: {row[4]})"
                for row in outstanding
            ])
            self.show_printable_results("Outstanding Uniforms", message)

    def create_backup(self):
        """
        Open a save dialog, write all student, uniform, and instrument
        records to a text file in CSV-like lines prefixed by section.
        """
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "Create Backup", "", "Text Files (*.txt)")
            if not file_path:
                return

            with open(file_path, "w", encoding="utf-8") as backup_file:
                # write students
                for student in db.get_students():  # instead of db.get_all_students()
                    backup_file.write("students," + ",".join(self.sanitize(field) for field in student) + "\n")

                # write uniforms
                for uniform in db.get_all_uniforms():
                    backup_file.write("uniforms," + ",".join(self.sanitize(field) for field in uniform) + "\n")

                # write instruments
                for instrument in db.get_all_instruments():
                    backup_file.write("instruments," + ",".join(self.sanitize(field) for field in instrument) + "\n")

            QMessageBox.information(self, "Backup", "Backup created successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Something went wrong during backup:\n{e}")
            
    def use_backup(self):
        """
        Open a file dialog to select a previously created backup file,
        clear all existing data, and restore from the file line by line.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Restore Backup", "", "Text Files (*.txt)")
        if not file_path:
            return

        # Wipe existing tables before restore
        db.delete_all_students()
        db.delete_all_uniforms()
        db.delete_all_instruments()

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                section = parts[0]
                fields = parts[1:]

                try:
                    if section == "students":
                        if len(fields) == 19:
                            db.add_student(*fields)
                    elif section == "uniforms":
                        # id, student_id, shako_num, hanger_num, garment_bag, coat_num, pants_num, is_checked_in
                        if len(fields) == 8:
                            db.add_uniform(*fields)
                    elif section == "instruments":
                        # id, student_id, instrument_name, instrument_serial, instrument_case, is_checked_in
                        if len(fields) == 6:
                            db.add_instrument(*fields)
                except Exception as e:
                    QMessageBox.critical(self, "Restore Error", f"Error restoring line:\n{line}\n\n{e}")
                    return

        QMessageBox.information(self, "Restore", "Backup restored successfully!")
        self.refresh_table()


    def import_students_from_csv(self):
        """
        Let user choose a CSV file, parse each row with DictReader,
        sanitize fields, skip invalid IDs, and either update existing
        records or add new ones. Finally, refresh the table.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Students CSV", "", "CSV Files (*.csv)")
        if not file_path:
            return

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                student_id = desanitize(row.get("Student ID", ""))

                # Skip rows with invalid or missing ID
                if not student_id or not student_id.isdigit() or len(student_id) != 9:
                    continue  
                
                # Collect each expected column in order
                fields = [desanitize(row.get(col, "")) for col in [
                    "Student ID", "First Name", "Last Name", "Section", "Phone", "Email",
                    "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #",
                    "Spats Size", "Gloves Size", "Guardian Name", "Guardian Phone",
                    "Instrument Name", "Instrument Serial", "Instrument Case", "Year Came Up"
                ]]

                existing = db.get_student_by_id(student_id)
                if existing:

                    # Update only changed fields to avoid unnecessary writes
                    field_names = [
                        "first_name", "last_name", "section", "phone", "email",
                        "shako_num", "hanger_num", "garment_bag", "coat_num", "pants_num",
                        "spats_size", "gloves_size", "guardian_name", "guardian_phone",
                        "instrument_name", "instrument_serial", "instrument_case", "year_came_up"
                    ]
                    for idx, field_name in enumerate(field_names, start=1):
                        new_value = fields[idx]
                        if new_value and new_value != str(existing[idx]):
                            db.update_student(student_id, field_name, new_value)
                else:

                    # Insert brand-new student record
                    db.add_student(*fields)

        QMessageBox.information(self, "Import", "Student data imported and updated!")
        self.refresh_table()


    def show_printable_results(self, title, message):
        """
        Display a custom dialog containing arbitrary text (e.g., student info,
        outstanding lists), with options to print or close.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout()
        label = QLabel(message)

        # Allow user to select and copy text
        label.setTextInteractionFlags(label.textInteractionFlags() | Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label)

        button_layout = QHBoxLayout()
        print_button = QPushButton("Print")
        close_button = QPushButton("Close")
        button_layout.addWidget(print_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        def handle_print():
            """
            Create a QTextEdit on-the-fly, load the label’s text,
            and send it to the printer object for hardcopy output.
            """
            printer = QPrinter()
            print_dialog = QPrintDialog(printer, dialog)
            if print_dialog.exec():
                # Print the label's text
                text_edit = QTextEdit()
                text_edit.setPlainText(label.text())
                text_edit.print(printer)

        print_button.clicked.connect(handle_print)
        close_button.clicked.connect(dialog.accept)

        dialog.exec()


    def student_to_code_popup(self):
        """
        Prompt for Student ID, choose QR Code or Barcode, generate the
        image in-memory, display it in a dialog with Print, Close, and
        Full Screen options.
        """
        student_id, ok = QInputDialog.getText(self, "Student to Bar/QR code", "Enter Student ID:")
        if not ok or not student_id.strip():
            return
        if not student_id.isdigit() or len(student_id) != 9:
            QMessageBox.warning(self, "Error", "Student ID must be exactly 9 digits.")
            return

        student = db.get_student_by_id(student_id.strip())
        if not student:
            QMessageBox.information(self, "Not Found", "No student found with that ID.")
            return

        # Let user choose code type
        code_type, ok = QInputDialog.getItem(
            self, "Choose Code Type", "Generate:", ["QR Code", "Barcode"], 0, False
        )
        if not ok:
            return

        # Build the info string to encode
        info = f"ID: {student[0]}\nName: {student[2]}, {student[1]}\nSection: {student[3]}\nPhone: {student[4]}"

        # Generate the appropriate image in memory
        if code_type == "QR Code":
            qr_img = qrcode.make(info)
            qr_img = qr_img.convert("RGB")
            buf = io.BytesIO()
            qr_img.save(buf, format="PNG")
            buf.seek(0)
            qimage = QImage.fromData(buf.getvalue())
            pixmap = QPixmap.fromImage(qimage)
        else:
            barcode_class = barcode.get_barcode_class('code128')
            barcode_img = barcode_class(student[0], writer=ImageWriter()).render(writer_options={"write_text": False})
            barcode_img = barcode_img.convert("RGB")
            buf = io.BytesIO()
            barcode_img.save(buf, format="PNG")
            buf.seek(0)
            qimage = QImage.fromData(buf.getvalue())
            pixmap = QPixmap.fromImage(qimage)

        # Build display dialog for the code image
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Student {code_type}")
        layout = QVBoxLayout()
        code_label = QLabel()
        code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scaled_pixmap = pixmap.scaled(256, 256, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        code_label.setPixmap(scaled_pixmap)
        layout.addWidget(code_label, alignment=Qt.AlignmentFlag.AlignCenter)
        button_layout = QHBoxLayout()
        print_button = QPushButton("Print")
        close_button = QPushButton("Close")
        button_layout.addWidget(print_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        def handle_print():
            """
            Print the code image by scaling it to the printer's viewport
            and painting via QPainter.
            """
            printer = QPrinter()
            print_dialog = QPrintDialog(printer, dialog)
            if print_dialog.exec():
                painter = QPainter(printer)
                rect = painter.viewport()
                size = scaled_pixmap.size()
                size.scale(rect.size(), Qt.AspectRatioMode.KeepAspectRatio)
                painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
                painter.setWindow(scaled_pixmap.rect())
                painter.drawPixmap(0, 0, scaled_pixmap)
                painter.end()

        print_button.clicked.connect(handle_print)
        close_button.clicked.connect(dialog.accept)
        dialog.exec()

        full_screen_button = QPushButton("Full Screen")
        button_layout.addWidget(full_screen_button)

        def handle_full_screen():
            """
            Show the full-resolution code image in a maximized dialog.
            """
            fs_dialog = QDialog(self)
            fs_dialog.setWindowTitle("Full Screen Code")
            fs_layout = QVBoxLayout()
            fs_label = QLabel()
            fs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fs_label.setPixmap(pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            fs_layout.addWidget(fs_label)
            fs_dialog.setLayout(fs_layout)
            fs_dialog.showMaximized()
            fs_dialog.exec()

        full_screen_button.clicked.connect(handle_full_screen)



