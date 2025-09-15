import db
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QFormLayout, QMessageBox
# Define a dialog window for adding a new student
class AddStudentDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Set window title and dimensions
        self.setWindowTitle("Add Student")
        self.setGeometry(300, 300, 400, 500)

        # Create a form layout to organize labels and input fields
        layout = QFormLayout()

        # Dictionary to store references to each input field
        self.inputs = {}

        # Define all fields to be collected from the user
        fields = [
            "Student ID", "First Name", "Last Name", "Section", "Phone", "Email",
            "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #",
            "Spats Size", "Gloves Size", "Guardian Name", "Guardian Phone",
            "Instrument Name", "Instrument Serial", "Instrument Case", "Year Came up"
        ]

        # Dynamically create a label and input field for each entry
        for field in fields:
            if isinstance(field, tuple):
                # For instrument fields, add a label without a corresponding input field
                layout.addRow(QLabel(field[0] + ":"))
            else:
                self.inputs[field] = QLineEdit() # Create a text input
                layout.addRow(QLabel(field + ":"), self.inputs[field]) # Add label and input to layout

        # Create a submit button and connect it to the add_student method
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.add_student)
        layout.addWidget(self.submit_button) # Add button to layout

        # Apply the layout to the dialog
        self.setLayout(layout)
        
    # Method triggered when the user clicks "Submit" 
    def add_student(self):
        """Handles adding a student to the database."""

        # Extract and sanitize the Student ID
        student_id = self.inputs["Student ID"].text().strip()

        # Check if the student ID already exists in the database
        if db.get_student_by_id(student_id):
            QMessageBox.warning(self, "Error", "A student with that ID already exists!")
            return  # Do NOT close the dialog
        
        # Collect all input values in the same order as defined in the fields list
        values = [self.inputs[field].text().strip() for field in self.inputs]
        
        # Extract specific fields for validation
        first_name = values[1]
        last_name = values[2]
        phone = values[4]
        guardian_phone = values[14] 

        # Validate Student ID: must be exactly 9 digits
        if not student_id.isdigit() or len(student_id) != 9:
            QMessageBox.warning(self, "Error", "Student ID must be exactly 9 digits.")
            return

        # Validate Phone Number
        if phone and (not phone.isdigit() or len(phone) != 10):
            QMessageBox.warning(self, "Error", "Phone number must be exactly 10 digits.")
            return

        # Validate Guardian Phone Number
        if guardian_phone and(not guardian_phone.isdigit() or len(guardian_phone) != 10):
            QMessageBox.warning(self, "Error", "Guardian phone number must be exactly 10 digits.")
            return
        # Ensure required fields are not empty
        if not first_name or not last_name or not student_id:
            QMessageBox.warning(self, "Error", "First Name, Last Name, and Student ID are required!")
            return
        
        db.add_student(*values)  # Add to database
        QMessageBox.information(self, "Success", "Student added successfully!")
        self.accept()  # Close dialog
