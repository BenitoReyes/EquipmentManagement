from PyQt6.QtWidgets import QVBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QLabel
from add_student_dialog import AddStudentDialog  # Import popup dialog
import db  # Database functions

def load_stylesheet():
    with open("src/styles.qss", "r") as f:
        return f.read()


class EquipmentManagementUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Equipment Management")
        self.setGeometry(200, 200, 900, 700)
        self.setStyleSheet(load_stylesheet())

        layout = QVBoxLayout()

        self.title_label = QLabel("Equipment Management System")
        layout.addWidget(self.title_label)

        # Add Student Button
        self.add_button = QPushButton("Add Student")
        self.add_button.clicked.connect(self.open_add_student_popup)
        layout.addWidget(self.add_button)

        # Student Records Table
        self.student_table = QTableWidget()
        self.student_table.setColumnCount(15)  # Number of fields
        self.student_table.setHorizontalHeaderLabels([
            "First Name", "Last Name", "Student ID", "Section", "Phone", "Email",
            "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #", "Spats Size",
            "Gloves Size", "Guardian Name", "Guardian Phone"
        ])
        layout.addWidget(self.student_table)

        self.setLayout(layout)
        self.refresh_table()

    def open_add_student_popup(self):
        """Opens the add student dialog."""
        dialog = AddStudentDialog()
        if dialog.exec():
            self.refresh_table()

    def refresh_table(self):
        """Fetches and displays student data."""
        students = db.get_students()
        self.student_table.setRowCount(len(students))

        for row_idx, student in enumerate(students):
            for col_idx, value in enumerate(student):
                self.student_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))