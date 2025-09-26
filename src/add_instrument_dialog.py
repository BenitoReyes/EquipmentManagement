from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox)
from PyQt6.QtCore import Qt
from db import connect_db

class AddInstrumentDialog(QDialog):
    def __init__(self, parent=None, find_mode=False):
        super().__init__(parent)
        self.find_mode = find_mode
        self.setWindowTitle("Find Instrument" if find_mode else "Add New Instrument")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Instrument Name
        name_layout = QHBoxLayout()
        name_label = QLabel("Instrument Name:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Serial Number
        serial_layout = QHBoxLayout()
        serial_label = QLabel("Serial Number:")
        self.serial_input = QLineEdit()
        serial_layout.addWidget(serial_label)
        serial_layout.addWidget(self.serial_input)
        layout.addLayout(serial_layout)

        # Case Number
        case_layout = QHBoxLayout()
        case_label = QLabel("Case Number:")
        self.case_input = QLineEdit()
        case_layout.addWidget(case_label)
        case_layout.addWidget(self.case_input)
        layout.addLayout(case_layout)

        # Model
        model_layout = QHBoxLayout()
        model_label = QLabel("Model:")
        self.model_input = QLineEdit()
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_input)
        layout.addLayout(model_layout)

        # Condition
        condition_layout = QHBoxLayout()
        condition_label = QLabel("Condition:")
        self.condition_combo = QComboBox()
        self.condition_combo.addItems(['Excellent', 'Good', 'Fair', 'Poor'])
        condition_layout.addWidget(condition_label)
        condition_layout.addWidget(self.condition_combo)
        layout.addLayout(condition_layout)

        # Notes
        notes_layout = QHBoxLayout()
        notes_label = QLabel("Notes:")
        self.notes_input = QLineEdit()
        notes_layout.addWidget(notes_label)
        notes_layout.addWidget(self.notes_input)
        layout.addLayout(notes_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Find" if self.find_mode else "Save")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect buttons
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_instrument_data(self):
        return {
            'instrument_name': None if not self.name_input.text().strip() else self.name_input.text().strip(),
            'instrument_serial': None if not self.serial_input.text().strip() else self.serial_input.text().strip(),
            'instrument_case': None if not self.case_input.text().strip() else self.case_input.text().strip(),
            'model': None if not self.model_input.text().strip() else self.model_input.text().strip(),
            'condition': None if not self.condition_combo.currentText() else self.condition_combo.currentText(),
            'status': 'Available',
            'notes': None if not self.notes_input.text().strip() else self.notes_input.text().strip()
        }