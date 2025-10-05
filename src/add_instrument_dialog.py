# Import necessary PyQt6 widgets and layout classes
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
)
from PyQt6.QtCore import Qt

# Import database connection utility (not used directly here, but may be useful later)
from db import connect_db

# Define a dialog window for adding or searching for an instrument
class AddInstrumentDialog(QDialog):
    def __init__(self, parent=None, find_mode=False, instruments=None):
        super().__init__(parent)

        # If True, this dialog is used to search for instruments instead of adding them
        self.find_mode = find_mode

        # List of valid instrument sections (e.g., Trumpet, Percussion, Flags)
        self.instruments = instruments or []

        # Set the window title based on mode
        self.setWindowTitle("Find Instrument" if find_mode else "Add New Instrument")

        # Build the UI layout and widgets
        if(self.find_mode== False):
            self.setup_ui()
        else:
            self.setup_ui_find()

    def setup_ui(self):
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
        Collect all input values and return them as a dictionary.
        Empty fields are converted to None to match database expectations.
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