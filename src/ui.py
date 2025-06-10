from PyQt6.QtWidgets import QVBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox,QInputDialog
from add_student_dialog import AddStudentDialog  # Import popup dialog
import db  # Database functions
from edit_student_dialog import EditStudentDialog

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
        self.update_button = QPushButton("Update Student")
        self.update_button.clicked.connect(self.update_student)
        layout.addWidget(self.update_button)
        self.delete_button = QPushButton("Delete Student")
        self.delete_button.clicked.connect(self.delete_student)
        layout.addWidget(self.delete_button)

        # Student Records Table
        self.student_table = QTableWidget()
        self.student_table.setColumnCount(15)  # Number of fields
        self.student_table.setHorizontalHeaderLabels([
            "Student ID", "First Name", "Last Name","Section", "Phone", "Email",
            "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #", "Spats Size",
            "Gloves Size", "Guardian Name", "Guardian Phone"
        ])
        layout.addWidget(self.student_table)

        self.setLayout(layout)
        self.student_table.clearContents()
        self.refresh_table()


    def open_add_student_popup(self):
        """Opens the add student dialog."""
        dialog = AddStudentDialog()
        if dialog.exec():
            self.student_table.clearContents()
            self.refresh_table()


    def update_student(self):
        """Step 1: Ask user for Student ID before updating."""
        student_id, ok = QInputDialog.getText(self, "Update Student", "Enter Student ID:")
        if not ok or not student_id.strip():
            QMessageBox.warning(self, "Error", "Student ID is required!")
            return

        # Step 2: Fetch student details
        student_data = db.get_student_by_id(student_id.strip())
        if not student_data:
            QMessageBox.warning(self, "Error", "No student found with that ID.")
            return

        # Step 3: Open edit popup with student data
        dialog = EditStudentDialog(student_data)
        if dialog.exec():  # If user confirms update
            self.refresh_table()



    def delete_student(self):
        """Step 1: Ask user for Student ID before deleting."""
        student_id, ok = QInputDialog.getText(self, "Delete Student", "Enter Student ID:")
        if not ok or not student_id.strip():
            QMessageBox.warning(self, "Error", "Student ID is required!")
            return

        # Step 2: Check if the student exists before deleting
        student_data = db.get_student_by_id(student_id.strip())
        if not student_data:
            QMessageBox.warning(self, "Error", "No student found with that ID.")
            return

        # Step 3: Confirm deletion
        confirm = QMessageBox.question(self, "Confirm Delete",
                               f"Are you sure you want to delete {student_data[0], student_data[1] +" "+ student_data[2]}?",
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm != QMessageBox.StandardButton.Yes:
            return  # User canceled deletion

        db.delete_student(student_id)
        QMessageBox.information(self, "Success", "Student deleted!")

        self.refresh_table()




    def refresh_table(self):
            """Loads student data into the table and removes stale records."""
            self.student_table.setRowCount(0)  # Clear the table

            students = db.get_students()
            self.student_table.setRowCount(len(students))

            for row_idx, student in enumerate(students):
                for col_idx, value in enumerate(student):
                    self.student_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
