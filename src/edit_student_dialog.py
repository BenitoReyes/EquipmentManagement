from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QFormLayout, QMessageBox
import db

class EditStudentDialog(QDialog):
    def __init__(self, student_data):
        super().__init__()

        self.setWindowTitle("Edit Student Details")
        self.student_id = student_data[0]  # Assuming ID is at index 0

        layout = QFormLayout()
        self.inputs = {}

        fields = [
            ("First Name", 1), ("Last Name", 2), ("Section", 3), ("Phone", 4), ("Email", 5),
            ("Shako #", 6), ("Hanger #", 7), ("Garment Bag", 8), ("Coat #", 9), ("Pants #", 10),
            ("Spats Size", 11), ("Gloves Size", 12), ("Guardian Name", 13), ("Guardian Phone", 14)
        ]

        for field_name, index in fields:
            self.inputs[field_name] = QLineEdit()
            self.inputs[field_name].setText(str(student_data[index]))  # Pre-fill with current data
            layout.addRow(QLabel(field_name + ":"), self.inputs[field_name])

        self.submit_button = QPushButton("Save Changes")
        self.submit_button.clicked.connect(self.update_student)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def update_student(self):
        """Step 4: Save updated details."""
        FIELD_MAPPING = {
        "Shako #": "shako_num",
        "Hanger #": "hanger_num",
        "Garment Bag": "garment_bag",
        "Coat #": "coat_num",
        "Pants #": "pants_num",
        "Spats Size": "spats_size",
        "Gloves Size": "gloves_size",
        "Guardian Name": "guardian_name",
        "Guardian Phone": "guardian_phone"
        }

        for field, input_widget in self.inputs.items():
            db.update_student(self.student_id, FIELD_MAPPING.get(field, field.lower().replace(" ", "_")), input_widget.text().strip())
        QMessageBox.information(self, "Success", "Student details updated!")
        self.accept()