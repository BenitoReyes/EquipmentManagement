from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QFormLayout, QMessageBox
import db
# Define a dialog window for editing an existing student's details
class EditStudentDialog(QDialog):
    def __init__(self, student_data):
        super().__init__()

        self.setWindowTitle("Edit Student Details")
        # Store the student ID for reference during updates
        self.student_id = student_data[0]  # Assuming ID is at index 0

        # Create a form layout to organize labels and input fields
        layout = QFormLayout()

        # Dictionary to hold QLineEdit widgets keyed by field name
        self.inputs = {}

        # Define editable fields and their corresponding index in student_data
        fields = [
            ("First Name", 1), ("Last Name", 2), ("Section", 3), ("Phone", 4), ("Email", 5),
            ("Shako #", 6), ("Hanger #", 7), ("Garment Bag", 8), ("Coat #", 9), ("Pants #", 10),
            ("Spats Size", 11), ("Gloves Size", 12), ("Guardian Name", 13), ("Guardian Phone", 14),
            ("Instrument Name", 15), ("Instrument Serial", 16), ("Instrument Case", 17),
            ("Year Came up", 18)
        ]

        # Create input fields and pre-fill them with existing student data
        for field_name, index in fields:
            self.inputs[field_name] = QLineEdit()

            # Populate with existing value or empty string if None
            self.inputs[field_name].setText(str(student_data[index]) if student_data[index] is not None else "")
            layout.addRow(QLabel(field_name + ":"), self.inputs[field_name])

        # Create a submit button and connect it to the update logic
        self.submit_button = QPushButton("Save Changes")
        self.submit_button.clicked.connect(self.update_student)
        layout.addWidget(self.submit_button)

        # Apply the layout to the dialog
        self.setLayout(layout)

    # Method to validate and save updated student details
    def update_student(self):
        """Save updated details with validation."""
        
        # Maps display field names to database column names
        FIELD_MAPPING = {
            "First Name": "first_name",
            "Last Name": "last_name",
            "Section": "section",
            "Phone": "phone",
            "Email": "email",
            "Shako #": "shako_num",
            "Hanger #": "hanger_num",
            "Garment Bag": "garment_bag",
            "Coat #": "coat_num",
            "Pants #": "pants_num",
            "Spats Size": "spats_size",
            "Gloves Size": "gloves_size",
            "Guardian Name": "guardian_name",
            "Guardian Phone": "guardian_phone",
            "Instrument Name": "instrument_name",
            "Instrument Serial": "instrument_serial",
            "Instrument Case": "instrument_case",
            "Year Came up": "year_came_up"
        }

        # Validate Student ID
        if not str(self.student_id).isdigit() or len(str(self.student_id)) != 9:
            QMessageBox.warning(self, "Error", "Student ID must be exactly 9 digits.")
            return

        # Validate Phone Number if not empty
        phone = self.inputs["Phone"].text().strip()
        if phone and (not phone.isdigit() or len(phone) != 10):
            QMessageBox.warning(self, "Error", "Phone number must be exactly 10 digits or left blank.")
            return

        # Validate Guardian Phone Number if not empty
        guardian_phone = self.inputs["Guardian Phone"].text().strip()
        if guardian_phone and (not guardian_phone.isdigit() or len(guardian_phone) != 10):
            QMessageBox.warning(self, "Error", "Guardian phone number must be exactly 10 digits or left blank.")
            return

        # Update all fields
        for field, input_widget in self.inputs.items():
            value = input_widget.text().strip()
            db.update_student(self.student_id, FIELD_MAPPING[field], value)

        QMessageBox.information(self, "Success", "Student details updated!")
        self.accept()
