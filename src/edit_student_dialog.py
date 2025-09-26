from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QComboBox, QPushButton, QFormLayout, QMessageBox
)
import db

class EditStudentDialog(QDialog):
    """
    Dialog for editing an existing student's core details:
    first name, last name, phone, email, year joined, status,
    guardian info, and section.
    """

    def __init__(self, student_data):
        super().__init__()

        self.setWindowTitle("Edit Student Details")
        # student_data indexes match the students table columns:
        # 0:id, 1:first_name, 2:last_name, 3:phone, 4:email,
        # 5:year_came_up, 6:status, 7:guardian_name, 8:guardian_phone, 9:section
        self.student_id = student_data[0]

        layout = QFormLayout()
        self.inputs = {}

        # Define fields: (label, index, widget_type, [options])
        field_defs = [
            ("First Name",      1, "line",  None),
            ("Last Name",       2, "line",  None),
            ("Phone",           3, "line",  None),
            ("Email",           4, "line",  None),
            ("Year Joined",     5, "line",  None),
            ("Status",          6, "combo", ["Student", "Former", "Alumni"]),
            ("Guardian Name",   7, "line",  None),
            ("Guardian Phone",  8, "line",  None),
            ("Section", 9, "combo", [
            "Trumpet", "Trombone", "Euphonium", "French Horn", "Tuba",
            "Flute", "Clarinet", "Saxophone", "Bassoon", "Oboe", "Percussion",
            "Flags"
            ])
        ]

        # Create input widgets per definition and prefill with student_data
        for label, idx, wtype, options in field_defs:
            if wtype == "combo":
                widget = QComboBox()
                widget.addItems(options)
                current = student_data[idx] or ""
                if current in options:
                    widget.setCurrentText(current)
            else:  # QLineEdit
                widget = QLineEdit()
                val = student_data[idx]
                widget.setText(str(val) if val is not None else "")

            self.inputs[label] = widget
            layout.addRow(QLabel(f"{label}:"), widget)

        # Save Changes button
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.update_student)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def update_student(self):
        """
        Validate inputs and write updates to the database.
        Runs field-by-field via db.update_student().
        """
        # Validate ID format
        sid = str(self.student_id)
        if not sid.isdigit() or len(sid) != 9:
            QMessageBox.warning(self, "Error", "Student ID must be exactly 9 digits.")
            return

        # Phone validation
        phone = self.inputs["Phone"].text().strip()
        if phone and (not phone.isdigit() or len(phone) != 10):
            QMessageBox.warning(self, "Error", "Phone must be 10 digits or blank.")
            return

        # Guardian phone validation
        gphone = self.inputs["Guardian Phone"].text().strip()
        if gphone and (not gphone.isdigit() or len(gphone) != 10):
            QMessageBox.warning(self, "Error", "Guardian Phone must be 10 digits or blank.")
            return

        # Field label → DB column mapping
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

        # Push updates for each field
        for label, widget in self.inputs.items():
            col = FIELD_MAPPING[label]
            if isinstance(widget, QComboBox):
                val = widget.currentText()
            else:
                val = widget.text().strip()
            # Let db.update_student handle empty→NULL conversion
            db.update_student(self.student_id, col, val)

        QMessageBox.information(self, "Success", "Student details updated!")
        self.accept()