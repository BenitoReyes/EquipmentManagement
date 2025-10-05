# Import necessary PyQt6 widgets for building the form
from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QComboBox,
    QPushButton, QFormLayout, QMessageBox
)

# Import your database module to insert the student record
import db

class AddStudentDialog(QDialog):
    """
    This dialog allows the user to add a new student to the system.
    It collects personal info, contact details, and section assignment.
    On submission, it validates the inputs and calls db.add_student().
    """

    def __init__(self):
        super().__init__()

        # Set the window title
        self.setWindowTitle("Add New Student")

        # Create a form layout to organize input fields vertically
        layout = QFormLayout()

        # Dictionary to store all input widgets by label
        self.inputs = {}

        # --- Create input fields for student information ---
        self.inputs["Student ID"] = QLineEdit()       # Must be 9 digits
        self.inputs["First Name"] = QLineEdit()
        self.inputs["Last Name"] = QLineEdit()
        self.inputs["Phone"] = QLineEdit()            # Optional, 10 digits
        self.inputs["Email"] = QLineEdit()
        self.inputs["Year Joined"] = QLineEdit()      # Optional

        # --- Dropdown for student status ---
        self.inputs["Status"] = QComboBox()
        self.inputs["Status"].addItems(["Student", "Former", "Alumni"])

        # --- Guardian contact info ---
        self.inputs["Guardian Name"] = QLineEdit()
        self.inputs["Guardian Phone"] = QLineEdit()   # Optional, 10 digits

        # --- Dropdown for instrument section ---
        sections = [
            "Trumpet", "Trombone", "Euphonium", "French Horn", "Tuba",
            "Flute", "Clarinet", "Saxophone", "Bassoon", "Oboe", "Percussion",
            "Flags"
        ]
        self.inputs["Section"] = QComboBox()
        self.inputs["Section"].addItems(sections)

        # --- Add all fields to the form layout ---
        for label, widget in self.inputs.items():
            layout.addRow(QLabel(f"{label}:"), widget)

        # --- Add Student button ---
        add_btn = QPushButton("Add Student")
        add_btn.clicked.connect(self.add_student)  # Trigger validation and save
        layout.addWidget(add_btn)

        # Apply layout to the dialog
        self.setLayout(layout)

    def add_student(self):
        """
        Validate all inputs and insert the student into the database.
        If any required field is invalid, show a warning.
        """

        # --- Retrieve and clean input values ---
        sid      = self.inputs["Student ID"].text().strip()
        first    = self.inputs["First Name"].text().strip()
        last     = self.inputs["Last Name"].text().strip()
        phone    = self.inputs["Phone"].text().strip()
        email    = self.inputs["Email"].text().strip()
        year     = self.inputs["Year Joined"].text().strip()
        status   = self.inputs["Status"].currentText()
        guardian = self.inputs["Guardian Name"].text().strip()
        gphone   = self.inputs["Guardian Phone"].text().strip()
        section  = self.inputs["Section"].currentText()

        # --- Validate Student ID ---
        if not sid.isdigit() or len(sid) != 9:
            QMessageBox.warning(self, "Validation Error",
                                "Student ID must be exactly 9 digits.")
            return

        # --- Validate required name fields ---
        if not first or not last:
            QMessageBox.warning(self, "Validation Error",
                                "First Name and Last Name cannot be blank.")
            return

        # --- Validate phone number (optional) ---
        if phone and (not phone.isdigit() or len(phone) != 10):
            QMessageBox.warning(self, "Validation Error",
                                "Phone must be exactly 10 digits or left blank.")
            return

        # --- Validate guardian phone number (optional) ---
        if gphone and (not gphone.isdigit() or len(gphone) != 10):
            QMessageBox.warning(self, "Validation Error",
                                "Guardian Phone must be exactly 10 digits or left blank.")
            return

        # --- Attempt to insert the student record into the database ---
        try:
            db.add_student(
                sid,
                first,
                last,
                phone or None,
                email or None,
                year or None,
                status,
                guardian or None,
                gphone or None,
                section
            )
            # Show success message and close dialog
            QMessageBox.information(self, "Success",
                                    f"Student {first} {last} added successfully.")
            self.accept()
        except Exception as e:
            # Show error message if database insert fails
            QMessageBox.critical(self, "Database Error",
                                 f"Failed to add student:\n{e}")