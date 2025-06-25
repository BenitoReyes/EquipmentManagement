from PyQt6.QtWidgets import QVBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox,QInputDialog, QToolButton, QMenu, QHBoxLayout
from PyQt6.QtGui import QAction


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

        # --- Centered Button Layout ---
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        # Student Operations Menu
        student_menu = QMenu()
        student_menu.addAction("Add Student", self.open_add_student_popup)
        student_menu.addAction("Update Student", self.update_student)
        student_menu.addAction("Delete Student", self.delete_student)

        student_ops = QToolButton()
        student_ops.setText("Student Operations")
        student_ops.setMenu(student_menu)
        student_ops.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        button_layout.addWidget(student_ops)

        # Uniform Operations Menu
        uniform_menu = QMenu()
        uniform_menu.addAction("Assign Uniform", self.assign_uniform_popup)
        uniform_menu.addAction("Return Uniform", self.return_uniform_popup)
        uniform_menu.addAction("View Outstanding", self.show_outstanding_uniforms)

        uniform_ops = QToolButton()
        uniform_ops.setText("Uniform Operations")
        uniform_ops.setMenu(uniform_menu)
        uniform_ops.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        button_layout.addWidget(uniform_ops)

        button_layout.addStretch(1)
        layout.addLayout(button_layout)
        # --- End Centered Button Layout ---

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
        student_id, ok = QInputDialog.getText(self, "Update Student", "Enter Student ID: \n(Or leave empty to search by name):")
        if not ok or not student_id.strip():
            QMessageBox.information(self,"Message","Student ID left empty moving to search by name")
            # Step 2: Ask for First and Last Name if ID is empty
            first_name, ok_first = QInputDialog.getText(self, "Update Student", "Enter First Name")
            last_name, ok_last = QInputDialog.getText(self, "Update Student", "Enter Last Name ") 
            if not (ok_first and ok_last) or not (first_name.strip() and last_name.strip()):
                QMessageBox.warning(self, "Error", "First and Last Name are required!")
                return
            student_data = db.get_student_by_name(first_name.strip(), last_name.strip())
            if not student_data:
                QMessageBox.warning(self, "Error", "No student found with that name.")
                return
        else:
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
        """Refresh the student table with up-to-date uniform assignments."""
        self.student_table.setRowCount(0)
        students = db.get_students_with_uniforms()
        for row_idx, student in enumerate(students):
            self.student_table.insertRow(row_idx)
            for col_idx, value in enumerate(student):
                display_value = "" if value is None else str(value)
                self.student_table.setItem(row_idx, col_idx, QTableWidgetItem(display_value))

    def assign_uniform_popup(self):
        student_id, ok = QInputDialog.getText(self, "Assign Uniform", "Enter Student ID:")
        if not ok or not student_id.strip():
            return

        # Get all uniform fields
        shako_num, ok1 = QInputDialog.getInt(self, "Assign Uniform", "Enter Shako Number:")
        if not ok1:
            return
        hanger_num, ok2 = QInputDialog.getInt(self, "Assign Uniform", "Enter Hanger Number:")
        if not ok2:
            return
        garment_bag, ok3 = QInputDialog.getText(self, "Assign Uniform", "Enter Garment Bag (Y/N):")
        if not ok3 or not garment_bag.strip():
            return
        coat_num, ok4 = QInputDialog.getInt(self, "Assign Uniform", "Enter Coat Number:")
        if not ok4:
            return
        pants_num, ok5 = QInputDialog.getInt(self, "Assign Uniform", "Enter Pants Number:")
        if not ok5:
            return

        # Assign uniform with all fields
        db.assign_uniform(student_id.strip(), shako_num, hanger_num, garment_bag.strip(), coat_num, pants_num)
        QMessageBox.information(self, "Success", "Uniform assigned!")
        self.refresh_table()

    def return_uniform_popup(self):
        student_id, ok = QInputDialog.getText(self, "Return Uniform", "Enter Student ID:")
        if ok and student_id.strip():
            db.return_uniform(student_id.strip())
            QMessageBox.information(self, "Success", "Uniform marked as returned.")
            self.refresh_table()

    def show_outstanding_uniforms(self):
        outstanding = db.get_students_with_outstanding_uniforms()
        if not outstanding:
            QMessageBox.information(self, "Info", "All uniforms are accounted for.")
        else:
            # Unpack all columns: first, last, shako, hanger, garment, coat, pants
            message = "\n".join([
                f"{row[0]} {row[1]}: Shako: {row[2]}, Hanger: {row[3]}, Garment: {row[4]}, Coat: {row[5]}, Pants: {row[6]}"
                for row in outstanding
            ])
            QMessageBox.information(self, "Outstanding Uniforms", message)
