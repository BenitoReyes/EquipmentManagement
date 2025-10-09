# Import necessary PyQt6 widgets and layout classes
from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QComboBox, QPushButton, QFormLayout, QMessageBox
)

# Import your database module to perform updates
import db

class EditStudentDialog(QDialog):
    """
    This dialog allows the user to edit an existing student's core details.
    It pre-fills the form with current data and updates the database on save.
    """

    def __init__(self, student_data):
        super().__init__()

        # Set the window title
        self.setWindowTitle("Edit Student Details")

        # Store the student ID for reference during updates
        # student_data is a tuple matching the students table columns:
        # 0: ID, 1: First Name, 2: Last Name, 3: Phone, 4: Email,
        # 5: Year Joined, 6: Status, 7: Guardian Name, 8: Guardian Phone, 9: Section
        self.student_id = student_data[0]

        # Create a form layout to organize fields vertically
        layout = QFormLayout()

        # Dictionary to hold input widgets keyed by field label
        self.inputs = {}

        # Define editable fields and their corresponding index in student_data
        # Each tuple: (label, index in student_data, widget type, options if combo)
        field_defs = [
            ("First Name",      1, "line",  None),
            ("Last Name",       2, "line",  None),
            ("Status",          3, "combo", ["Student", "Former", "Alumni"]),
            ("Phone",           4, "line",  None),
            ("Email",           5, "line",  None),
            ("Guardian Name",   6, "line",  None),
            ("Guardian Phone",  7, "line",  None),
            ("Year Joined",     8, "line",  None),
            ("Section",         9, "combo", [
                "Trumpet", "Trombone", "Euphonium", "French Horn", "Tuba",
                "Flute", "Clarinet", "Saxophone", "Bassoon", "Oboe", "Percussion",
                "Flags"
            ])
        ]



        # Create input widgets and pre-fill them with existing student data
        for label, idx, wtype, options in field_defs:
            if wtype == "combo":
                widget = QComboBox()
                widget.addItems(options)  # Populate dropdown
                current = student_data[idx] or ""
                if current in options:
                    widget.setCurrentText(current)  # Set current value
            else:
                widget = QLineEdit()
                val = student_data[idx]
                widget.setText(str(val) if val is not None else "")  # Pre-fill text

            self.inputs[label] = widget
            layout.addRow(QLabel(f"{label}:"), widget)

        # Add Save Changes button
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.update_student)  # Trigger update logic
        layout.addWidget(save_btn)

        # Apply layout to the dialog
        self.setLayout(layout)

    def update_student(self):
        """
        Validate inputs and update the student record in the database.
        Each field is updated individually using db.update_student().
        """

        # --- Validate Student ID format ---
        sid = str(self.student_id)
        if not sid.isdigit() or len(sid) != 9:
            QMessageBox.warning(self, "Error", "Student ID must be exactly 9 digits.")
            return

        # --- Validate phone number (optional) ---
        phone = self.inputs["Phone"].text().strip()
        if phone and (not phone.isdigit() or len(phone) != 10):
            QMessageBox.warning(self, "Error", "Phone must be 10 digits or blank.")
            return

        # --- Validate guardian phone number (optional) ---
        gphone = self.inputs["Guardian Phone"].text().strip()
        if gphone and (not gphone.isdigit() or len(gphone) != 10):
            QMessageBox.warning(self, "Error", "Guardian Phone must be 10 digits or blank.")
            return

        # --- Map field labels to database column names ---
        FIELD_MAPPING = {
            "First Name":     "first_name",
            "Last Name":      "last_name",
            "Phone":          "phone",
            "Email":          "email",
            "Year Joined":    "year_came_up",
            "Status":         "status",
            "Guardian Name":  "guardian_name",
            "Guardian Phone": "guardian_phone",
            "Section":        "section"
        }

        # --- Update each field in the database ---
        for label, widget in self.inputs.items():
            col = FIELD_MAPPING[label]
            # Get value from widget depending on type
            if isinstance(widget, QComboBox):
                val = widget.currentText()
            else:
                val = widget.text().strip()
            # Update the field in the database
            db.update_student(self.student_id, col, val)

        # Show success message and close dialog
        QMessageBox.information(self, "Success", "Student details updated!")
        self.accept()