from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QFormLayout, QMessageBox
import db  # Database operations


class AddStudentDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Student")
        self.setGeometry(300, 300, 400, 500)

        layout = QFormLayout()
        self.inputs = {}

        fields = ["First Name", "Last Name", "Student ID", "Section", "Phone", "Email",
                  "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #", "Spats Size",
                  "Gloves Size", "Guardian Name", "Guardian Phone"]

        for field in fields:
            self.inputs[field] = QLineEdit()
            layout.addRow(QLabel(field + ":"), self.inputs[field])

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.add_student)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def add_student(self):
        """Handles adding a student to the database."""
        values = {field: self.inputs[field].text().strip() for field in self.inputs}

        if not values["First Name"] or not values["Last Name"] or not values["Student ID"]:
            QMessageBox.warning(self, "Error", "First Name, Last Name, and Student ID are required!")
            return

        db.add_student(*values.values())
        QMessageBox.information(self, "Success", "Student added successfully!")
        self.accept()
