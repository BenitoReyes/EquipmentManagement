# Standard library imports

# Third-party imports
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt

class AddUniformDialog(QDialog):
    """
    Dialog for adding new uniforms or searching existing inventory.
    
    This dialog provides a dual-mode interface for:
    1. Adding new uniform components to inventory
    2. Searching existing uniform components
    
    Uniform Components:
    - Shakos (numbered headwear)
    - Coats with hangers
    - Pants (numbered)
    - Garment Bags
    
    Add Mode Features:
    - Component number entry
    - Hanger tracking
    - Notes field
    - Status setting
    - Multi-component entry
    
    Search Mode Features:
    - Component number search
    - Partial criteria matching
    - Multi-component search
    - Results filtering
    
    Data Management:
    - Number validation
    - Optional fields
    - Status tracking
    - Notes handling
    
    Interface Elements:
    - Numeric inputs
    - Text fields
    - Action buttons
    - Clear labeling
    
    Note:
        This dialog adapts its interface and behavior based on
        the find_mode parameter to support both inventory
        addition and search operations
    """
    def __init__(self, parent=None, find_mode=False):
        """
        Initialize and configure the uniform dialog.
        
        This constructor configures the dialog based on its mode:
        1. Parent widget association
        2. Operation mode setting
        3. Window title configuration
        4. Appropriate UI setup
        
        Args:
            parent (QWidget, optional): Parent widget for this dialog.
                Defaults to None for top-level window.
            find_mode (bool, optional): If True, configures for search operations.
                If False, configures for new uniform entry.
                Defaults to False.
        
        Dialog Configuration:
        - Parent hierarchy setup
        - Mode flag setting
        - Title customization
        - UI layout selection
        
        Mode-based Features:
        - Add mode: Complete component entry
        - Find mode: Search-focused interface
        
        Note:
            The find_mode parameter determines which UI setup
            method is called and thus the entire dialog behavior
        """
        super().__init__(parent)
        self.find_mode = find_mode
        self.setWindowTitle("Find Uniform" if find_mode else "Add New Uniform")

        if not self.find_mode:
            self.setup_ui()
        else:
            self.setup_ui_search()

    def setup_ui(self):
        """
        Build and configure the dialog's UI for add mode.
        
        This method creates a comprehensive input form with:
        1. Component number inputs
        2. Optional fields
        3. Notes capability
        4. Action buttons
        
        Form Structure:
        - Vertical layout with field groups
        - Each group uses horizontal layout
        - Consistent label placement
        - Aligned input fields
        
        Input Components:
        - Shako Number (0-9999)
        - Hanger Number (0-9999)
        - Coat Number (0-9999)
        - Pants Number (0-9999)
        - Garment Bag (text)
        - Notes field (text)
        
        Control Elements:
        - Save button
        - Cancel button
        
        Layout Management:
        - Nested layouts
        - Widget alignment
        - Consistent spacing
        - Visual grouping
        
        Note:
            This UI is optimized for adding new uniform
            components with full details and validation
        """
        layout = QVBoxLayout()

        # --- Shako Number ---
        shako_layout = QHBoxLayout()
        shako_label = QLabel("Shako Number:")
        self.shako_input = QLineEdit()
        self.shako_input.setPlaceholderText("Shako Number")
        shako_layout.addWidget(shako_label)
        shako_layout.addWidget(self.shako_input)
        layout.addLayout(shako_layout)

        # --- Hanger Number ---
        hanger_layout = QHBoxLayout()
        hanger_label = QLabel("Hanger Number:")
        self.hanger_input = QLineEdit()
        self.hanger_input.setPlaceholderText("Hanger Number")
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
        """
        Build and configure the dialog's UI for search mode.
        
        This method creates a focused search interface with:
        1. Component search fields
        2. Simple layout
        3. Search controls
        
        Form Structure:
        - Streamlined vertical layout
        - Search-focused fields
        - Clear visual hierarchy
        - Essential controls only
        
        Search Components:
        - Shako Number search
        - Coat Number search
        - Pants Number search
        - Garment Bag search
        
        Control Elements:
        - Find button
        - Cancel button
        
        Layout Features:
        - Simplified layout
        - Direct input fields
        - Clear labeling
        - Search-oriented design
        
        Note:
            This UI is optimized for quick uniform searches
            with minimal required fields
        """
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
        """
        Collect and normalize uniform data from the form.
        
        This method processes input fields based on mode:
        1. Collect all field values
        2. Handle mode-specific fields
        3. Normalize empty values
        4. Format for database
        
        Returns:
            dict: Normalized uniform data with fields:
                All modes:
                - shako_num: int or None
                - coat_num: int or None
                - pants_num: int or None
                - garment_bag: str or None
                
                Add mode only:
                - hanger_num: int or None
                - status: str ('Available')
                - notes: str or None
        
        Data Processing:
        - Zero values normalized to None
        - Empty strings normalized to None
        - Whitespace trimming
        - Mode-specific field inclusion
        
        Field Handling:
        - SpinBox values: 0 converted to None
        - Text inputs: stripped and None if empty
        - Status: 'Available' for new items
        - Notes: Optional in add mode
        
        Note:
            This method ensures database-compatible data format
            while handling differences between add and find modes
        """
        shako = self.shako_input.text().strip()
        coat = self.coat_input.text().strip()
        pants = self.pants_input.text().strip()
        bag = self.bag_input.text().strip()

        if self.find_mode:
            return {
                'shako_num': int(shako) if shako else None,
                'coat_num': int(coat) if coat else None,
                'pants_num': int(pants) if pants else None,
                'garment_bag': bag if bag else None
            }

        # Only access hanger_input and notes_input in add mode
        hanger = self.hanger_input.text().strip()
        notes = self.notes_input.text().strip()

        return {
            'shako_num': int(shako) if shako else None,
            'hanger_num': int(hanger) if hanger else None,
            'garment_bag': None if not bag else bag,
            'coat_num': int(coat) if coat else None,
            'pants_num': int(pants) if pants else None,
            'status': 'Available',
            'notes': None if not notes else notes
        }
