# Import necessary PyQt6 widgets and layout classes
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSpinBox
)
from PyQt6.QtCore import Qt

# Import database connection utility (not used directly here, but may be useful later)
from db import connect_db

# Define a dialog window for adding or searching for a uniform
class AddUniformDialog(QDialog):
    def __init__(self, parent=None, find_mode=False):
        super().__init__(parent)

        # If True, this dialog is used to search for uniforms instead of adding them
        self.find_mode = find_mode

        # Set the window title depending on mode
        self.setWindowTitle("Find Uniform" if find_mode else "Add New Uniform")

        # Build the UI layout and widgets
        if(self.find_mode== False):
            self.setup_ui()
        else:
            self.setup_ui_search()

    def setup_ui(self):
        # Main vertical layout to stack all input rows
        layout = QVBoxLayout()

        # --- Shako Number ---
        shako_layout = QHBoxLayout()
        shako_label = QLabel("Shako Number:")
        self.shako_input = QSpinBox()              # SpinBox allows only numeric input
        self.shako_input.setRange(0, 9999)         # Acceptable range for shako numbers
        shako_layout.addWidget(shako_label)
        shako_layout.addWidget(self.shako_input)
        layout.addLayout(shako_layout)

        # --- Hanger Number ---
        hanger_layout = QHBoxLayout()
        hanger_label = QLabel("Hanger Number:")
        self.hanger_input = QSpinBox()
        self.hanger_input.setRange(0, 9999)
        hanger_layout.addWidget(hanger_label)
        hanger_layout.addWidget(self.hanger_input)
        layout.addLayout(hanger_layout)

        # --- Coat Number ---
        coat_layout = QHBoxLayout()
        coat_label = QLabel("Coat Number:")
        self.coat_input = QSpinBox()
        self.coat_input.setRange(0, 9999)
        coat_layout.addWidget(coat_label)
        coat_layout.addWidget(self.coat_input)
        layout.addLayout(coat_layout)

        # --- Pants Number ---
        pants_layout = QHBoxLayout()
        pants_label = QLabel("Pants Number:")
        self.pants_input = QSpinBox()
        self.pants_input.setRange(0, 9999)
        pants_layout.addWidget(pants_label)
        pants_layout.addWidget(self.pants_input)
        layout.addLayout(pants_layout)

        # --- Garment Bag Number ---
        bag_layout = QHBoxLayout()
        bag_label = QLabel("Garment Bag Number:")
        self.bag_input = QLineEdit()               # Free text input for bag ID
        bag_layout.addWidget(bag_label)
        bag_layout.addWidget(self.bag_input)
        layout.addLayout(bag_layout)

        # --- Notes field ---
        notes_layout = QHBoxLayout()
        notes_label = QLabel("Notes:")
        self.notes_input = QLineEdit()             # Optional notes about the uniform
        notes_layout.addWidget(notes_label)
        notes_layout.addWidget(self.notes_input)
        layout.addLayout(notes_layout)

        # --- Save and Cancel buttons ---
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

    def setup_ui_search(self):
        # Main vertical layout to stack all input rows
        layout = QVBoxLayout()

        # --- Shako Number ---
        shako_layout = QHBoxLayout()
        shako_label = QLabel("Shako Number:")
        self.shako_input = QSpinBox()              # SpinBox allows only numeric input
        self.shako_input.setRange(0, 9999)         # Acceptable range for shako numbers
        shako_layout.addWidget(shako_label)
        shako_layout.addWidget(self.shako_input)
        layout.addLayout(shako_layout)

        # --- Hanger Number ---
        #hanger empty for search
        self.hanger_input = QSpinBox()

        # --- Coat Number ---
        coat_layout = QHBoxLayout()
        coat_label = QLabel("Coat Number:")
        self.coat_input = QSpinBox()
        self.coat_input.setRange(0, 9999)
        coat_layout.addWidget(coat_label)
        coat_layout.addWidget(self.coat_input)
        layout.addLayout(coat_layout)

        # --- Pants Number ---
        pants_layout = QHBoxLayout()
        pants_label = QLabel("Pants Number:")
        self.pants_input = QSpinBox()
        self.pants_input.setRange(0, 9999)
        pants_layout.addWidget(pants_label)
        pants_layout.addWidget(self.pants_input)
        layout.addLayout(pants_layout)

        # --- Garment Bag Number ---
        bag_layout = QHBoxLayout()
        bag_label = QLabel("Garment Bag Number:")
        self.bag_input = QLineEdit()               # Free text input for bag ID
        bag_layout.addWidget(bag_label)
        bag_layout.addWidget(self.bag_input)
        layout.addLayout(bag_layout)

        # --- Notes field ---
        # Notes left empty for search as well
        self.notes_input = QLineEdit()             

        # --- Save and Cancel buttons ---
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

    def get_uniform_data(self):
        """
        Collect all input values and return them as a dictionary.
        Fields left blank or at zero are returned as None so that
        the caller can distinguish between 'unspecified' and 'actual value'.
        """
        shako  = self.shako_input.value()
        hanger = self.hanger_input.value()
        coat   = self.coat_input.value()
        pants  = self.pants_input.value()

        return {
            'shako_num': None if shako == 0 else shako,
            'hanger_num': None if hanger == 0 else hanger,
            'garment_bag': None if not self.bag_input.text().strip() else self.bag_input.text().strip(),
            'coat_num': None if coat == 0 else coat,
            'pants_num': None if pants == 0 else pants,
            'status': 'Available',  # Default status for new uniforms
            'notes': None if not self.notes_input.text().strip() else self.notes_input.text().strip()
        }