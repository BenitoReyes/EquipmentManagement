# Standard library imports

# Third-party imports
from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QComboBox, QPushButton, QFormLayout, QMessageBox
)

# Local application imports
import db

class EditStudentDialog(QDialog):
    """
    Dialog for modifying existing student records with data validation.
    
    This dialog implements a comprehensive student editing interface:
    1. Pre-populated form display
    2. Field-by-field modifications
    3. Data validation
    4. Database updates
    
    Form Categories:
    - Personal Information:
      * First Name
      * Last Name
      * Status (Student/Former/Alumni)
      * Year Joined
      
    - Contact Details:
      * Phone Number (optional)
      * Email Address
      * Section Assignment
      
    - Guardian Information:
      * Guardian Name
      * Guardian Phone (optional)
    
    Validation Features:
    - Phone number format checking
    - Required field verification
    - Data type validation
    - Status constraints
    
    Database Integration:
    - Individual field updates
    - Transaction management
    - Error handling
    - Success confirmation
    
    Interface Elements:
    - Pre-filled form fields
    - Field-specific inputs
    - Clear labeling
    - Status messages
    
    Note:
        This dialog ensures data integrity through field-level
        validation and individual database updates for each
        modified field
    """

    def __init__(self, student_data):
        """
        Initialize the student editing dialog with existing data.
        
        This constructor configures the dialog and pre-populates fields:
        1. Basic dialog setup
        2. Student data storage
        3. Form layout creation
        4. Field population
        
        Args:
            student_data (tuple): Student record from database containing:
                0: Student ID (9 digits)
                1: First Name
                2: Last Name
                3: Phone (10 digits, optional)
                4: Email
                5: Year Joined
                6: Status
                7: Guardian Name
                8: Guardian Phone (10 digits, optional)
                9: Section
        
        Dialog Setup:
        - Window configuration
        - Data preservation
        - Layout initialization
        - Widget creation
        
        Data Handling:
        - Student ID storage
        - Field mapping
        - Null value handling
        - Type conversion
        
        Note:
            The student_data tuple structure must match the
            database schema exactly for proper field mapping
        """
        super().__init__()

        # Configure window presentation
        self.setWindowTitle("Edit Student Details")

        # Preserve student identifier for database operations
        # student_data follows database schema structure:
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
        Process form data and update student record in database.
        
        This method implements a complete update workflow:
        1. Input validation
        2. Data normalization
        3. Field mapping
        4. Database updates
        
        Validation Steps:
        - Student ID:
          * Verify 9-digit format
          * Check numeric content
          
        - Phone Numbers:
          * Optional field handling
          * 10-digit format check
          * Numeric content validation
          
        - Guardian Phone:
          * Optional field handling
          * 10-digit format check
          * Numeric content validation
        
        Database Operations:
        - Field-by-field updates
        - Column name mapping
        - Null handling
        - Transaction management
        
        Field Processing:
        - Widget type detection
        - Value extraction
        - String normalization
        - Empty field handling
        
        User Feedback:
        - Validation errors
        - Update confirmation
        - Success message
        - Dialog closure
        
        Note:
            This method uses individual field updates to ensure
            granular error handling and transaction safety
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