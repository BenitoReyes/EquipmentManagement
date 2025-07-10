import db
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QFormLayout, QMessageBox

class AddStudentDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Student")
        self.setGeometry(300, 300, 400, 500)

        layout = QFormLayout()
        self.inputs = {}

        fields = ["Student ID", "First Name", "Last Name", "Section", "Phone", "Email",
                  "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #", 
                  "Spats Size", "Gloves Size", "Guardian Name", "Guardian Phone", 
                  "Instrument Name", "Instrument Serial", "Instrument Case"]

        for field in fields:
            if isinstance(field, tuple):
                # For instrument fields, add a label without a corresponding input field
                layout.addRow(QLabel(field[0] + ":"))
            else:
                self.inputs[field] = QLineEdit()
                layout.addRow(QLabel(field + ":"), self.inputs[field])

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.add_student)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def add_student(self):
        """Handles adding a student to the database."""
        values = [self.inputs[field].text().strip() for field in self.inputs]

        student_id = values[0]
        first_name = values[1]
        last_name = values[2]
        phone = values[4]
        guardian_phone = values[14] 

        # Validate Student ID
        if not student_id.isdigit() or len(student_id) != 9:
            QMessageBox.warning(self, "Error", "Student ID must be exactly 9 digits.")
            return

        # Validate Phone Number
        if not phone.isdigit() or len(phone) != 10:
            QMessageBox.warning(self, "Error", "Phone number must be exactly 10 digits.")
            return

        # Validate Guardian Phone Number
        if not guardian_phone.isdigit() or len(guardian_phone) != 10:
            QMessageBox.warning(self, "Error", "Guardian phone number must be exactly 10 digits.")
            return

        if not first_name or not last_name or not student_id:
            QMessageBox.warning(self, "Error", "First Name, Last Name, and Student ID are required!")
            return

        db.add_student(*values)  # Add to database
        QMessageBox.information(self, "Success", "Student added successfully!")
        self.accept()  # Close dialog
