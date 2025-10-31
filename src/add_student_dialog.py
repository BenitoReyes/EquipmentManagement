# Standard library imports

# Third-party imports
from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QComboBox,
    QPushButton, QFormLayout, QMessageBox
)

# Local application imports
import db

class AddStudentDialog(QDialog):
    """
    Dialog for adding new students with comprehensive information collection.
    
    This dialog implements a form-based interface for:
    1. Personal information collection
    2. Contact details management
    3. Section assignment
    4. Status tracking
    
    Form Categories:
    - Student Identification:
      * Student ID (9 digits)
      * First and Last Name
      * Year Joined
      
    - Contact Information:
      * Phone Number (10 digits)
      * Email Address
      * Status Selection
      
    - Guardian Details:
      * Guardian Name
      * Guardian Phone (10 digits)
      
    - Program Assignment:
      * Section Selection (Instrument/Unit)
      * Status Tracking
    
    Validation Features:
    - Required field checking
    - ID format validation
    - Phone number formatting
    - Data type verification
    
    Database Integration:
    - Direct db.add_student() connection
    - Error handling
    - Success confirmation
    - Duplicate prevention
    
    Interface Elements:
    - Form layout structure
    - Clear field labeling
    - Input validation
    - Status messages
    
    Note:
        This dialog enforces data integrity through
        comprehensive validation before database insertion
    """

    def __init__(self):
        """
        Initialize and configure the student addition dialog.
        
        This constructor sets up:
        1. Basic dialog configuration
        2. Form layout structure
        3. Input field creation
        4. Widget organization
        
        Dialog Setup:
        - Window title configuration
        - Form layout initialization
        - Widget storage system
        - Field organization
        
        Input Fields Created:
        - Text entry fields
        - Dropdown selectors
        - Status indicators
        - Section choosers
        
        Layout Management:
        - Vertical form structure
        - Label alignment
        - Widget spacing
        - Visual hierarchy
        
        Note:
            All widgets are stored in self.inputs dictionary
            for easy access during validation and submission
        """
        super().__init__()

        # Configure window title
        self.setWindowTitle("Add New Student")

        # Initialize form layout for organized field presentation
        layout = QFormLayout()

        # Central widget storage for validation and data collection
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
        Process form data and add new student to database.
        
        This method implements a complete data processing workflow:
        1. Data collection and cleaning
        2. Field validation
        3. Database insertion
        4. Result handling
        
        Validation Steps:
        - Student ID:
          * Must be exactly 9 digits
          * All characters must be numeric
        
        - Name Fields:
          * First name required
          * Last name required
          * Non-empty after trimming
        
        - Phone Numbers:
          * Optional fields
          * When provided: 10 digits
          * All characters numeric
        
        - Other Fields:
          * Email optional
          * Year optional
          * Section required
          * Status required
        
        Database Operation:
        - Null handling for optional fields
        - Exception management
        - Success confirmation
        - Error reporting
        
        User Feedback:
        - Validation error messages
        - Success confirmations
        - Database error reporting
        - Dialog closure on success
        
        Note:
            This method ensures data integrity through
            comprehensive validation before attempting
            database operations
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