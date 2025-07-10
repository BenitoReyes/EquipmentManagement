from PyQt6.QtWidgets import QVBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox,QInputDialog, QToolButton, QMenu, QHBoxLayout, QDialog, QListWidget
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
        student_menu.addAction("Find Student", self.find_student_popup)

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

        # Instrument Operations Menu
        instrument_menu = QMenu()
        instrument_menu.addAction("Assign Instrument", self.assign_instrument_popup)
        instrument_menu.addAction("Return Instrument", self.return_instrument_popup)
        instrument_menu.addAction("View Outstanding Instruments", self.show_outstanding_instruments)

        instrument_ops = QToolButton()
        instrument_ops.setText("Instrument Operations")
        instrument_ops.setMenu(instrument_menu)
        instrument_ops.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        button_layout.addWidget(instrument_ops)
        
        # Add Delete All Students button
        delete_all_button = QPushButton("Delete ALL Students")
        delete_all_button.setObjectName("deleteAllButton")
        delete_all_button.clicked.connect(self.delete_all_students)
        button_layout.addWidget(delete_all_button)

        button_layout.addStretch(1)
        layout.addLayout(button_layout)       
        # --- End Centered Button Layout ---

        # Student Records Table
        self.student_table = QTableWidget()
        self.student_table.setColumnCount(18)  # Adjust for new fields
        self.student_table.setHorizontalHeaderLabels([
            "Student ID", "Last Name", "First Name", "Section", "Phone", "Email",
            "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #",
            "Spats Size", "Gloves Size", "Guardian Name", "Guardian Phone",
            "Instrument Name", "Instrument Serial", "Instrument Case"
        ])
        layout.addWidget(self.student_table)

        self.setLayout(layout)
        self.student_table.clearContents()
        self.refresh_table()
        self.student_table.sortItems(1)  # 1 is the column index for Last Name


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
            QMessageBox.information(self, "Message", "Student ID left empty, searching by last name.")
            last_name, ok_last = QInputDialog.getText(self, "Update Student", "Enter Last Name:")
            if not ok_last or not last_name.strip():
                return
            students = db.get_students_by_last_name(last_name.strip())
            if not students:
                QMessageBox.information(self, "Not Found", "No students found with that last name.")
                return
            # Show selection dialog as above
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Student")
            layout = QVBoxLayout()
            label = QLabel("Select a student to edit:")
            layout.addWidget(label)
            list_widget = QListWidget()
            for student in students:
                list_widget.addItem(f"{student[2]}, {student[1]} (ID: {student[0]})")
            layout.addWidget(list_widget)
            button = QPushButton("Edit")
            layout.addWidget(button)
            dialog.setLayout(layout)
            def handle_edit():
                idx = list_widget.currentRow()
                if idx >= 0:
                    edit_dialog = EditStudentDialog(students[idx])
                    edit_dialog.exec()
                    self.refresh_table()
                    dialog.accept()
            button.clicked.connect(handle_edit)
            dialog.exec()
            return
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
        students = db.get_students_with_uniforms_and_instruments()
        for row_idx, student in enumerate(students):
            self.student_table.insertRow(row_idx)
            for col_idx, value in enumerate(student):
                display_value = "" if value is None else str(value)
                self.student_table.setItem(row_idx, col_idx, QTableWidgetItem(display_value))
        self.student_table.sortItems(1)  # 1 is the column index for Last Name

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

    def assign_instrument_popup(self):
        student_id, ok = QInputDialog.getText(self, "Assign Instrument", "Enter Student ID:")
        if not ok or not student_id.strip():
            return
        instrument_name, ok1 = QInputDialog.getText(self, "Assign Instrument", "Instrument Name:")
        if not ok1 or not instrument_name.strip():
            return
        instrument_serial, ok2 = QInputDialog.getText(self, "Assign Instrument", "Instrument Serial:")
        if not ok2 or not instrument_serial.strip():
            return
        instrument_case, ok3 = QInputDialog.getText(self, "Assign Instrument", "Instrument Case:")
        if not ok3 or not instrument_case.strip():
            return

        db.assign_instrument(student_id.strip(), instrument_name.strip(), instrument_serial.strip(), instrument_case.strip())
        QMessageBox.information(self, "Success", "Instrument assigned!")
        self.refresh_table()

    def return_instrument_popup(self):
        student_id, ok = QInputDialog.getText(self, "Return Instrument", "Enter Student ID:")
        if ok and student_id.strip():
            db.return_instrument(student_id.strip())
            QMessageBox.information(self, "Success", "Instrument marked as returned.")
            self.refresh_table()

    def show_outstanding_instruments(self):
        outstanding = db.get_students_with_outstanding_instruments()
        if not outstanding:
            QMessageBox.information(self, "Info", "All instruments are accounted for.")
        else:
            message = "\n".join([
                f"{row[0]} {row[1]}: {row[2]} (Serial: {row[3]}, Case: {row[4]})"
                for row in outstanding
            ])
            QMessageBox.information(self, "Outstanding Instruments", message)

    def find_student_popup(self):
        """Find students by last name and allow view or edit."""
        last_name, ok = QInputDialog.getText(self, "Find Student", "Enter Last Name:")
        if not ok or not last_name.strip():
            return

        students = db.get_students_by_last_name(last_name.strip())
        if not students:
            QMessageBox.information(self, "Not Found", "No students found with that last name.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Select Student")
        layout = QVBoxLayout()
        label = QLabel("Select a student:")
        layout.addWidget(label)

        list_widget = QListWidget()
        for student in students:
            # Show: Last Name, First Name, Student ID
            list_widget.addItem(f"{student[2]}, {student[1]} (ID: {student[0]})")
        layout.addWidget(list_widget)

        button_layout = QHBoxLayout()
        view_button = QPushButton("View")
        edit_button = QPushButton("Edit")
        button_layout.addWidget(view_button)
        button_layout.addWidget(edit_button)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        def handle_view():
            idx = list_widget.currentRow()
            if idx >= 0:
                self.show_student_info(students[idx])
                dialog.accept()

        def handle_edit():
            idx = list_widget.currentRow()
            if idx >= 0:
                edit_dialog = EditStudentDialog(students[idx])
                edit_dialog.exec()
                self.refresh_table()
                dialog.accept()

        view_button.clicked.connect(handle_view)
        edit_button.clicked.connect(handle_edit)

        dialog.exec()

    def show_student_info(self, student):
        """Display student info in a message box."""
        headers = [
            "Student ID", "First Name", "Last Name", "Section", "Phone", "Email",
            "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #",
            "Spats Size", "Gloves Size", "Guardian Name", "Guardian Phone",
            "Instrument Name", "Instrument Serial", "Instrument Case"
        ]
        info = "\n".join(f"{header}: {str(value) if value is not None else ''}" for header, value in zip(headers, student))
        QMessageBox.information(self, "Student Info", info)

    def delete_all_students(self):
        # Combined first and second confirmation
        reply = QMessageBox.question(
            self,
            "Confirm Delete All",
            "Are you absolutely sure you want to delete ALL students? This will permanently remove ALL student records, uniforms, and instruments. This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Second confirmation: require typing "DELETE ALL"
        text, ok = QInputDialog.getText(
            self,
            "Final Confirmation",
            'Type "DELETE ALL" (all caps, no quotes) to confirm:'
        )
        if not ok or text.strip() != "DELETE ALL":
            QMessageBox.information(self, "Cancelled", "Operation cancelled.")
            return

        # Perform deletion
        db.delete_all_students()
        QMessageBox.information(self, "Deleted", "All students have been deleted.")
        self.refresh_table()
