from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QComboBox,
    QPushButton, QFormLayout, QMessageBox
)
import db

class AddStudentDialog(QDialog):
    """
    Dialog for adding a new student.
    Collects:
      - Student ID (9 digits)
      - First Name, Last Name
      - Phone (10 digits, optional)
      - Email
      - Year Joined
      - Status (Student, Former, Alumni)
      - Guardian Name, Guardian Phone (10 digits, optional)
      - Section (dropdown)
    On submit, validates inputs and calls db.add_student().
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Student")

        layout = QFormLayout()
        self.inputs = {}

        # Create input widgets
        self.inputs["Student ID"] = QLineEdit()
        self.inputs["First Name"] = QLineEdit()
        self.inputs["Last Name"] = QLineEdit()
        self.inputs["Phone"] = QLineEdit()
        self.inputs["Email"] = QLineEdit()
        self.inputs["Year Joined"] = QLineEdit()

        # Status dropdown
        self.inputs["Status"] = QComboBox()
        self.inputs["Status"].addItems(["Student", "Former", "Alumni"])

        self.inputs["Guardian Name"] = QLineEdit()
        self.inputs["Guardian Phone"] = QLineEdit()

        # Section dropdown
        sections = [
        "Trumpet", "Trombone", "Euphonium", "French Horn", "Tuba",
        "Flute", "Clarinet", "Saxophone", "Bassoon", "Oboe", "Percussion",
        "Flags"
        ]
        self.inputs["Section"] = QComboBox()
        self.inputs["Section"].addItems(sections)


        # Add fields to the form layout
        for label, widget in self.inputs.items():
            layout.addRow(QLabel(f"{label}:"), widget)

        # Submit button
        add_btn = QPushButton("Add Student")
        add_btn.clicked.connect(self.add_student)
        layout.addWidget(add_btn)

        self.setLayout(layout)

    def add_student(self):
        """
        Validate inputs and insert a new student record.
        Uses db.add_student() with uniform/instrument defaults.
        """
        # Retrieve and trim values
        sid = self.inputs["Student ID"].text().strip()
        first = self.inputs["First Name"].text().strip()
        last = self.inputs["Last Name"].text().strip()
        phone = self.inputs["Phone"].text().strip()
        email = self.inputs["Email"].text().strip()
        year = self.inputs["Year Joined"].text().strip()
        status = self.inputs["Status"].currentText()
        guardian = self.inputs["Guardian Name"].text().strip()
        gphone = self.inputs["Guardian Phone"].text().strip()
        section = self.inputs["Section"].currentText()

        # Validate Student ID
        if not sid.isdigit() or len(sid) != 9:
            QMessageBox.warning(self, "Validation Error",
                                "Student ID must be exactly 9 digits.")
            return

        # Validate required names
        if not first or not last:
            QMessageBox.warning(self, "Validation Error",
                                "First Name and Last Name cannot be blank.")
            return

        # Validate phone numbers (optional)
        if phone and (not phone.isdigit() or len(phone) != 10):
            QMessageBox.warning(self, "Validation Error",
                                "Phone must be exactly 10 digits or left blank.")
            return
        if gphone and (not gphone.isdigit() or len(gphone) != 10):
            QMessageBox.warning(self, "Validation Error",
                                "Guardian Phone must be exactly 10 digits or left blank.")
            return

        # Insert student; uniform/instrument fields default to None
        try:
            db.add_student(
                sid, first, last, phone or None, email or None, year or None,
                status, guardian or None, gphone or None, section
            )
            QMessageBox.information(self, "Success",
                                    f"Student {first} {last} added successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error",
                                 f"Failed to add student:\n{e}")