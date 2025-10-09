"""
This module defines the EquipmentManagementUI class, which provides
a Qt-based graphical interface for managing students, uniforms, and instruments.
It features menus for CRUD operations, CSV import/export, code generation,
printing support, backup/restore functionality, and table views for
students, uniforms, and instruments.
"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QMessageBox, QInputDialog, QToolButton, QMenu,
    QHBoxLayout, QDialog, QListWidget, QFileDialog, QTextEdit,
    QComboBox, QGroupBox, QApplication, QLineEdit
)
from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtGui import QPixmap, QImage, QPainter, QIcon, QFontMetrics, QBrush, QColor
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
import qrcode
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import io
import csv
from add_student_dialog import AddStudentDialog
from edit_student_dialog import EditStudentDialog
from add_uniform_dialog import AddUniformDialog
from add_instrument_dialog import AddInstrumentDialog
import db
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
def load_stylesheet():
    """Load styles.qss from project root if present, otherwise return empty string."""
    try:
        p = resource_path('styles.qss')
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as fh:
                return fh.read()
    except Exception:
        pass
    return ""
class EquipmentManagementUI(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Equipment Management")
        self.setGeometry(200, 200, 900, 700)
        self.setStyleSheet(load_stylesheet())

        # Valid sections including Flags
        self.sections = [
            "Trumpet", "Trombone", "Euphonium", "French Horn", "Tuba",
            "Flute", "Clarinet", "Saxophone", "Bassoon", "Oboe",
            "Percussion", "Flags"
        ]

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Equipment Management System"))

        # --- Button bar ---
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addStretch(1)

        # Student menu
        student_menu = QMenu()
        student_menu.addAction("Add Student", self.open_add_student_popup)
        student_menu.addAction("Update Student", self.update_student)
        student_menu.addAction("Delete Student", self.delete_student)
        student_menu.addAction("Find Student", self.find_student_popup)
        student_menu.addAction("Student to Bar/QR code", self.student_to_code_popup)
        student_menu.addAction("Import Students from CSV", self.import_students_from_csv)
        student_menu.addAction("View Students Table", self.show_students_table)
        student_ops = QToolButton()
        student_ops.setText("Student Operations")
        student_ops.setMenu(student_menu)
        student_ops.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_layout.addWidget(student_ops)

        # Equipment menu
        equipment_menu = QMenu()
        equipment_menu.addAction("Add New Uniform", self.add_uniform_popup)
        equipment_menu.addAction("Find Uniform", self.find_uniform_popup)
        equipment_menu.addAction("Assign Uniform", self.assign_uniform_popup)
        equipment_menu.addAction("Return Uniform", self.return_uniform_popup)
        equipment_menu.addAction("View Outstanding Uniforms", self.show_outstanding_uniforms)
        equipment_menu.addAction("View Uniform Table", self.show_uniform_table_screen)
        equipment_menu.addSeparator()
        # Instrument management
        equipment_menu.addAction("Add New Instrument", self.add_instrument_popup)
        equipment_menu.addAction("Find Instrument", self.find_instrument_popup)
        equipment_menu.addAction("Assign Instrument", self.assign_instrument_popup)
        equipment_menu.addAction("Return Instrument", self.return_instrument_popup)
        equipment_menu.addAction("View Outstanding Instruments", self.show_outstanding_instruments)
        equipment_menu.addAction("View All Instruments", self.view_all_instruments_table)
        equipment_ops = QToolButton()
        equipment_ops.setText("Equipment Operations")
        equipment_ops.setMenu(equipment_menu)
        equipment_ops.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_layout.addWidget(equipment_ops)

        # Admin menu
        admin_menu = QMenu()
        admin_menu.addAction("Delete ALL...", self.delete_all_dialog)
        admin_menu.addSeparator()
        admin_menu.addAction("Create Backup", self.create_backup)
        admin_menu.addAction("Use Backup", self.use_backup)
        admin_ops = QToolButton()
        admin_ops.setText("Administrative Operations")
        admin_ops.setMenu(admin_menu)
        admin_ops.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_layout.addWidget(admin_ops)

        # About button
        info_btn = QPushButton()
        info_btn.setIcon(QIcon.fromTheme("system-help"))
        info_btn.setToolTip("About this app")
        info_btn.setIconSize(QSize(19, 19))
        info_btn.clicked.connect(self.show_about_dialog)
        self.btn_layout.addWidget(info_btn)

        self.btn_layout.addStretch(1)
        self.layout.addLayout(self.btn_layout)

        # Table widget
        self.student_table = QTableWidget()
        self.layout.addWidget(self.student_table)

        self.setLayout(self.layout)
        # Show the main student table by default
        self.refresh_table()

    def delete_all_dialog(self):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Delete ALL Data")
        msg.setText("What would you like to delete?")
        btn_students = msg.addButton("Delete All Students", QMessageBox.ButtonRole.ActionRole)
        btn_uniforms = msg.addButton("Delete All Uniforms", QMessageBox.ButtonRole.ActionRole)
        btn_instruments = msg.addButton("Delete All Instruments", QMessageBox.ButtonRole.ActionRole)
        btn_cancel = msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        msg.exec()
        clicked = msg.clickedButton()
        if clicked == btn_students:
            self.delete_all_students()
        elif clicked == btn_uniforms:
            self.delete_all_uniforms()
        elif clicked == btn_instruments:
            self.delete_all_instruments()
        elif clicked == btn_cancel:
            self.close()

    def show_about_dialog(self):
        QMessageBox.information(
            self, "About This App",
            "Made by: Benito Reyes\nFall '21 Trumpet \nKKPSI DI,, SPR '24 Ace\n"
            "Code: https://github.com/BenitoReyes/EquipmentManagement"
        )

    def sanitize(self, value):
        return "" if value is None or str(value).strip().lower() == "none" else str(value)

    def show_printable_results(self, title, text):
        """Show a printable dialog with text and a Print button."""
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        v = QVBoxLayout()
        te = QTextEdit()
        te.setReadOnly(True)
        te.setPlainText(text)
        v.addWidget(te)
        h = QHBoxLayout()
        print_btn = QPushButton("Print")
        close_btn = QPushButton("Close")
        h.addWidget(print_btn)
        h.addWidget(close_btn)
        v.addLayout(h)
        dlg.setLayout(v)

        def do_print():
            doc = te.document()
            printer = QPrinter()
            pd = QPrintDialog(printer, dlg)
            if pd.exec():
                doc.print(printer)

        print_btn.clicked.connect(do_print)
        close_btn.clicked.connect(dlg.accept)
        dlg.exec()

    # --------------------------------------------------------------------------
    # Table view methods
    # --------------------------------------------------------------------------
    
    def show_students_table(self):
        self.active_table = "students"

        # Clear other widgets from layout
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if item and item.widget() and item.widget() is not self.student_table and item.widget() is not None:
                item.widget().setParent(None)

        # Create student table if needed
        if not hasattr(self, 'student_table') or self.student_table.parent() is None:
            self.student_table = QTableWidget()
            self.layout.addWidget(self.student_table)

        self.student_table.show()
        self.refresh_table()

    def refresh_table(self):
        self.active_table = "students"

        rows, headers = db.get_students_with_uniforms_and_instruments()

        self.student_table.setSortingEnabled(False)  # Disable sorting during population
        self.student_table.clearContents()
        self.student_table.setColumnCount(len(headers))
        self.student_table.setHorizontalHeaderLabels(headers)
        self.student_table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            # Normalize row length
            if len(row) < len(headers):
                row += [None] * (len(headers) - len(row))
            elif len(row) > len(headers):
                print(f"Warning: Row {r} has extra fields. Trimming.")
                row = row[:len(headers)]

            for c, val in enumerate(row):
                item = QTableWidgetItem("" if val is None else str(val))
                self.student_table.setItem(r, c, item)

        header = self.student_table.horizontalHeader()
        stretch_labels = {"First Name", "Last Name", "Email", "Guardian Name", "Notes"}
        for idx, label in enumerate(headers):
            if label in stretch_labels:
                header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Stretch)
            else:
                header.setSectionResizeMode(idx, QHeaderView.ResizeMode.ResizeToContents)

        self.student_table.verticalHeader().setVisible(False)
        self.student_table.setSortingEnabled(True)

        # Sort by last name if present
        if "Last Name" in headers:
            last_name_index = headers.index("Last Name")
            self.student_table.sortItems(last_name_index)

    def refresh_if_active(self, table_name):
        if self.active_table == table_name:
            if table_name == "students":
                self.refresh_table()
            elif table_name == "uniforms":
                self.show_uniform_table_screen()
            elif table_name == "instruments":
                self.view_all_instruments_table()

    def view_all_uniforms_table(self):
        """
        Show all uniform records in the table.
        """
        self.active_table = "uniforms"
        headers = [
            "Record ID", "Student ID", "Shako #", "Hanger #",
            "Garment Bag", "Coat #", "Pants #", "Status", "Notes"
        ]
        self.student_table.setColumnCount(len(headers))
        self.student_table.setHorizontalHeaderLabels(headers)
        self.student_table.setRowCount(0)

        rows = db.get_all_uniforms()
        for r, u in enumerate(rows):
            self.student_table.insertRow(r)
            for c, val in enumerate(u):
                text = "" if val is None else str(val)
                self.student_table.setItem(r, c, QTableWidgetItem(text))

        self.student_table.resizeColumnsToContents()

    def open_uniform_inventory(self):
        self.active_table = "uniforms"
        dlg = QDialog(self)
        dlg.setWindowTitle("Uniform Inventory")
        vbox = QVBoxLayout()

        # Shakos Section
        shako_group = QGroupBox("Shakos")
        shako_group.setCheckable(True)
        shako_group.setChecked(True)
        shako_layout = QVBoxLayout()
        shako_table = QTableWidget()
        shako_headers = ["ID", "Shako #", "Status", "Student ID", "Notes"]
        shako_table.setColumnCount(len(shako_headers))
        shako_table.setHorizontalHeaderLabels(shako_headers)
        shakos = db.get_all_shakos()
        shako_table.setRowCount(len(shakos))
        for r, row in enumerate(shakos):
            for c, val in enumerate(row):
                shako_table.setItem(r, c, QTableWidgetItem(str(val) if val is not None else ""))
        shako_table.resizeColumnsToContents()
        shako_layout.addWidget(shako_table)
        shako_group.setLayout(shako_layout)
        vbox.addWidget(shako_group)

        # Coats Section
        coat_group = QGroupBox("Coats")
        coat_group.setCheckable(True)
        coat_group.setChecked(True)
        coat_layout = QVBoxLayout()
        coat_table = QTableWidget()
        coat_headers = ["ID", "Coat #", "Status", "Student ID", "Notes"]
        coat_table.setColumnCount(len(coat_headers))
        coat_table.setHorizontalHeaderLabels(coat_headers)
        coats = db.get_all_coats()
        coat_table.setRowCount(len(coats))
        for r, row in enumerate(coats):
            for c, val in enumerate(row):
                coat_table.setItem(r, c, QTableWidgetItem(str(val) if val is not None else ""))
        coat_table.resizeColumnsToContents()
        coat_layout.addWidget(coat_table)
        coat_group.setLayout(coat_layout)
        vbox.addWidget(coat_group)

        # Pants Section
        pants_group = QGroupBox("Pants")
        pants_group.setCheckable(True)
        pants_group.setChecked(True)
        pants_layout = QVBoxLayout()
        pants_table = QTableWidget()
        pants_headers = ["ID", "Pants #", "Status", "Student ID", "Notes"]
        pants_table.setColumnCount(len(pants_headers))
        pants_table.setHorizontalHeaderLabels(pants_headers)
        pants = db.get_all_pants()
        pants_table.setRowCount(len(pants))
        for r, row in enumerate(pants):
            for c, val in enumerate(row):
                pants_table.setItem(r, c, QTableWidgetItem(str(val) if val is not None else ""))
        pants_table.resizeColumnsToContents()
        pants_layout.addWidget(pants_table)
        pants_group.setLayout(pants_layout)
        vbox.addWidget(pants_group)

        # Garment Bags Section
        bag_group = QGroupBox("Garment Bags")
        bag_group.setCheckable(True)
        bag_group.setChecked(True)
        bag_layout = QVBoxLayout()
        bag_table = QTableWidget()
        bag_headers = ["ID", "Bag #", "Status", "Student ID", "Notes"]
        bag_table.setColumnCount(len(bag_headers))
        bag_table.setHorizontalHeaderLabels(bag_headers)
        bags = db.get_all_garment_bags()
        bag_table.setRowCount(len(bags))
        for r, row in enumerate(bags):
            for c, val in enumerate(row):
                bag_table.setItem(r, c, QTableWidgetItem(str(val) if val is not None else ""))
        bag_table.resizeColumnsToContents()
        bag_layout.addWidget(bag_table)
        bag_group.setLayout(bag_layout)
        vbox.addWidget(bag_group)

        # Dialog controls
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        vbox.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        dlg.setLayout(vbox)
        dlg.exec()

    def show_uniform_table_screen(self):
        self.active_table = "uniforms"
        """Display separate uniform component tables full-screen (keeps button bar)."""
        # Remove any existing widgets under the main layout (but keep the button bar layout)
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            # Keep layouts (like the top button bar) intact
            if item is None:
                continue
            if item.widget():
                item.widget().setParent(None)

        # Shakos
        shako_group = QGroupBox("Shakos")
        shako_group.setCheckable(True)
        shako_group.setChecked(True)
        shako_layout = QVBoxLayout()
        shako_table = QTableWidget()
        shako_headers = ["ID", "Shako #", "Status", "Student ID", "Notes"]
        shako_table.setColumnCount(len(shako_headers))
        shako_table.setHorizontalHeaderLabels(shako_headers)
        shakos = db.get_all_shakos()
        shako_table.setRowCount(len(shakos))
        shako_table.setVerticalHeaderLabels(["" for _ in range(len(shakos))])
        for r, row in enumerate(shakos):
            for c, val in enumerate(row):
                shako_table.setItem(r, c, QTableWidgetItem(str(val) if val is not None else ""))
        shako_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        shako_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        shako_layout.addWidget(shako_table)
        shako_group.toggled.connect(lambda checked, tbl=shako_table: tbl.setVisible(checked))
        shako_group.setLayout(shako_layout)
        self.layout.addWidget(shako_group)

        # Coats
        coat_group = QGroupBox("Coats")
        coat_group.setCheckable(True)
        coat_group.setChecked(True)
        coat_layout = QVBoxLayout()
        coat_table = QTableWidget()
        coat_headers = ["ID", "Coat #", "Hanger #", "Status", "Student ID", "Notes"]
        coat_table.setColumnCount(len(coat_headers))
        coat_table.setHorizontalHeaderLabels(coat_headers)
        coats = db.get_all_coats()
        coat_table.setRowCount(len(coats))
        coat_table.setVerticalHeaderLabels(["" for _ in range(len(coats))])
        for r, row in enumerate(coats):
            for c in range(len(coat_headers)):
                val = row[c] if c < len(row) else ""
                coat_table.setItem(r, c, QTableWidgetItem(str(val) if val is not None else ""))
        coat_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        coat_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        coat_layout.addWidget(coat_table)
        coat_group.toggled.connect(lambda checked, tbl=coat_table: tbl.setVisible(checked))
        coat_group.setLayout(coat_layout)
        self.layout.addWidget(coat_group)

        # Pants
        pants_group = QGroupBox("Pants")
        pants_group.setCheckable(True)
        pants_group.setChecked(True)
        pants_layout = QVBoxLayout()
        pants_table = QTableWidget()
        pants_headers = ["ID", "Pants #", "Status", "Student ID", "Notes"]
        pants_table.setColumnCount(len(pants_headers))
        pants_table.setHorizontalHeaderLabels(pants_headers)
        pants = db.get_all_pants()
        pants_table.setRowCount(len(pants))
        pants_table.setVerticalHeaderLabels(["" for _ in range(len(pants))])
        for r, row in enumerate(pants):
            for c, val in enumerate(row):
                pants_table.setItem(r, c, QTableWidgetItem(str(val) if val is not None else ""))
        pants_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        pants_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        pants_layout.addWidget(pants_table)
        pants_group.toggled.connect(lambda checked, tbl=pants_table: tbl.setVisible(checked))
        pants_group.setLayout(pants_layout)
        self.layout.addWidget(pants_group)

        # Garment Bags
        bag_group = QGroupBox("Garment Bags")
        bag_group.setCheckable(True)
        bag_group.setChecked(True)
        bag_layout = QVBoxLayout()
        bag_table = QTableWidget()
        bag_headers = ["ID", "Bag #", "Status", "Student ID", "Notes"]
        bag_table.setColumnCount(len(bag_headers))
        bag_table.setHorizontalHeaderLabels(bag_headers)
        bags = db.get_all_garment_bags()
        bag_table.setRowCount(len(bags))
        bag_table.setVerticalHeaderLabels(["" for _ in range(len(bags))])
        for r, row in enumerate(bags):
            for c, val in enumerate(row):
                bag_table.setItem(r, c, QTableWidgetItem(str(val) if val is not None else ""))
        bag_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        bag_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        bag_layout.addWidget(bag_table)
        bag_group.toggled.connect(lambda checked, tbl=bag_table: tbl.setVisible(checked))
        bag_group.setLayout(bag_layout)
        self.layout.addWidget(bag_group)

    def view_all_instruments_table(self):
        self.active_table = "instruments"

        # Remove other widgets
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if item and item.widget() and item.widget() is not self.student_table and item.widget() is not None:
                item.widget().setParent(None)

        # Create or reuse the table
        if not hasattr(self, 'student_table') or self.student_table.parent() is None:
            self.student_table = QTableWidget()
            self.layout.addWidget(self.student_table)

        headers = [
            "ID", "Student ID", "Name", "Serial", "Case",
            "Model", "Condition", "Status", "Notes"
        ]
        expected_len = len(headers)

        self.student_table.setSortingEnabled(False)
        self.student_table.clearContents()
        self.student_table.setColumnCount(expected_len)
        self.student_table.setHorizontalHeaderLabels(headers)
        self.student_table.setRowCount(0)

        rows = db.get_all_instruments()
        self.student_table.setRowCount(len(rows))
        for r, inst in enumerate(rows):
            inst = list(inst)
            if len(inst) < expected_len:
                inst += [None] * (expected_len - len(inst))
            elif len(inst) > expected_len:
                print(f"Warning: Instrument row {r} has extra fields. Trimming.")
                inst = inst[:expected_len]

            for c, val in enumerate(inst):
                text = "" if val is None else str(val)
                self.student_table.setItem(r, c, QTableWidgetItem(text))
        self.student_table.setSortingEnabled(True)
        self.student_table.sortItems(7)
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.student_table.verticalHeader().setVisible(False)

    # --------------------------------------------------------------------------
    # Student CRUD methods
    # --------------------------------------------------------------------------

    def find_student_popup(self):
        """Opens a dialog to search for students by ID or section."""
        choice, ok = QInputDialog.getItem(
            self, "Find Student", "Search by:", ["Student ID", "Section"], 0, False
        )
        if not ok:
            return

        if choice == "Student ID":
            sid, okid = QInputDialog.getText(self, "Find Student", "Enter Student ID:")
            if not okid or not sid.strip():
                return
            sid = sid.strip()
            if not sid.isdigit() or len(sid) != 9:
                QMessageBox.warning(self, "Error", "ID must be 9 digits.")
                return

            stu = db.get_student_by_id(sid)
            if not stu:
                QMessageBox.information(self, "Not Found", "No student.")
                return

            dlg = QDialog(self)
            dlg.setWindowTitle("Student Found")
            vbox = QVBoxLayout()

            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["ID", "First Name", "Last Name"])
            table.setRowCount(1)
            table.setItem(0, 0, QTableWidgetItem(str(stu[0])))
            table.setItem(0, 1, QTableWidgetItem(stu[1]))
            table.setItem(0, 2, QTableWidgetItem(stu[2]))
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.setStyleSheet("""
                QTableWidget {
                    background-color: #1e1e1e;
                    color: white;
                }
                QTableWidget::item {
                    padding: 6px;
                }
            """)

            vbox.addWidget(QLabel("Student found:"))
            vbox.addWidget(table)

            hbox = QHBoxLayout()
            view_btn = QPushButton("View")
            edit_btn = QPushButton("Edit")

            view_btn.clicked.connect(lambda _, s=stu, d=dlg: self._view_single_student(s, d))
            edit_btn.clicked.connect(lambda: (
                self._edit_single_student(stu),
                dlg.accept(),
                self.refresh_if_active("students")
            ))

            hbox.addWidget(view_btn)
            hbox.addWidget(edit_btn)
            vbox.addLayout(hbox)

            dlg.setLayout(vbox)
            dlg.exec()

        else:
            section, oksec = QInputDialog.getItem(
                self, "Find Student", "Select Section:", self.sections, 0, False
            )
            if not oksec:
                return

            students = db.get_students_by_section(section)
            if not students:
                QMessageBox.information(self, "Not Found", "No students in that section.")
                return

            dlg = QDialog(self)
            dlg.setWindowTitle("Select Student")
            vbox = QVBoxLayout()

            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["ID", "First Name", "Last Name"])
            table.setRowCount(len(students))
            selected_row = [-1]

            def highlight_row(row_index):
                for r in range(table.rowCount()):
                    for c in range(table.columnCount()):
                        item = table.item(r, c)
                        if item:
                            item.setBackground(QColor("#1e1e1e"))
                for c in range(table.columnCount()):
                    item = table.item(row_index, c)
                    if item:
                        item.setBackground(QColor("#3c3c3c"))
                selected_row[0] = row_index

            for r, s in enumerate(students):
                table.setItem(r, 0, QTableWidgetItem(str(s[0])))
                table.setItem(r, 1, QTableWidgetItem(s[1]))
                table.setItem(r, 2, QTableWidgetItem(s[2]))

            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.cellClicked.connect(lambda r, _: highlight_row(r))

            vbox.addWidget(QLabel(f"Students in section: {section}"))
            vbox.addWidget(table)

            hbox = QHBoxLayout()
            view_all_btn = QPushButton("View All")
            edit_sel_btn = QPushButton("Edit Selected")

            def on_edit_selected():
                r = selected_row[0]
                if r < 0:
                    QMessageBox.information(self, "Select", "Select a student to edit.")
                    return
                self._edit_single_student(students[r])
                dlg.accept()
                self.refresh_if_active("students")

            view_all_btn.clicked.connect(lambda _, s=students, sec=section, d=dlg: self._view_section_students(s, sec, d))
            edit_sel_btn.clicked.connect(on_edit_selected)

            hbox.addWidget(view_all_btn)
            hbox.addWidget(edit_sel_btn)
            vbox.addLayout(hbox)

            dlg.setLayout(vbox)
            dlg.exec()

    def open_add_student_popup(self):
        dialog = AddStudentDialog()
        if dialog.exec():
            self.refresh_if_active(self.active_table)

    def update_student(self):
        """Launches a dialog to update a student by ID or last name."""
        sid, ok = QInputDialog.getText(
            self, "Update Student",
            "Enter Student ID (9 digits) or leave blank to search by last name:"
        )
        if not ok:
            return

        sid = sid.strip()

        # --- Search by Last Name ---
        if not sid:
            last, okn = QInputDialog.getText(self, "Update Student", "Enter Last Name:")
            if not okn or not last.strip():
                return

            matches = db.get_students_by_last_name(last.strip())
            if not matches:
                QMessageBox.information(self, "Not Found", "No matches.")
                return

            dlg = QDialog(self)
            dlg.setWindowTitle("Select Student")
            vbox = QVBoxLayout()

            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["ID", "First Name", "Last Name"])
            table.setRowCount(len(matches))
            selected_row = [-1]

            def highlight_row(row_index):
                for r in range(table.rowCount()):
                    for c in range(table.columnCount()):
                        item = table.item(r, c)
                        if item:
                            item.setBackground(QColor("#1e1e1e"))
                for c in range(table.columnCount()):
                    item = table.item(row_index, c)
                    if item:
                        item.setBackground(QColor("#3c3c3c"))
                selected_row[0] = row_index

            for r, s in enumerate(matches):
                table.setItem(r, 0, QTableWidgetItem(str(s[0])))
                table.setItem(r, 1, QTableWidgetItem(s[1]))
                table.setItem(r, 2, QTableWidgetItem(s[2]))

            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.cellClicked.connect(lambda r, _: highlight_row(r))
            table.cellDoubleClicked.connect(lambda r, _: edit_selected(r))

            def edit_selected(row_index):
                self._edit_single_student(matches[row_index])
                dlg.accept()
                self.refresh_if_active("students")

            vbox.addWidget(QLabel("Select a student to edit:"))
            vbox.addWidget(table)

            btn = QPushButton("Edit Selected")

            def on_edit_selected():
                r = selected_row[0]
                if r < 0:
                    QMessageBox.information(self, "Select", "Select a student to edit.")
                    return
                edit_selected(r)

            btn.clicked.connect(on_edit_selected)
            vbox.addWidget(btn)

            dlg.setLayout(vbox)
            dlg.exec()
            return

        # --- Search by Student ID ---
        if not sid.isdigit() or len(sid) != 9:
            QMessageBox.warning(self, "Error", "ID must be 9 digits.")
            return

        data = db.get_student_by_id(sid)
        if not data:
            QMessageBox.warning(self, "Error", "Not found.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Student Found")
        vbox = QVBoxLayout()

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["ID", "First Name", "Last Name"])
        table.setRowCount(1)
        table.setItem(0, 0, QTableWidgetItem(str(data[0])))
        table.setItem(0, 1, QTableWidgetItem(data[1]))
        table.setItem(0, 2, QTableWidgetItem(data[2]))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: white;
            }
            QTableWidget::item {
                padding: 6px;
            }
        """)

        vbox.addWidget(QLabel("Student found:"))
        vbox.addWidget(table)

        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: (self._edit_single_student(data), dlg.accept(), self.refresh_if_active("students")))
        vbox.addWidget(edit_btn)

        dlg.setLayout(vbox)
        dlg.exec()

    def _handle_batch_edit(self, list_widget, students, dialog):
        idx = list_widget.currentRow()
        if idx < 0:
            return
        ed = EditStudentDialog(students[idx])
        ed.exec()
        self.refresh_if_active(self.active_table)
        dialog.accept()

    def delete_student(self):
        sid, ok = QInputDialog.getText(self, "Delete Student", "Enter Student ID (9 digits):")
        if not ok or not sid.strip():
            return
        sid = sid.strip()
        if not sid.isdigit() or len(sid) != 9:
            QMessageBox.warning(self, "Error", "ID must be 9 digits.")
            return

        data = db.get_student_by_id(sid)
        if not data:
            QMessageBox.warning(self, "Error", "Not found.")
            return

        ans = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete {data[1]} {data[2]} (ID: {sid})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ans == QMessageBox.StandardButton.Yes:
            db.delete_student(sid)
            QMessageBox.information(self, "Deleted", "Student deleted.")
            self.refresh_if_active(self.active_table)

    def delete_all_students(self):
        ans = QMessageBox.question(
            self, "Delete ALL",
            "This will remove ALL students continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ans != QMessageBox.StandardButton.Yes:
            return

        txt, ok = QInputDialog.getText(
            self, "Final Confirmation", 'Type DELETE ALL to confirm:'
        )
        if not ok or txt.strip() != "DELETE ALL":
            QMessageBox.information(self, "Cancelled", "Operation cancelled.")
            return
        db.delete_all_students()
        QMessageBox.information(self, "Deleted", "All data cleared.")
        self.refresh_if_active(self.active_table)

    def import_students_from_csv(self):
        """
        Import students from a CSV file. Overwrite existing students with the same ID.
        Supports two formats:
        1) Backup-style rows prefixed with 'STUDENTS'
        2) Plain CSV with headers
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Students from CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        if not file_path:
            return

        count_added = 0
        count_updated = 0

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            first = csvfile.read(1024)
            csvfile.seek(0)

            # --- Format 1: Backup-style rows prefixed with 'STUDENTS' ---
            if first.lstrip().upper().startswith('STUDENTS') or ',STUDENTS' in first.upper():
                reader = csv.reader(csvfile)
                for row in reader:
                    if not row or row[0].strip().upper() != 'STUDENTS':
                        continue
                    parts = [p if p != '' else None for p in row[1:]]

                    # Expect 12 fields: student_id, first_name, last_name, phone, email,
                    # year_came_up, status, guardian_name, guardian_phone, section,
                    # glove_size, spat_size
                    if len(parts) < 12:
                        continue

                    sid = parts[0]
                    if not sid or not sid.isdigit() or len(sid) != 9:
                        continue

                    inserted = db.add_or_update_student(
                        sid, parts[1], parts[2], parts[6], parts[9],
                        parts[3], parts[4], parts[7], parts[8], parts[5],
                        parts[10], parts[11]
                    )
                    if inserted:
                        count_added += 1
                    else:
                        count_updated += 1

            # --- Format 2: Plain CSV with headers ---
            else:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    sid = row.get('student_id') or row.get('Student ID') or row.get('ID')
                    if not sid or not sid.isdigit() or len(sid) != 9:
                        continue

                    student_data = {
                        'student_id': sid,
                        'first_name': row.get('first_name') or row.get('First Name') or '',
                        'last_name': row.get('last_name') or row.get('Last Name') or '',
                        'status': row.get('status') or row.get('Status') or '',
                        'section': row.get('section') or row.get('Section') or '',
                        'phone': row.get('phone') or row.get('Phone') or '',
                        'email': row.get('email') or row.get('Email') or '',
                        'guardian_name': row.get('guardian_name') or row.get('Guardian Name') or '',
                        'guardian_phone': row.get('guardian_phone') or row.get('Guardian Phone') or '',
                        'year_came_up': row.get('year_came_up') or row.get('Year Came Up') or '',
                        'glove_size': row.get('glove_size') or row.get('Glove Size') or '',
                        'spat_size': row.get('spat_size') or row.get('Spat Size') or '',
                    }

                    inserted = db.add_or_update_student(
                        sid,
                        student_data['first_name'],
                        student_data['last_name'],
                        student_data['status'],
                        student_data['section'],
                        student_data['phone'],
                        student_data['email'],
                        student_data['guardian_name'],
                        student_data['guardian_phone'],
                        student_data['year_came_up'],
                        student_data['glove_size'],
                        student_data['spat_size']
                    )
                    if inserted:
                        count_added += 1
                    else:
                        count_updated += 1

        self.refresh_if_active(self.active_table)
        QMessageBox.information(self, "Import Complete", f"Added: {count_added}\nUpdated: {count_updated}")
    
    def student_to_code_popup(self):
        """
        Prompt for Student ID, choose QR Code or Barcode,
        generate and display with Print, Full Screen, Close.
        """
        sid, ok = QInputDialog.getText(self, "Student to Bar/QR code", "Enter Student ID:")
        if not ok or not sid.strip():
            return
        if not sid.isdigit() or len(sid) != 9:
            QMessageBox.warning(self, "Error", "Student ID must be 9 digits.")
            return
        student = db.get_student_by_id(sid.strip())
        if not student:
            QMessageBox.information(self, "Not Found", "No student found.")
            return

        code_type, ok = QInputDialog.getItem(
            self, "Choose Code Type", "Generate:", ["QR Code", "Barcode"], 0, False
        )
        if not ok:
            return

        info = (
            f"ID:{student[0]} "
            f"Name:{student[2]}, {student[1]} "
            f"Phone:{student[3]} Email:{student[4]} "
            f"Year:{student[5]} Status:{student[6]} "
            f"Guardian:{student[7]} ({student[8]}) "
            f"Section:{student[9]}"
        )

        if code_type == "QR Code":
            img = qrcode.make(info).convert("RGB")
        else:
            cls = barcode.get_barcode_class('code128')
            img = cls(student[0], writer=ImageWriter()).render(writer_options={"write_text": False}).convert("RGB")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        qimg = QImage.fromData(buf.getvalue())
        pix = QPixmap.fromImage(qimg)

        dlg = QDialog(self)
        dlg.setWindowTitle(f"{code_type} for {student[0]}")
        vbox = QVBoxLayout()
        lbl = QLabel()
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scaled = pix.scaled(256, 256, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        lbl.setPixmap(scaled)
        vbox.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        hbox = QHBoxLayout()
        print_btn = QPushButton("Print")
        fs_btn = QPushButton("Full Screen")
        close_btn = QPushButton("Close")
        hbox.addWidget(print_btn)
        hbox.addWidget(fs_btn)
        hbox.addWidget(close_btn)
        vbox.addLayout(hbox)
        dlg.setLayout(vbox)

        def on_print():
            printer = QPrinter()
            pd = QPrintDialog(printer, dlg)
            if pd.exec():
                painter = QPainter(printer)
                rect = painter.viewport()
                size = scaled.size()
                size.scale(rect.size(), Qt.AspectRatioMode.KeepAspectRatio)
                painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
                painter.setWindow(scaled.rect())
                painter.drawPixmap(0, 0, scaled)
                painter.end()

        def on_fullscreen():
            fs = QDialog(self)
            fs.setWindowTitle("Full Screen Code")
            box = QVBoxLayout()
            lbl_fs = QLabel()
            lbl_fs.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_fs.setPixmap(pix.scaled(400, 400,
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            box.addWidget(lbl_fs)
            fs.setLayout(box)
            fs.showMaximized()
            fs.exec()

        print_btn.clicked.connect(on_print)
        fs_btn.clicked.connect(on_fullscreen)
        close_btn.clicked.connect(dlg.accept)
        dlg.exec()

    # --------------------------------------------------------------------------
    # Find / View methods
    # --------------------------------------------------------------------------

    def _view_single_student(self, stu, dialog):
        """
        Display a printable summary of a student's full profile,
        including uniform and instrument assignments if available.
        """
        headers = [
            "Student ID", "First Name", "Last Name", "Status", "Phone", "Email",
            "Guardian Name", "Guardian Phone", "Year Came Up", "Section",
            "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #",
            "Instrument Name", "Instrument Serial", "Instrument Case"
        ]

        vals = list(stu)

        # If student-only row, enrich with uniform/instrument data
        if len(vals) < len(headers):
            sid = vals[0]
            enriched = db.get_students_with_uniforms_and_instruments()
            match = next((r for r in enriched if r[0] == sid), None)
            if match:
                vals = list(match)
            else:
                vals += [None] * (len(headers) - len(vals))

        info = "\n".join(
            f"{headers[i]}: {vals[i] if i < len(vals) and vals[i] is not None else ''}"
            for i in range(len(headers))
        )

        self.show_printable_results("Student Info", info)
        dialog.accept()

    def _edit_single_student(self, stu):
        """Launches the EditStudentDialog for a single student."""
        ed = EditStudentDialog(stu)
        ed.exec()
        self.refresh_if_active("students")

    def _view_section_students(self, students, section, dialog):
        headers = [
            "Student ID", "First Name", "Last Name", "Status", "Phone", "Email",
            "Guardian Name", "Guardian Phone", "Year Came Up", "Section",
            "Glove Size", "Spat Size",
            "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #",
            "Instrument Name", "Instrument Serial", "Instrument Case"
        ]

        info = ""
        joined_rows = db.get_students_with_uniforms_and_instruments()

        for stu in students:
            vals = list(stu)
            sid = vals[0]

            # Try to find full joined row
            matched = [r for r in joined_rows if r[0] == sid]
            if matched:
                vals = list(matched[0])
            else:
                # Convert student-only row to joined layout
                # students table: student_id, first_name, last_name, phone, email, year_came_up, status, guardian_name, guardian_phone, section, glove_size, spat_size
                # joined layout: student_id, first_name, last_name, status, phone, email, guardian_name, guardian_phone, year_came_up, section
                vals = [
                    stu[0],  # student_id
                    stu[1],  # first_name
                    stu[2],  # last_name
                    stu[6] if len(stu) > 6 else None,  # status
                    stu[3] if len(stu) > 3 else None,  # phone
                    stu[4] if len(stu) > 4 else None,  # email
                    stu[7] if len(stu) > 7 else None,  # guardian_name
                    stu[8] if len(stu) > 8 else None,  # guardian_phone
                    stu[5] if len(stu) > 5 else None,  # year_came_up
                    stu[9] if len(stu) > 9 else None,  # section
                    stu[10] if len(stu) > 10 else None,  # glove_size
                    stu[11] if len(stu) > 11 else None,  # spat_size
                ]
                vals += [None] * (len(headers) - len(vals))

            block = "\n".join(
                f"{headers[i]}: {vals[i] if i < len(vals) and vals[i] is not None else ''}"
                for i in range(len(headers))
            )
            info += block + "\n" + "-" * 40 + "\n"

        self.show_printable_results(f"Section: {section}", info)
        dialog.accept()

    def _edit_section_student(self, list_widget, students, dialog):
        idx = list_widget.currentRow()
        if idx < 0:
            return
        ed = EditStudentDialog(students[idx])
        ed.exec()
        self.refresh_if_active(self.active_table)
        dialog.accept()

    # --------------------------------------------------------------------------
    # Uniform methods
    # --------------------------------------------------------------------------
    
    def find_uniform_popup(self):
        """
        Open the AddUniformDialog in find mode and return matching component values.
        Displays results in a table with clear row highlighting and edit functionality.
        """
        dialog = AddUniformDialog(self, find_mode=True)
        if not dialog.exec():
            return
        q = dialog.get_uniform_data()

        found_rows = []
        if q.get('shako_num') is not None:
            s = db.find_shako_by_number(q['shako_num'])
            if s:
                found_rows.append({'type': 'Shako', 'data': s})
        if q.get('coat_num') is not None:
            c = db.find_coat_by_number(q['coat_num'])
            if c:
                found_rows.append({'type': 'Coat', 'data': c})
        if q.get('pants_num') is not None:
            p = db.find_pants_by_number(q['pants_num'])
            if p:
                found_rows.append({'type': 'Pants', 'data': p})
        if q.get('garment_bag') is not None:
            b = db.find_bag_by_number(q['garment_bag'])
            if b:
                found_rows.append({'type': 'Bag', 'data': b})

        dlg = QDialog(self)
        dlg.setWindowTitle("Find Results")
        v = QVBoxLayout()

        if not found_rows:
            v.addWidget(QLabel("No matching components found."))
        else:
            table = QTableWidget()
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(["Type", "ID/Num", "Hanger", "Status", "Student", "Notes"])
            table.setRowCount(len(found_rows))

            selected_row = [-1]

            def highlight_row(row_index):
                for r in range(table.rowCount()):
                    for c in range(table.columnCount()):
                        item = table.item(r, c)
                        if item:
                            item.setBackground(QColor("#1e1e1e"))

                for c in range(table.columnCount()):
                    item = table.item(row_index, c)
                    if item:
                        item.setBackground(QColor("#3c3c3c"))

                selected_row[0] = row_index

            for r, rowinfo in enumerate(found_rows):
                typ = rowinfo['type']
                data = rowinfo['data']
                table.setItem(r, 0, QTableWidgetItem(typ))
                if typ == 'Shako':
                    table.setItem(r, 1, QTableWidgetItem(str(data[1])))
                    table.setItem(r, 2, QTableWidgetItem(""))
                    table.setItem(r, 3, QTableWidgetItem(str(data[2] or '')))
                    table.setItem(r, 4, QTableWidgetItem(str(data[3] or '')))
                    table.setItem(r, 5, QTableWidgetItem(str(data[4] or '')))
                elif typ == 'Coat':
                    table.setItem(r, 1, QTableWidgetItem(str(data[1])))
                    table.setItem(r, 2, QTableWidgetItem(str(data[2] or '')))
                    table.setItem(r, 3, QTableWidgetItem(str(data[3] or '')))
                    table.setItem(r, 4, QTableWidgetItem(str(data[4] or '')))
                    table.setItem(r, 5, QTableWidgetItem(str(data[5] or '')))
                elif typ == 'Pants':
                    table.setItem(r, 1, QTableWidgetItem(str(data[1])))
                    table.setItem(r, 2, QTableWidgetItem(""))
                    table.setItem(r, 3, QTableWidgetItem(str(data[2] or '')))
                    table.setItem(r, 4, QTableWidgetItem(str(data[3] or '')))
                    table.setItem(r, 5, QTableWidgetItem(str(data[4] or '')))
                elif typ == 'Bag':
                    table.setItem(r, 1, QTableWidgetItem(str(data[1])))
                    table.setItem(r, 2, QTableWidgetItem(""))
                    table.setItem(r, 3, QTableWidgetItem(str(data[2] or '')))
                    table.setItem(r, 4, QTableWidgetItem(str(data[3] or '')))
                    table.setItem(r, 5, QTableWidgetItem(str(data[4] or '')))

            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.cellClicked.connect(lambda r, _: highlight_row(r))
            v.addWidget(table)

            h = QHBoxLayout()
            edit_btn = QPushButton("Edit Selected")
            close_btn = QPushButton("Close")
            h.addWidget(edit_btn)
            h.addWidget(close_btn)
            v.addLayout(h)

            def on_edit():
                r = selected_row[0]
                if r < 0:
                    QMessageBox.information(self, "Select", "Select a row to edit.")
                    return

                typ = table.item(r, 0).text()
                num = table.item(r, 1).text()

                ed = QDialog(self)
                ed.setWindowTitle(f"Edit {typ} {num}")
                ed_v = QVBoxLayout()

                status_cb = QComboBox()
                status_cb.addItems(["Available", "Assigned", "Maintenance", "Retired"])
                stud_inp = QLineEdit()
                notes_inp = QLineEdit()
                hanger_inp = None

                status_val = table.item(r, 3).text()
                if status_val:
                    idx = status_cb.findText(status_val)
                    if idx >= 0:
                        status_cb.setCurrentIndex(idx)

                stud_cell = table.item(r, 4)
                notes_cell = table.item(r, 5)
                orig_student = stud_cell.text() if stud_cell else ""
                orig_notes = notes_cell.text() if notes_cell else ""
                stud_inp.setText(orig_student)
                notes_inp.setText(orig_notes)

                if typ == 'Coat':
                    hanger_inp = QLineEdit()
                    hanger_cell = table.item(r, 2)
                    orig_hanger = hanger_cell.text() if hanger_cell else ""
                    hanger_inp.setText(orig_hanger)
                    ed_v.addWidget(QLabel("Hanger # (optional):"))
                    ed_v.addWidget(hanger_inp)

                ed_v.addWidget(QLabel("Notes:"))
                ed_v.addWidget(notes_inp)

                be_h = QHBoxLayout()
                be_save = QPushButton("Save")
                be_cancel = QPushButton("Cancel")
                be_h.addWidget(be_save)
                be_h.addWidget(be_cancel)
                ed_v.addLayout(be_h)
                ed.setLayout(ed_v)

                def on_save_edit():
                    entered_notes = notes_inp.text().strip()
                    notes_param = entered_notes if entered_notes != orig_notes else None

                    hanger_param = None
                    if typ == 'Coat' and hanger_inp:
                        entered_hanger = hanger_inp.text().strip()
                        if entered_hanger != orig_hanger:
                            if entered_hanger == "":
                                hanger_param = None
                            else:
                                try:
                                    hanger_param = int(entered_hanger)
                                except ValueError:
                                    QMessageBox.warning(self, "Error", "Hanger must be a number.")
                                    return

                    if typ == 'Shako':
                        db.update_shako(int(num), notes=notes_param)
                    elif typ == 'Coat':
                        db.update_coat(int(num), hanger_num=hanger_param, notes=notes_param)
                    elif typ == 'Pants':
                        db.update_pants(int(num), notes=notes_param)
                    elif typ == 'Bag':
                        db.update_bag(num, notes=notes_param)

                    table.setItem(r, 5, QTableWidgetItem(entered_notes if notes_param else orig_notes))
                    if typ == 'Coat' and hanger_param is not None:
                        table.setItem(r, 2, QTableWidgetItem(str(hanger_param)))

                    highlight_row(r)
                    QMessageBox.information(self, "Saved", "Changes saved.")
                    ed.accept()
                    self.refresh_if_active(self.active_table)


                be_save.clicked.connect(on_save_edit)
                be_cancel.clicked.connect(ed.reject)
                ed.exec()

            edit_btn.clicked.connect(on_edit)
            close_btn.clicked.connect(dlg.accept)

        dlg.setLayout(v)
        dlg.exec()

    def add_uniform_popup(self):
        """
        Open dialog to add a new uniform part(s) without assigning to a student.
        Adds to separate tables based on which fields are filled.
        Prevents duplicate entries based on unique identifiers.
        """
        dialog = AddUniformDialog(self)
        if not dialog.exec():
            return

        uniform_data = dialog.get_uniform_data()
        conn, cursor = db.connect_db()
        added = []
        duplicates = []

        # Add shako if filled
        if uniform_data['shako_num']:
            existing = db.find_shako_by_number(uniform_data['shako_num'])
            if existing:
                duplicates.append(f"Shako #{uniform_data['shako_num']}")
            else:
                cursor.execute(
                    '''INSERT INTO shakos (shako_num, status, notes) VALUES (?, ?, ?)''',
                    (uniform_data['shako_num'], uniform_data['status'], uniform_data['notes'])
                )
                added.append('Shako')

        # Add coat if filled
        if uniform_data['coat_num']:
            existing = db.find_coat_by_number(uniform_data['coat_num'])
            if existing:
                duplicates.append(f"Coat #{uniform_data['coat_num']}")
            else:
                cursor.execute(
                    '''INSERT INTO coats (coat_num, hanger_num, status, notes) VALUES (?, ?, ?, ?)''',
                    (uniform_data['coat_num'], uniform_data['hanger_num'], uniform_data['status'], uniform_data['notes'])
                )
                added.append('Coat')

        # Add pants if filled
        if uniform_data['pants_num']:
            existing = db.find_pants_by_number(uniform_data['pants_num'])
            if existing:
                duplicates.append(f"Pants #{uniform_data['pants_num']}")
            else:
                cursor.execute(
                    '''INSERT INTO pants (pants_num, status, notes) VALUES (?, ?, ?)''',
                    (uniform_data['pants_num'], uniform_data['status'], uniform_data['notes'])
                )
                added.append('Pants')

        # Add garment bag if filled
        if uniform_data['garment_bag']:
            existing = db.find_bag_by_number(uniform_data['garment_bag'])
            if existing:
                duplicates.append(f"Bag {uniform_data['garment_bag']}")
            else:
                cursor.execute(
                    '''INSERT INTO garment_bags (bag_num, status, notes) VALUES (?, ?, ?)''',
                    (uniform_data['garment_bag'], uniform_data['status'], uniform_data['notes'])
                )
                added.append('Garment Bag')

        conn.commit()
        conn.close()
        self.refresh_if_active(self.active_table)

        if added:
            msg = f"Added: {', '.join(added)}"
            if duplicates:
                msg += f"\nSkipped duplicates: {', '.join(duplicates)}"
            QMessageBox.information(self, "Success", msg)
        elif duplicates:
            QMessageBox.warning(self, "Duplicates", f"No new items added.\nDuplicates: {', '.join(duplicates)}")
        else:
            QMessageBox.warning(self, "No Data", "No uniform parts were added. Please fill at least one field.")

    def assign_uniform_popup(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Assign Uniform")
        v = QVBoxLayout()

        sid_in = QLineEdit()
        sid_in.setPlaceholderText("Student ID (9 digits)")
        shako_in = QLineEdit()
        shako_in.setPlaceholderText("Shako # (blank if not assigning)")
        coat_in = QLineEdit()
        coat_in.setPlaceholderText("Coat # (blank if not assigning)")
        pants_in = QLineEdit()
        pants_in.setPlaceholderText("Pants # (blank if not assigning)")
        bag_in = QLineEdit()
        bag_in.setPlaceholderText("Garment Bag (blank if not assigning)")

        glove_cb = QComboBox()
        glove_cb.addItems(["", "XS", "S", "M", "L", "XL"])
        spat_cb = QComboBox()
        spat_cb.addItems(["", "XS", "S", "M", "L", "XL"])

        v.addWidget(QLabel("Enter Student ID and any uniform parts to assign (leave blank for unassigned):"))
        v.addWidget(sid_in)
        v.addWidget(shako_in)
        v.addWidget(coat_in)
        v.addWidget(pants_in)
        v.addWidget(bag_in)
        v.addWidget(QLabel("Glove Size:"))
        v.addWidget(glove_cb)
        v.addWidget(QLabel("Spat Size:"))
        v.addWidget(spat_cb)

        h = QHBoxLayout()
        assign_btn = QPushButton("Assign")
        cancel_btn = QPushButton("Cancel")
        h.addWidget(assign_btn)
        h.addWidget(cancel_btn)
        v.addLayout(h)
        dlg.setLayout(v)

        def do_assign():
            sid = sid_in.text().strip()
            if not sid.isdigit() or len(sid) != 9:
                QMessageBox.warning(self, "Error", "ID must be 9 digits.")
                return
            if not db.get_student_by_id(sid):
                QMessageBox.warning(self, "Error", "No student found.")
                return

            # Collect inputs
            shako = shako_in.text().strip()
            coat = coat_in.text().strip()
            pants = pants_in.text().strip()
            bag = bag_in.text().strip()
            glove_size = glove_cb.currentText().strip() or None
            spat_size = spat_cb.currentText().strip() or None

            shako_num = int(shako) if shako else None
            coat_num = int(coat) if coat else None
            pants_num = int(pants) if pants else None
            bag_val = bag if bag else None
            hanger_num = None

            # Check if student already has uniform parts
            current = db.get_uniforms_by_student_id(sid)  # <-- implement this helper
            already_assigned = []
            if current:
                if shako_num and current.get("shako_num"):
                    already_assigned.append(f"Shako (#{current['shako_num']})")
                if coat_num and current.get("coat_num"):
                    already_assigned.append(f"Coat (#{current['coat_num']})")
                if pants_num and current.get("pants_num"):
                    already_assigned.append(f"Pants (#{current['pants_num']})")
                if bag_val and current.get("garment_bag"):
                    already_assigned.append(f"Bag ({current['garment_bag']})")

            if already_assigned:
                QMessageBox.warning(
                    self,
                    "Already Assigned",
                    f"Student {sid} already has: {', '.join(already_assigned)}.\n"
                    "Unassign first before reassigning."
                )
                return

            # Validate inventory
            missing, not_available = [], []

            if shako_num is not None:
                if not db.find_shako_by_number(shako_num):
                    missing.append(f"Shako #{shako_num}")
                elif not db.is_shako_available(shako_num):
                    not_available.append(f"Shako #{shako_num}")

            if coat_num is not None:
                coat_row = db.find_coat_by_number(coat_num)
                if not coat_row:
                    missing.append(f"Coat #{coat_num}")
                elif not db.is_coat_available(coat_num):
                    not_available.append(f"Coat #{coat_num}")
                else:
                    try:
                        hanger_num = int(coat_row[2]) if coat_row and coat_row[2] is not None else None
                    except Exception:
                        hanger_num = None

            if pants_num is not None:
                if not db.find_pants_by_number(pants_num):
                    missing.append(f"Pants #{pants_num}")
                elif not db.is_pants_available(pants_num):
                    not_available.append(f"Pants #{pants_num}")

            if bag_val:
                if not db.find_bag_by_number(bag_val):
                    missing.append(f"Bag {bag_val}")
                elif not db.is_bag_available(bag_val):
                    not_available.append(f"Bag {bag_val}")

            if missing:
                QMessageBox.warning(self, "Missing Parts", f"The following parts are not in inventory: {', '.join(missing)}.")
                return
            if not_available:
                QMessageBox.warning(self, "Not Available", f"The following parts are not available: {', '.join(not_available)}")
                return

            # Unified assignment
            assign_kwargs = {}
            if shako_num is not None:
                assign_kwargs["shako_num"] = shako_num
            if coat_num is not None:
                assign_kwargs["coat_num"] = coat_num
            if pants_num is not None:
                assign_kwargs["pants_num"] = pants_num
            if bag_val:
                assign_kwargs["garment_bag"] = bag_val
            if hanger_num is not None:
                assign_kwargs["hanger_num"] = hanger_num

            db.assign_uniform_piece(sid, **assign_kwargs)

            # Update inventory tables
            if shako_num is not None:
                db.update_shako(shako_num, student_id=sid, status='Assigned')
            if coat_num is not None:
                db.update_coat(coat_num, student_id=sid, status='Assigned', hanger_num=hanger_num)
            if pants_num is not None:
                db.update_pants(pants_num, student_id=sid, status='Assigned')
            if bag_val:
                db.update_bag(bag_val, student_id=sid, status='Assigned')

            # Update student glove/spat size
            if glove_size is not None:
                db.update_student(sid, "glove_size", glove_size)
            if spat_size is not None:
                db.update_student(sid, "spat_size", spat_size)

            QMessageBox.information(self, "Success", "Uniform assigned.")
            dlg.accept()
            self.refresh_if_active(self.active_table)

        assign_btn.clicked.connect(do_assign)
        cancel_btn.clicked.connect(dlg.reject)
        dlg.exec()

    def return_uniform_popup(self):
        sid, ok = QInputDialog.getText(self, "Return Uniform", "Enter Student ID:")
        if not ok or not sid.strip():
            return
        sid = sid.strip()
        if not sid.isdigit() or len(sid) != 9:
            QMessageBox.warning(self, "Error", "ID must be 9 digits.")
            return
        if not db.get_student_by_id(sid):
            QMessageBox.warning(self, "Error", "No student found.")
            return

        # Call the DB helper
        db.return_uniform_piece(sid)

        QMessageBox.information(self, "Success", "Uniform returned.")
        self.refresh_if_active(self.active_table)

    def show_outstanding_uniforms(self):
        opts = ["<All>"] + self.sections
        section, ok = QInputDialog.getItem(
            self, "Outstanding Uniforms",
            "Filter by section:", opts, 0, False
        )
        if ok and section != "<All>":
            rows = db.get_students_with_outstanding_uniforms_by_section(section)
        else:
            rows = db.get_students_with_outstanding_uniforms()
        if not rows:
            QMessageBox.information(self, "Info", "All uniforms are accounted for.")
            return
        msg = "\n".join(
            f"{r[0]} {r[1]}: Shako {r[2]}, Hanger {r[3]}, Bag {r[4]}, Coat {r[5]}, Pants {r[6]}"
            for r in rows
        )
        self.show_printable_results("Outstanding Uniforms", msg)

    def delete_all_uniforms(self):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete ALL uniforms? This cannot be undone.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db.delete_all_shakos()
            db.delete_all_coats()
            db.delete_all_pants()
            db.delete_all_garment_bags()
            self.refresh_if_active(self.active_table)

    # --------------------------------------------------------------------------
    # Instrument methods
    # --------------------------------------------------------------------------
    def find_instrument_popup(self):
        """
        Opens a dialog to search for instruments by serial number and/or name.
        Displays matching results in a table with clear row highlighting and edit functionality.
        """
        dlg = AddInstrumentDialog(self, find_mode=True, instruments=self.sections)
        if not dlg.exec():
            return

        q = dlg.get_instrument_data()
        serial_query = q.get('instrument_serial')
        name_query = q.get('instrument_name')

        found_rows = []
        for r in db.get_all_instruments():
            # Skip if both queries are blank
            if not serial_query and not name_query:
                continue

            serial_match = r[3] == serial_query if serial_query else True
            name_match = name_query.lower() in r[2].lower() if name_query and r[2] else True

            # Only include rows that match all provided filters
            if serial_query and name_query:
                if serial_match and name_match:
                    found_rows.append(r)
            elif serial_query and serial_match:
                found_rows.append(r)
            elif name_query and name_match:
                found_rows.append(r)



        dlg2 = QDialog(self)
        dlg2.setWindowTitle("Find Instrument Results")
        v = QVBoxLayout()
        if not found_rows:
            v.addWidget(QLabel("No matching instrument found."))
        else:
            table = QTableWidget()
            table.setColumnCount(9)
            table.setHorizontalHeaderLabels([
                "ID", "Student", "Name", "Serial", "Case", "Model",
                "Condition", "Status", "Notes"
            ])
            table.setRowCount(len(found_rows))

            # Manual row tracking
            selected_row = [-1]

            def highlight_row(row_index):
                # Clear previous highlight
                for r in range(table.rowCount()):
                    for c in range(table.columnCount()):
                        item = table.item(r, c)
                        if item:
                            item.setBackground(QColor("#1e1e1e"))

                # Apply highlight to selected row
                for c in range(table.columnCount()):
                    item = table.item(row_index, c)
                    if item:
                        item.setBackground(QColor("#3c3c3c"))

                selected_row[0] = row_index

            for r, row in enumerate(found_rows):
                for c, val in enumerate([
                    row[0], row[1], row[2], row[3], row[4],
                    row[5], row[6], row[7], row[8]
                ]):
                    item = QTableWidgetItem(str(val) if val is not None else "")
                    table.setItem(r, c, item)

            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.cellClicked.connect(lambda r, _: highlight_row(r))
            v.addWidget(table)

            h = QHBoxLayout()
            edit_btn = QPushButton("Edit Selected")
            close_btn = QPushButton("Close")
            h.addWidget(edit_btn)
            h.addWidget(close_btn)
            v.addLayout(h)

            def on_edit():
                r = selected_row[0]
                if r < 0:
                    QMessageBox.warning(self, "Select", "Select a row to edit.")
                    return

                inst_id = int(table.item(r, 0).text())
                ed = QDialog(self)
                ed.setWindowTitle(f"Edit Instrument {inst_id}")
                ed_v = QVBoxLayout()

                instrument_cb = QComboBox()
                instrument_cb.addItems(self.sections)
                instrument_cb.setCurrentText(table.item(r, 2).text())

                serial_in = QLineEdit(table.item(r, 3).text())
                case_in = QLineEdit(table.item(r, 4).text())
                model_in = QLineEdit(table.item(r, 5).text())

                cond_cb = QComboBox()
                cond_cb.addItems(["Excellent", "Good", "Fair", "Poor"])
                cond_cb.setCurrentText(table.item(r, 6).text())

                status_cb = QComboBox()
                status_cb.addItems(["Available", "Assigned", "Maintenance", "Retired"])
                status_cb.setCurrentText(table.item(r, 7).text())

                notes_in = QLineEdit(table.item(r, 8).text())

                ed_v.addWidget(QLabel("Instrument:"))
                ed_v.addWidget(instrument_cb)
                ed_v.addWidget(QLabel("Serial:"))
                ed_v.addWidget(serial_in)
                ed_v.addWidget(QLabel("Case:"))
                ed_v.addWidget(case_in)
                ed_v.addWidget(QLabel("Model:"))
                ed_v.addWidget(model_in)
                ed_v.addWidget(QLabel("Condition:"))
                ed_v.addWidget(cond_cb)
                ed_v.addWidget(QLabel("Status:"))
                ed_v.addWidget(status_cb)
                ed_v.addWidget(QLabel("Notes:"))
                ed_v.addWidget(notes_in)

                be_h = QHBoxLayout()
                be_save = QPushButton("Save")
                be_cancel = QPushButton("Cancel")
                be_h.addWidget(be_save)
                be_h.addWidget(be_cancel)
                ed_v.addLayout(be_h)
                ed.setLayout(ed_v)

                def on_save():
                    db.update_instrument_by_id(
                        inst_id,
                        name=instrument_cb.currentText().strip() or None,
                        case=case_in.text().strip() or None,
                        status=status_cb.currentText(),
                        notes=notes_in.text().strip() or None,
                        model=model_in.text().strip() or None,
                        condition=cond_cb.currentText()
                    )
                    QMessageBox.information(self, "Saved", "Instrument updated.")
                    ed.accept()

                    # Update table row
                    table.setItem(r, 2, QTableWidgetItem(instrument_cb.currentText().strip()))
                    table.setItem(r, 3, QTableWidgetItem(serial_in.text().strip()))
                    table.setItem(r, 4, QTableWidgetItem(case_in.text().strip()))
                    table.setItem(r, 5, QTableWidgetItem(model_in.text().strip()))
                    table.setItem(r, 6, QTableWidgetItem(cond_cb.currentText()))
                    table.setItem(r, 7, QTableWidgetItem(status_cb.currentText()))
                    table.setItem(r, 8, QTableWidgetItem(notes_in.text().strip()))

                    highlight_row(r)  # Reapply highlight after update
                    self.refresh_if_active("instruments")
                be_save.clicked.connect(on_save)
                be_cancel.clicked.connect(ed.reject)
                ed.exec()

            edit_btn.clicked.connect(on_edit)
            close_btn.clicked.connect(dlg2.accept)

        dlg2.setLayout(v)
        dlg2.exec()

    def add_instrument_popup(self):
        """
        Opens a dialog to add a new instrument to the database.
        This version does not assign the instrument to a student.
        """
        # Launch the instrument dialog in 'add' mode
        dialog = AddInstrumentDialog(self, instruments=self.sections)

        # If the user clicks Save (dialog accepted)
        if dialog.exec():
            # Retrieve the instrument data entered by the user
            instrument_data = dialog.get_instrument_data()

            # Connect to the database
            conn, cursor = db.connect_db()

            # Insert the new instrument record
            cursor.execute('''
                INSERT INTO instruments (
                    instrument_name, instrument_serial, instrument_case,
                    model, condition, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                instrument_data['instrument_name'],
                instrument_data['instrument_serial'],
                instrument_data['instrument_case'],
                instrument_data['model'],
                instrument_data['condition'],
                instrument_data['status'],
                instrument_data['notes']
            ))

            # Commit changes and close connection
            conn.commit()
            conn.close()
            self.refresh_if_active(self.active_table)

            # Notify the user of success
            QMessageBox.information(self, "Success", "New instrument added successfully!")

    def assign_instrument_popup(self):
        """
        Popup workflow to assign an instrument to a student.
        1. Prompt for Student ID.
        2. Prompt for instrument type and serial number.
        3. Look up matching instruments.
        4. If available, assign it to the student.
        """
        # Step 1: Get Student ID
        sid, ok = QInputDialog.getText(self, "Assign Instrument", "Enter Student ID:")
        if not ok or not sid.strip():
            return
        sid = sid.strip()
        if not sid.isdigit() or len(sid) != 9:
            QMessageBox.warning(self, "Error", "ID must be 9 digits.")
            return
        if not db.get_student_by_id(sid):
            QMessageBox.warning(self, "Error", "No student found.")
            return

        # Step 2: Choose instrument type and serial
        type_dialog = QDialog(self)
        type_dialog.setWindowTitle("Select Instrument Type")
        type_layout = QVBoxLayout()

        instrument_cb = QComboBox()
        instrument_cb.addItems(self.sections)  # self.sections should contain instrument types
        type_layout.addWidget(QLabel("Select Instrument Type:"))
        type_layout.addWidget(instrument_cb)

        serial_in = QLineEdit()
        type_layout.addWidget(QLabel("Enter Serial #:"))
        type_layout.addWidget(serial_in)

        btn_layout = QHBoxLayout()
        next_btn = QPushButton("Next")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(next_btn)
        btn_layout.addWidget(cancel_btn)
        type_layout.addLayout(btn_layout)

        type_dialog.setLayout(type_layout)

        def proceed():
            serial = serial_in.text().strip()
            if not serial:
                QMessageBox.warning(self, "Error", "Serial number required.")
                return
            instrument_type = instrument_cb.currentText()
            type_dialog.accept()

            # Step 3: Find matching instruments
            matches = [
                i for i in db.get_all_instruments()
                if i[2] == instrument_type and i[3] == serial
            ]

            if not matches:
                create = QMessageBox.question(
                    self, "Instrument Not Found",
                    f"No {instrument_type} with Serial '{serial}' found. Create new?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if create == QMessageBox.StandardButton.Yes:
                    self.add_instrument_popup()
                return

            available = [i for i in matches if i[7] == 'Available']
            if not available:
                QMessageBox.warning(self, "Not Available", f"No available {instrument_type} with Serial '{serial}'.")
                return

            # Step 4: Assign instrument
            def assign_instrument(inst):
                case, ok3 = QInputDialog.getText(
                    self, "Assign Instrument", "Case:", text=str(inst[4] or '')
                )
                if not ok3:
                    return

                conn, cursor = db.connect_db()
                if case:
                    cursor.execute(
                        """
                        UPDATE instruments
                        SET status = 'Assigned',
                            student_id = ?,
                            instrument_case = ?
                        WHERE id = ?
                        """,
                        (sid, case.strip(), inst[0])
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE instruments
                        SET status = 'Assigned',
                            student_id = ?
                        WHERE id = ?
                        """,
                        (sid, inst[0])
                    )
                conn.commit()
                conn.close()

                QMessageBox.information(self, "Success", f"Instrument ID {inst[0]} assigned.")
                self.refresh_if_active("instruments")
                self.refresh_if_active("students")

                self.refresh_if_active(self.active_table)

            if len(available) == 1:
                assign_instrument(available[0])
            else:
                dlg = QDialog(self)
                dlg.setWindowTitle("Select Instrument to Assign")
                v = QVBoxLayout()
                table = QTableWidget()
                table.setColumnCount(6)
                table.setHorizontalHeaderLabels(["ID", "Name", "Serial", "Case", "Status", "Notes"])
                table.setRowCount(len(available))
                for r, row in enumerate(available):
                    table.setItem(r, 0, QTableWidgetItem(str(row[0])))  # ID
                    table.setItem(r, 1, QTableWidgetItem(str(row[2] or '')))  # Name
                    table.setItem(r, 2, QTableWidgetItem(str(row[3] or '')))  # Serial
                    table.setItem(r, 3, QTableWidgetItem(str(row[4] or '')))  # Case
                    table.setItem(r, 4, QTableWidgetItem(str(row[7] or '')))  # Status
                    table.setItem(r, 5, QTableWidgetItem(str(row[8] or '')))  # Notes
                table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                v.addWidget(QLabel(f"Multiple {instrument_type}s found with Serial '{serial}'. Select one to assign:"))
                v.addWidget(table)

                h = QHBoxLayout()
                assign_btn = QPushButton("Assign Selected")
                cancel_btn = QPushButton("Cancel")
                h.addWidget(assign_btn)
                h.addWidget(cancel_btn)
                v.addLayout(h)
                dlg.setLayout(v)

                def do_assign():
                    row = table.currentRow()
                    if row < 0:
                        QMessageBox.warning(self, "Select", "Select a row to assign.")
                        return
                    assign_instrument(available[row])
                    dlg.accept()

                assign_btn.clicked.connect(do_assign)
                cancel_btn.clicked.connect(dlg.reject)
                dlg.exec()

        next_btn.clicked.connect(proceed)
        cancel_btn.clicked.connect(type_dialog.reject)
        type_dialog.exec()

    def return_instrument_popup(self):
        sid, ok = QInputDialog.getText(self, "Return Instrument", "Enter Student ID:")
        if not ok or not sid.strip():
            return
        sid = sid.strip()
        if not sid.isdigit() or len(sid) != 9:
            QMessageBox.warning(self, "Error", "ID must be 9 digits.")
            return
        if not db.get_student_by_id(sid):
            QMessageBox.warning(self, "Error", "No student found.")
            return
        db.return_instrument(sid)
        QMessageBox.information(self, "Success", "Instrument returned.")
        self.refresh_if_active(self.active_table)

    def show_outstanding_instruments(self):
        """
        Display all instruments that are currently checked out (not returned).
        Optionally filters the results by student section.
        """
        # Build dropdown options: <All> plus each section name
        opts = ["<All>"] + self.sections

        # Prompt user to select a section filter
        section, ok = QInputDialog.getItem(
            self,
            "Outstanding Instruments",
            "Filter by section:",
            opts,
            0,
            False
        )

        # Fetch instrument records based on filter
        if ok and section != "<All>":
            # Filter by student section
            rows = db.get_students_with_outstanding_instruments_by_section(section)
        else:
            # No filter — get all outstanding instruments
            rows = db.get_students_with_outstanding_instruments()

        # If no results, show message and exit
        if not rows:
            QMessageBox.information(self, "Info", "All instruments are accounted for.")
            return

        # Format results into a printable string
        msg = "\n".join(
            f"{r[0]} {r[1]}: {r[2]} | Serial: {r[4]} | Case: {r[5]}"
            for r in rows
        )


        # Display results in a scrollable, printable dialog
        self.show_printable_results("Outstanding Instruments", msg)

    def delete_all_instruments(self):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete ALL instruments? This cannot be undone.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db.delete_all_instruments()
            self.refresh_if_active(self.active_table)

    # --------------------------------------------------------------------------
    # Backup & Restore
    # --------------------------------------------------------------------------

    def create_backup(self):
        """Create a CSV backup of all tables in a consistent format."""

        # Ask user where to save
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Create Backup",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if not file_path:
            return

        try:
            conn, cursor = db.connect_db()
            with open(file_path, "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)

                # --- Students ---
                cursor.execute("""
                    SELECT student_id, first_name, last_name, phone, email,
                        year_came_up, status, guardian_name, guardian_phone, section,
                        glove_size, spat_size
                    FROM students
                """)
                for row in cursor.fetchall():
                    writer.writerow(["STUDENTS", *row])

                # --- Uniforms ---
                cursor.execute("""
                    SELECT id, student_id, shako_num, hanger_num, garment_bag,
                        coat_num, pants_num, status, notes
                    FROM uniforms
                """)
                for row in cursor.fetchall():
                    writer.writerow(["UNIFORMS", *row])

                # --- Shakos ---
                cursor.execute("SELECT id, shako_num, status, student_id, notes FROM shakos")
                for row in cursor.fetchall():
                    writer.writerow(["SHAKOS", *row])

                # --- Coats ---
                cursor.execute("SELECT id, coat_num, hanger_num, status, student_id, notes FROM coats")
                for row in cursor.fetchall():
                    writer.writerow(["COATS", *row])

                # --- Pants ---
                cursor.execute("SELECT id, pants_num, status, student_id, notes FROM pants")
                for row in cursor.fetchall():
                    writer.writerow(["PANTS", *row])

                # --- Bags ---
                cursor.execute("SELECT id, bag_num, status, student_id, notes FROM garment_bags")
                for row in cursor.fetchall():
                    writer.writerow(["BAGS", *row])

                # --- Instruments ---
                cursor.execute("""
                    SELECT id, student_id, instrument_name, instrument_serial,
                        instrument_case, model, condition, status, notes
                    FROM instruments
                """)
                for row in cursor.fetchall():
                    writer.writerow(["INSTRUMENTS", *row])

            conn.close()

            QMessageBox.information(self, "Backup Complete", f"Backup saved to:\n{file_path}")

        except Exception as e:
            QMessageBox.warning(self, "Backup Failed", f"Error: {e}")

    def use_backup(self):
        """
        Restore the database from a CSV backup snapshot.

        Format: section,field1,field2,...
        Sections: STUDENTS, SHAKOS, COATS, PANTS, BAGS, UNIFORMS, INSTRUMENTS
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Use Backup", "", "CSV Files (*.csv);;All Files (*)"
        )
        if not file_path:
            return

        try:
            counts = {"STUDENTS": 0, "SHAKOS": 0, "COATS": 0, "PANTS": 0,
                    "BAGS": 0, "UNIFORMS": 0, "INSTRUMENTS": 0}

            # Open one connection for the whole restore
            conn, cur = db.connect_db()

            # Clear all tables first (snapshot restore)
            for table in ["students", "shakos", "coats", "pants", "garment_bags", "uniforms", "instruments"]:
                cur.execute(f"DELETE FROM {table}")
            conn.commit()

            with open(file_path, newline='', encoding='utf-8') as fh:
                reader = csv.reader(fh)
                for row in reader:
                    if not row:
                        continue
                    section = row[0].strip().upper()
                    parts = [p.strip() if p and p.strip() != '' else None for p in row[1:]]
                    try:
                        if section == 'STUDENTS':
                            cur.execute("""
                                INSERT INTO students (
                                    student_id, first_name, last_name, phone, email,
                                    year_came_up, status, guardian_name, guardian_phone, section,
                                    glove_size, spat_size
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, tuple(parts[:12]))
                            counts['STUDENTS'] += 1

                        elif section == 'UNIFORMS':
                            cur.execute("""
                                INSERT INTO uniforms (
                                    id, student_id, shako_num, hanger_num, garment_bag,
                                    coat_num, pants_num, status, notes
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, tuple(parts[:9]))
                            counts['UNIFORMS'] += 1

                        elif section == 'INSTRUMENTS':
                            cur.execute("""
                                INSERT INTO instruments (
                                    id, student_id, instrument_name, instrument_serial,
                                    instrument_case, model, condition, status, notes
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, tuple(parts[:9]))
                            counts['INSTRUMENTS'] += 1

                        elif section == 'SHAKOS':
                            cur.execute("""
                                INSERT INTO shakos (id, shako_num, status, student_id, notes)
                                VALUES (?, ?, ?, ?, ?)
                            """, tuple(parts[:5]))
                            counts['SHAKOS'] += 1

                        elif section == 'COATS':
                            cur.execute("""
                                INSERT INTO coats (id, coat_num, hanger_num, status, student_id, notes)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, tuple(parts[:6]))
                            counts['COATS'] += 1

                        elif section == 'PANTS':
                            cur.execute("""
                                INSERT INTO pants (id, pants_num, status, student_id, notes)
                                VALUES (?, ?, ?, ?, ?)
                            """, tuple(parts[:5]))
                            counts['PANTS'] += 1

                        elif section == 'BAGS':
                            cur.execute("""
                                INSERT INTO garment_bags (id, bag_num, status, student_id, notes)
                                VALUES (?, ?, ?, ?, ?)
                            """, tuple(parts[:5]))
                            counts['BAGS'] += 1

                    except Exception as e:
                        print("Restore line failed", section, row, e)

            conn.commit()
            conn.close()

            self.refresh_if_active(self.active_table)
            summary = "\n".join(f"{k}: {v}" for k, v in counts.items())
            QMessageBox.information(self, "Restore Complete",
                                    f"Backup restored successfully.\n\nRestored:\n{summary}")

        except Exception as e:
            QMessageBox.warning(self, "Restore Failed", f"Error: {e}")
