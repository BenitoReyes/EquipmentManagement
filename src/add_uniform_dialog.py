# Import necessary PyQt6 widgets and layout classes
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt

class AddUniformDialog(QDialog):
    def __init__(self, parent=None, find_mode=False):
        super().__init__(parent)
        self.find_mode = find_mode
        self.setWindowTitle("Find Uniform" if find_mode else "Add New Uniform")

        if not self.find_mode:
            self.setup_ui()
        else:
            self.setup_ui_search()

    def setup_ui(self):
        layout = QVBoxLayout()

        # --- Shako Number ---
        shako_layout = QHBoxLayout()
        shako_label = QLabel("Shako Number:")
        self.shako_input = QSpinBox()
        self.shako_input.setRange(0, 9999)
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

        # --- Garment Bag ---
        bag_layout = QHBoxLayout()
        bag_label = QLabel("Garment Bag Number:")
        self.bag_input = QLineEdit()
        bag_layout.addWidget(bag_label)
        bag_layout.addWidget(self.bag_input)
        layout.addLayout(bag_layout)

        # --- Notes ---
        notes_layout = QHBoxLayout()
        notes_label = QLabel("Notes:")
        self.notes_input = QLineEdit()
        notes_layout.addWidget(notes_label)
        notes_layout.addWidget(self.notes_input)
        layout.addLayout(notes_layout)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Find" if self.find_mode else "Save")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def setup_ui_search(self):
        layout = QVBoxLayout()

        # --- Shako Number ---
        shako_layout = QHBoxLayout()
        shako_label = QLabel("Shako Number:")
        self.shako_input = QSpinBox()
        self.shako_input.setRange(0, 9999)
        shako_layout.addWidget(shako_label)
        shako_layout.addWidget(self.shako_input)
        layout.addLayout(shako_layout)

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

        # --- Garment Bag ---
        bag_layout = QHBoxLayout()
        bag_label = QLabel("Garment Bag Number:")
        self.bag_input = QLineEdit()
        bag_layout.addWidget(bag_label)
        bag_layout.addWidget(self.bag_input)
        layout.addLayout(bag_layout)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Find")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_uniform_data(self):
        """Returns all uniform-related fields, safely handling add vs. find mode."""
        shako = self.shako_input.value()
        coat = self.coat_input.value()
        pants = self.pants_input.value()
        bag = self.bag_input.text().strip()

        if self.find_mode:
            return {
                'shako_num': None if shako == 0 else shako,
                'coat_num': None if coat == 0 else coat,
                'pants_num': None if pants == 0 else pants,
                'garment_bag': None if not bag else bag
            }

        # Only access hanger_input and notes_input in add mode
        hanger = self.hanger_input.value()
        notes = self.notes_input.text().strip()

        return {
            'shako_num': None if shako == 0 else shako,
            'hanger_num': None if hanger == 0 else hanger,
            'garment_bag': None if not bag else bag,
            'coat_num': None if coat == 0 else coat,
            'pants_num': None if pants == 0 else pants,
            'status': 'Available',
            'notes': None if not notes else notes
        }
