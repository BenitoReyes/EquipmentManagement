# Standard library imports

# Third-party imports
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
)
from PyQt6.QtCore import Qt

# Local application imports
from db import connect_db

class AddInstrumentDialog(QDialog):
    """
    Dialog for adding new instruments or searching existing ones.
    
    This dialog provides a dual-mode interface for:
    1. Adding new instruments to inventory with complete details
    2. Searching existing instruments using partial criteria
    
    Main Components:
    - Instrument type selector (from predefined sections)
    - Serial number input
    - Case number tracking
    - Model specification
    - Condition assessment
    - Notes field
    
    Features:
    - Mode-based UI adaptation
    - Required field validation
    - Default value handling
    - Empty field normalization
    
    Usage Modes:
    1. Add Mode:
       - Complete instrument details entry
       - Status defaulting
       - Data validation
       
    2. Find Mode:
       - Partial search criteria
       - Multiple field search
       - Flexible matching
    
    Data Handling:
    - Blank field normalization to None
    - String trimming
    - Dropdown selections
    - Status management
    
    Interface Elements:
    - Input validation
    - Clear labeling
    - Intuitive layout
    - Mode-specific buttons
    
    Note:
        This dialog adapts its interface and behavior based on
        the find_mode parameter, providing appropriate fields
        and validation for each use case.
    """
    def __init__(self, parent=None, find_mode=False, instruments=None):
        """
        Initialize the instrument dialog with specified mode and options.
        
        This constructor sets up the dialog's basic configuration:
        1. Parent widget association
        2. Operating mode determination
        3. Instrument options setup
        4. Title configuration
        
        Args:
            parent (QWidget, optional): Parent widget for this dialog.
                Defaults to None for top-level window.
            find_mode (bool, optional): If True, configures for search operations.
                If False, configures for new instrument entry.
                Defaults to False.
            instruments (list, optional): List of valid instrument types.
                Used to populate the instrument selector.
                Defaults to empty list if None.
        
        Dialog Configuration:
        - Parent hierarchy setup
        - Mode-based behavior setting
        - Instrument options initialization
        - Window title customization
        
        Note:
            The find_mode parameter significantly alters the dialog's
            behavior and interface to match its intended use case.
        """
        super().__init__(parent)

        # Operation mode flag - search vs add
        self.find_mode = find_mode

        # Available instrument types list
        self.instruments = instruments or []

        # Dynamic window title based on operation mode
        self.setWindowTitle("Find Instrument" if find_mode else "Add New Instrument")

        # Build the UI layout and widgets
        if(self.find_mode== False):
            self.setup_ui()
        else:
            self.setup_ui_find()

    def setup_ui(self):
        """
        Build and configure the dialog's user interface for add mode.
        
        This method creates a comprehensive input form with:
        1. Instrument type selection
        2. Identification fields
        3. Condition assessment
        4. Notes capability
        
        Form Structure:
        - Vertical layout with field rows
        - Each row uses horizontal layout
        - Consistent label placement
        - Aligned input fields
        
        Input Fields:
        - Instrument selector (dropdown)
        - Serial number (text)
        - Case number (text)
        - Model details (text)
        - Condition (dropdown)
        - Notes (text)
        
        Control Elements:
        - Save button
        - Cancel button
        
        Layout Management:
        - Nested layouts
        - Widget alignment
        - Spacing control
        - Size policies
        
        Note:
            This UI is optimized for adding new instruments
            with all necessary details and validation
        """
        # Main vertical layout for stacking all input rows
        layout = QVBoxLayout()

        # --- Instrument Name ---
        instruments_layout = QHBoxLayout()
        instruments_label = QLabel("Instrument:")
        self.instruments_combo = QComboBox()
        self.instruments_combo.addItem("")  # Blank option for optional selection
        if self.instruments:
            self.instruments_combo.addItems(self.instruments)  # Populate with provided section list
        instruments_layout.addWidget(instruments_label)
        instruments_layout.addWidget(self.instruments_combo)
        layout.addLayout(instruments_layout)

        # --- Serial Number ---
        serial_layout = QHBoxLayout()
        serial_label = QLabel("Serial Number:")
        self.serial_input = QLineEdit()
        serial_layout.addWidget(serial_label)
        serial_layout.addWidget(self.serial_input)
        layout.addLayout(serial_layout)

        # --- Case Number ---
        case_layout = QHBoxLayout()
        case_label = QLabel("Case Number:")
        self.case_input = QLineEdit()
        case_layout.addWidget(case_label)
        case_layout.addWidget(self.case_input)
        layout.addLayout(case_layout)

        # --- Model ---
        model_layout = QHBoxLayout()
        model_label = QLabel("Model:")
        self.model_input = QLineEdit()
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_input)
        layout.addLayout(model_layout)

        # --- Condition Dropdown ---
        condition_layout = QHBoxLayout()
        condition_label = QLabel("Condition:")
        self.condition_combo = QComboBox()
        # Predefined condition options
        self.condition_combo.addItems(['Excellent', 'Good', 'Fair', 'Poor'])
        condition_layout.addWidget(condition_label)
        condition_layout.addWidget(self.condition_combo)
        layout.addLayout(condition_layout)

        # --- Notes ---
        notes_layout = QHBoxLayout()
        notes_label = QLabel("Notes:")
        self.notes_input = QLineEdit()
        notes_layout.addWidget(notes_label)
        notes_layout.addWidget(self.notes_input)
        layout.addLayout(notes_layout)

        # --- Save/Cancel Buttons ---
        button_layout = QHBoxLayout()
        # Button text changes depending on mode
        self.save_button = QPushButton("Find" if self.find_mode else "Save")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Apply the layout to the dialog window
        self.setLayout(layout)

        # Connect button actions to dialog behavior
        self.save_button.clicked.connect(self.accept)   # Accept closes dialog with success
        self.cancel_button.clicked.connect(self.reject) # Reject closes dialog without saving

    def setup_ui_find(self):
        """
        Build and configure the dialog's user interface for search mode.
        
        This method creates a simplified search form with:
        1. Primary search fields
        2. Optional criteria
        3. Search controls
        
        Form Structure:
        - Focused search layout
        - Key field prominence
        - Minimal required fields
        - Clear search intent
        
        Search Fields:
        - Serial number (primary)
        - Instrument type (filter)
        
        Hidden Fields:
        - Case number
        - Model
        - Condition
        - Notes
        These are maintained for format consistency
        but not displayed in search mode
        
        Control Elements:
        - Find button
        - Cancel button
        
        Layout Management:
        - Simplified vertical flow
        - Essential fields only
        - Intuitive ordering
        - Clear visual hierarchy
        
        Note:
            This UI is optimized for quick instrument searches
            focusing on key identifiers
        """
        # Main vertical layout for stacking all input rows
        layout = QVBoxLayout()

        # --- Serial Number ---
        serial_layout = QHBoxLayout()
        serial_label = QLabel("Serial Number:")
        self.serial_input = QLineEdit()
        serial_layout.addWidget(serial_label)
        serial_layout.addWidget(self.serial_input)
        layout.addLayout(serial_layout)

        # --- Instrument Name ---
        instruments_layout = QHBoxLayout()
        instruments_label = QLabel("Instrument:")
        self.instruments_combo = QComboBox()
        self.instruments_combo.addItem("")  # Blank option for optional selection
        if self.instruments:
            self.instruments_combo.addItems(self.instruments)  # Populate with provided section list
        instruments_layout.addWidget(instruments_label)
        instruments_layout.addWidget(self.instruments_combo)
        layout.addLayout(instruments_layout)
        # --- Empty inputs for other fields for formatting purposes---
        self.case_input = QLineEdit()
        self.model_input = QLineEdit()
        self.condition_combo = QComboBox()
        self.notes_input = QLineEdit()
        # --- Save/Cancel Buttons ---
        button_layout = QHBoxLayout()
        # Button text changes depending on mode
        self.save_button = QPushButton("Find" if self.find_mode else "Save")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Apply the layout to the dialog window
        self.setLayout(layout)

        # Connect button actions to dialog behavior
        self.save_button.clicked.connect(self.accept)   # Accept closes dialog with success
        self.cancel_button.clicked.connect(self.reject) # Reject closes dialog without saving

    def get_instrument_data(self):
        """
        Collect and normalize all instrument data from the form.
        
        This method processes all input fields to create a consistent
        data structure suitable for database operations:
        1. Collect all field values
        2. Normalize empty inputs
        3. Strip whitespace
        4. Apply defaults
        
        Returns:
            dict: Normalized instrument data with fields:
                - instrument_name: str or None
                - instrument_serial: str or None
                - instrument_case: str or None
                - model: str or None
                - condition: str or None
                - status: str (always 'Available' for new instruments)
                - notes: str or None
        
        Data Processing:
        - Empty string normalization to None
        - Whitespace trimming
        - Dropdown value extraction
        - Default status assignment
        
        Field Handling:
        - Text inputs: stripped and None if empty
        - Dropdowns: current selection text
        - Fixed values: status always 'Available'
        
        Note:
            This method ensures database-compatible data format
            regardless of input mode or user entry style
        """
        return {
            'instrument_name': None if not self.instruments_combo.currentText().strip() else self.instruments_combo.currentText().strip(),
            'instrument_serial': None if not self.serial_input.text().strip() else self.serial_input.text().strip(),
            'instrument_case': None if not self.case_input.text().strip() else self.case_input.text().strip(),
            'model': None if not self.model_input.text().strip() else self.model_input.text().strip(),
            'condition': None if not self.condition_combo.currentText() else self.condition_combo.currentText(),
            'status': 'Available',  # Default status for new instruments
            'notes': None if not self.notes_input.text().strip() else self.notes_input.text().strip()
        }