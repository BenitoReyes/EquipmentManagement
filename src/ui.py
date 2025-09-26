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
from PyQt6.QtGui import QPixmap, QImage, QPainter, QIcon, QFontMetrics
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
    """
    Resolve a path to an embedded resource file, whether running as a script
    or as a frozen executable (e.g., PyInstaller).
    """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def load_stylesheet():
    path = resource_path("styles.qss")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def desanitize(value):
    """
    Convert empty or 'none' strings to None.
    """
    return None if not value or value.strip().lower() == "none" else value.strip()


class EquipmentManagementUI(QWidget):
    def show_printable_results(self, title, text):
        """
        Show a dialog with the given text, and provide Print, Full Screen, and Close options.
        """
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        vbox = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(text)
        vbox.addWidget(text_edit)

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
                font = text_edit.font()
                metrics = QFontMetrics(font)
                line_height = metrics.lineSpacing()
                lines = text.split('\n')
                y = 0
                for line in lines:
                    painter.drawText(0, y + line_height, line)
                    y += line_height
                painter.end()

        def on_fullscreen():
            fs = QDialog(self)
            fs.setWindowTitle(title + " (Full Screen)")
            box = QVBoxLayout()
            fs_text = QTextEdit()
            fs_text.setReadOnly(True)
            fs_text.setText(text)
            fs_text.setFont(text_edit.font())
            box.addWidget(fs_text)
            fs.setLayout(box)
            fs.showMaximized()
            fs.exec()

        print_btn.clicked.connect(on_print)
        fs_btn.clicked.connect(on_fullscreen)
        close_btn.clicked.connect(dlg.accept)
        dlg.exec()
    def use_backup(self):
        """
        Restore students, uniforms, and instruments from a backup file.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Restore from Backup", "", "Text Files (*.txt);;All Files (*)")
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                section = None
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("[STUDENTS]"):
                        section = "students"
                        continue
                    elif line.startswith("[UNIFORMS]"):
                        section = "uniforms"
                        continue
                    elif line.startswith("[INSTRUMENTS]"):
                        section = "instruments"
                        continue
                    if section == "students":
                        # Format: student_id,first_name,last_name,status,section,phone,email,guardian_name,guardian_phone,year_came_up
                        parts = line.split(",")
                        if len(parts) >= 10:
                            db.add_or_update_student(*[p.strip() for p in parts[:10]])
                    elif section == "uniforms":
                        # Format: id,student_id,shako_num,hanger_num,garment_bag,coat_num,pants_num,status,is_checked_in,notes
                        parts = line.split(",")
                        if len(parts) >= 10:
                            db.add_or_update_uniform(*[p.strip() for p in parts[:10]])
                    elif section == "instruments":
                        # Format: id,student_id,name,serial,case,model,condition,status,is_checked_in,notes
                        parts = line.split(",")
                        if len(parts) >= 10:
                            db.add_or_update_instrument(*[p.strip() for p in parts[:10]])
            self.refresh_table()
            QMessageBox.information(self, "Restore Complete", "Backup restored successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Restore Failed", f"Error: {e}")
    def import_students_from_csv(self):
        """
        Import students from a CSV file. Overwrite existing students with the same ID.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Students from CSV", "", "CSV Files (*.csv);;All Files (*)")
        if not file_path:
            return
        count_added = 0
        count_updated = 0
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                sid = row.get('student_id') or row.get('Student ID') or row.get('ID')
                if not sid or not sid.isdigit() or len(sid) != 9:
                    continue
                # Prepare fields (adjust as needed for your schema)
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
                }
                # Check if student exists
                existing = db.get_student_by_id(sid)
                if existing:
                    db.update_student(
                        sid,
                        student_data['first_name'],
                        student_data['last_name'],
                        student_data['status'],
                        student_data['section'],
                        student_data['phone'],
                        student_data['email'],
                        student_data['guardian_name'],
                        student_data['guardian_phone'],
                        student_data['year_came_up']
                    )
                    count_updated += 1
                else:
                    db.add_student(
                        sid,
                        student_data['first_name'],
                        student_data['last_name'],
                        student_data['status'],
                        student_data['section'],
                        student_data['phone'],
                        student_data['email'],
                        student_data['guardian_name'],
                        student_data['guardian_phone'],
                        student_data['year_came_up']
                    )
                    count_added += 1
        self.refresh_table()
        QMessageBox.information(self, "Import Complete", f"Added: {count_added}\nUpdated: {count_updated}")
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

    def show_students_table(self):
        # Make the student table occupy the full main area by removing other widgets
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if item and item.widget() and item.widget() is not self.student_table and item.widget() is not None:
                item.widget().setParent(None)
        if not hasattr(self, 'student_table') or self.student_table.parent() is None:
            self.student_table = QTableWidget()
            self.layout.addWidget(self.student_table)
        self.student_table.show()
        self.refresh_table()

    def find_uniform_popup(self):
        """Open the AddUniformDialog in find mode and return matching component values."""
        dialog = AddUniformDialog(self, find_mode=True)
        if not dialog.exec():
            return
        q = dialog.get_uniform_data()

        found_rows = []
        # Collect each component's found row as a dict for the results dialog
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

        # Show the richer results dialog
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
            for r, rowinfo in enumerate(found_rows):
                typ = rowinfo['type']
                data = rowinfo['data']
                table.setItem(r, 0, QTableWidgetItem(typ))
                # data tuple varies by type; normalize
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
            v.addWidget(table)

            # Edit / Close buttons
            h = QHBoxLayout()
            edit_btn = QPushButton("Edit Selected")
            close_btn = QPushButton("Close")
            h.addWidget(edit_btn)
            h.addWidget(close_btn)
            v.addLayout(h)

            def on_edit():
                r = table.currentRow()
                if r < 0:
                    QMessageBox.information(self, "Select", "Select a row to edit.")
                    return
                typ = table.item(r, 0).text()
                num = table.item(r, 1).text()
                # Open a simple edit dialog to change status, student, notes
                ed = QDialog(self)
                ed.setWindowTitle(f"Edit {typ} {num}")
                ed_v = QVBoxLayout()
                status_cb = QComboBox()
                status_cb.addItems(["Available", "Assigned", "Maintenance", "Retired"])
                stud_inp = QLineEdit()
                notes_inp = QLineEdit()
                hanger_inp = None
                # prefill
                status_in_table = table.item(r, 3).text()
                if status_in_table:
                    idx = status_cb.findText(status_in_table)
                    if idx >= 0:
                        status_cb.setCurrentIndex(idx)
                # Safely prefill student and notes (cells may be None)
                stud_cell = table.item(r, 4)
                notes_cell = table.item(r, 5)
                orig_student = stud_cell.text() if stud_cell is not None else ""
                orig_notes = notes_cell.text() if notes_cell is not None else ""
                stud_inp.setText(orig_student)
                notes_inp.setText(orig_notes)
                # If coat, include hanger number field (column 2)
                if typ == 'Coat':
                    hanger_inp = QLineEdit()
                    hanger_cell = table.item(r, 2)
                    orig_hanger = hanger_cell.text() if hanger_cell is not None else ""
                    hanger_inp.setText(orig_hanger)
                    ed_v.addWidget(QLabel("Hanger # (optional):"))
                    ed_v.addWidget(hanger_inp)
                ed_v.addWidget(QLabel("Status:"))
                ed_v.addWidget(status_cb)
                ed_v.addWidget(QLabel("Student ID (9 digits or blank):"))
                ed_v.addWidget(stud_inp)
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
                    # Determine original values
                    orig_status = status_in_table or ""
                    # Compute changed values: only send params that actually changed
                    new_status = status_cb.currentText()
                    status_param = new_status if new_status != orig_status else None

                    entered_student = stud_inp.text().strip()
                    student_param = None
                    if entered_student != orig_student:
                        # empty string -> clear assignment (use None), otherwise send string
                        student_param = entered_student if entered_student != "" else None

                    entered_notes = notes_inp.text().strip()
                    notes_param = None
                    if entered_notes != orig_notes:
                        # allow empty string to clear notes
                        notes_param = entered_notes

                    hanger_param = None
                    if typ == 'Coat' and hanger_inp is not None:
                        entered_hanger = hanger_inp.text().strip()
                        # compare to original
                        if entered_hanger != orig_hanger:
                            # empty -> set to None (cleared), else try to convert to int
                            if entered_hanger == "":
                                hanger_param = None
                            else:
                                try:
                                    hanger_param = int(entered_hanger)
                                except ValueError:
                                    QMessageBox.warning(self, "Error", "Hanger must be a number.")
                                    return

                    # Update DB depending on type; only pass changed params (None means don't update for notes/status logic in helpers)
                    if typ == 'Shako':
                        db.update_shako(int(num), student_id=student_param, status=status_param, notes=notes_param)
                    elif typ == 'Coat':
                        db.update_coat(int(num), student_id=student_param, status=status_param, hanger_num=hanger_param, notes=notes_param)
                    elif typ == 'Pants':
                        db.update_pants(int(num), student_id=student_param, status=status_param, notes=notes_param)
                    elif typ == 'Bag':
                        db.update_bag(num, student_id=student_param, status=status_param, notes=notes_param)

                    # Refresh the row in the results table in-place so the dialog can remain open
                    # Determine displayed values after update
                    disp_status = new_status if status_param is not None else orig_status
                    disp_student = entered_student if entered_student != orig_student else orig_student
                    disp_notes = notes_param if notes_param is not None else orig_notes
                    # Update table cells safely
                    table.setItem(r, 3, QTableWidgetItem(disp_status))
                    table.setItem(r, 4, QTableWidgetItem(disp_student))
                    table.setItem(r, 5, QTableWidgetItem(disp_notes))
                    if typ == 'Coat' and hanger_param is not None:
                        table.setItem(r, 2, QTableWidgetItem(str(hanger_param) if hanger_param is not None else ""))

                    QMessageBox.information(self, "Saved", "Changes saved.")
                    ed.accept()

                be_save.clicked.connect(on_save_edit)
                be_cancel.clicked.connect(ed.reject)
                ed.exec()

            edit_btn.clicked.connect(on_edit)
            close_btn.clicked.connect(dlg.accept)

        dlg.setLayout(v)
        dlg.exec()

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
        # else: cancel

    def delete_all_uniforms(self):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete ALL uniforms? This cannot be undone.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db.delete_all_shakos()
            db.delete_all_coats()
            db.delete_all_pants()
            db.delete_all_garment_bags()
            self.show_uniform_table_screen()

    def delete_all_instruments(self):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete ALL instruments? This cannot be undone.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db.delete_all_instruments()
            self.view_all_instruments_table()
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
        # else: cancel

    def delete_all_uniforms(self):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete ALL uniforms? This cannot be undone.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db.delete_all_shakos()
            db.delete_all_coats()
            db.delete_all_pants()
            db.delete_all_garment_bags()
            self.show_uniform_table_screen()

    def delete_all_instruments(self):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete ALL instruments? This cannot be undone.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db.delete_all_instruments()
            self.view_all_instruments_table()
    def show_uniform_table_screen(self):
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




    def open_uniform_inventory(self):
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

    def show_about_dialog(self):
        QMessageBox.information(
            self, "About This App",
            "Made by: Benito Reyes, Fall '21 Trumpet KKPSI DI,, SPR '24 Ace\n\n"
            "Code: https://github.com/BenitoReyes/EquipmentManagement"
        )

    def sanitize(self, value):
        return "" if value is None or str(value).strip().lower() == "none" else str(value)

    # --------------------------------------------------------------------------
    # Table view methods
    # --------------------------------------------------------------------------

    def refresh_table(self):
        """
        Show the main students view with joined uniform/instrument data.
        """
        headers = [
            "Student ID", "Last Name", "First Name", "Status", "Section",
            "Phone", "Email", "Guardian Name", "Guardian Phone", "Year Came Up",
            "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #",
            "Instrument Name", "Instrument Serial", "Instrument Case"
        ]
        self.student_table.setColumnCount(len(headers))
        self.student_table.setHorizontalHeaderLabels(headers)
        self.student_table.setRowCount(0)

        rows = db.get_students_with_uniforms_and_instruments()
        for r, row in enumerate(rows):
            self.student_table.insertRow(r)
            for c, val in enumerate(row):
                text = "" if val is None else str(val)
                self.student_table.setItem(r, c, QTableWidgetItem(text))

        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.student_table.setVerticalHeaderLabels(["" for _ in range(self.student_table.rowCount())])
        self.student_table.sortItems(1)

    def view_all_uniforms_table(self):
        """
        Show all uniform records in the table.
        """
        headers = [
            "Record ID", "Student ID", "Shako #", "Hanger #",
            "Garment Bag", "Coat #", "Pants #", "Status",
            "Checked In", "Notes"
        ]
        self.student_table.setColumnCount(len(headers))
        self.student_table.setHorizontalHeaderLabels(headers)
        self.student_table.setRowCount(0)

        rows = db.get_all_uniforms()
        for r, u in enumerate(rows):
            self.student_table.insertRow(r)
            for c, val in enumerate(u):
                if isinstance(val, bool):  # For is_checked_in
                    text = "Yes" if val else "No"
                else:
                    text = "" if val is None else str(val)
                self.student_table.setItem(r, c, QTableWidgetItem(text))

        self.student_table.resizeColumnsToContents()

    def view_all_instruments_table(self):
        """
        Show all instrument records in the table.
        """
        # Make instruments view full screen (remove other main widgets)
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if item and item.widget() and item.widget() is not self.student_table and item.widget() is not None:
                item.widget().setParent(None)
        # Reuse student_table as the single table area
        if not hasattr(self, 'student_table') or self.student_table.parent() is None:
            self.student_table = QTableWidget()
            self.layout.addWidget(self.student_table)

        headers = [
            "ID", "Student ID", "Name", "Serial", "Case", "Model", "Condition", "Status", "Notes"
        ]
        self.student_table.setColumnCount(len(headers))
        self.student_table.setHorizontalHeaderLabels(headers)
        self.student_table.setRowCount(0)

        rows = db.get_all_instruments()
        for r, i in enumerate(rows):
            self.student_table.insertRow(r)
            # i: id, student_id, name, serial, case, model, condition, status, is_checked_in, notes
            for c, val in enumerate([i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[9]]):
                text = "" if val is None else str(val)
                self.student_table.setItem(r, c, QTableWidgetItem(text))

        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.student_table.setVerticalHeaderLabels(["" for _ in range(self.student_table.rowCount())])

    def find_instrument_popup(self):
        dlg = AddInstrumentDialog(self, find_mode=True)
        if not dlg.exec():
            return
        q = dlg.get_instrument_data()
        # Search by serial if present, else by name
        found_rows = []
        if q.get('instrument_serial'):
            # Find all with this serial
            for r in db.get_all_instruments():
                if r[3] == q['instrument_serial']:
                    found_rows.append(r)
        elif q.get('instrument_name'):
            for r in db.get_all_instruments():
                if r[2] and q['instrument_name'].lower() in r[2].lower():
                    found_rows.append(r)

        dlg2 = QDialog(self)
        dlg2.setWindowTitle("Find Instrument Results")
        v = QVBoxLayout()
        if not found_rows:
            v.addWidget(QLabel("No matching instrument found."))
        else:
            table = QTableWidget()
            table.setColumnCount(9)
            table.setHorizontalHeaderLabels(["ID", "Student", "Name", "Serial", "Case", "Model", "Condition", "Status", "Notes"])
            table.setRowCount(len(found_rows))
            for r, row in enumerate(found_rows):
                for c, val in enumerate([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[9]]):
                    table.setItem(r, c, QTableWidgetItem(str(val) if val is not None else ""))
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            v.addWidget(table)

            h = QHBoxLayout()
            edit_btn = QPushButton("Edit Selected")
            close_btn = QPushButton("Close")
            h.addWidget(edit_btn)
            h.addWidget(close_btn)
            v.addLayout(h)

            def on_edit():
                r = table.currentRow()
                if r < 0:
                    QMessageBox.warning(self, "Select", "Select a row to edit.")
                    return
                inst_id = int(table.item(r, 0).text())
                ed = QDialog(self)
                ed.setWindowTitle(f"Edit Instrument {inst_id}")
                ed_v = QVBoxLayout()
                name_in = QLineEdit(table.item(r, 2).text())
                serial_in = QLineEdit(table.item(r, 3).text())
                case_in = QLineEdit(table.item(r, 4).text())
                model_in = QLineEdit(table.item(r, 5).text())
                cond_cb = QComboBox()
                cond_cb.addItems(["Excellent", "Good", "Fair", "Poor"])
                cond_val = table.item(r, 6).text()
                if cond_val:
                    idx = cond_cb.findText(cond_val)
                    if idx >= 0:
                        cond_cb.setCurrentIndex(idx)
                status_cb = QComboBox()
                status_cb.addItems(["Available", "Assigned", "Maintenance", "Retired"])
                stat_val = table.item(r, 7).text()
                if stat_val:
                    idx = status_cb.findText(stat_val)
                    if idx >= 0:
                        status_cb.setCurrentIndex(idx)
                notes_in = QLineEdit(table.item(r, 8).text())
                ed_v.addWidget(QLabel("Name:"))
                ed_v.addWidget(name_in)
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
                        name=name_in.text().strip() or None,
                        case=case_in.text().strip() or None,
                        status=status_cb.currentText(),
                        notes=notes_in.text().strip() or None,
                        model=model_in.text().strip() or None,
                        condition=cond_cb.currentText()
                    )
                    QMessageBox.information(self, "Saved", "Instrument updated.")
                    ed.accept()
                    # Refresh the row in the table
                    table.setItem(r, 2, QTableWidgetItem(name_in.text().strip()))
                    table.setItem(r, 3, QTableWidgetItem(serial_in.text().strip()))
                    table.setItem(r, 4, QTableWidgetItem(case_in.text().strip()))
                    table.setItem(r, 5, QTableWidgetItem(model_in.text().strip()))
                    table.setItem(r, 6, QTableWidgetItem(cond_cb.currentText()))
                    table.setItem(r, 7, QTableWidgetItem(status_cb.currentText()))
                    table.setItem(r, 8, QTableWidgetItem(notes_in.text().strip()))

                be_save.clicked.connect(on_save)
                be_cancel.clicked.connect(ed.reject)
                ed.exec()

            edit_btn.clicked.connect(on_edit)
            close_btn.clicked.connect(dlg2.accept)

        dlg2.setLayout(v)
        dlg2.exec()

    # --------------------------------------------------------------------------
    # Student CRUD methods
    # --------------------------------------------------------------------------

    def open_add_student_popup(self):
        dialog = AddStudentDialog()
        if dialog.exec():
            self.refresh_table()

    def update_student(self):
        sid, ok = QInputDialog.getText(
            self, "Update Student",
            "Enter Student ID (9 digits) or leave blank to search by last name:"
        )
        if not ok:
            return

        sid = sid.strip()
        # If blank, search by last name
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
            vbox.addWidget(QLabel("Select a student to edit:"))
            lw = QListWidget()
            for s in matches:
                lw.addItem(f"{s[2]}, {s[1]} (ID: {s[0]})")
            vbox.addWidget(lw)
            btn = QPushButton("Edit Selected")
            btn.clicked.connect(lambda: self._handle_batch_edit(lw, matches, dlg))
            vbox.addWidget(btn)
            dlg.setLayout(vbox)
            dlg.exec()
            return

        if not sid.isdigit() or len(sid) != 9:
            QMessageBox.warning(self, "Error", "ID must be 9 digits.")
            return

        data = db.get_student_by_id(sid)
        if not data:
            QMessageBox.warning(self, "Error", "Not found.")
            return

        ed = EditStudentDialog(data)
        if ed.exec():
            self.refresh_table()

    def _handle_batch_edit(self, list_widget, students, dialog):
        idx = list_widget.currentRow()
        if idx < 0:
            return
        ed = EditStudentDialog(students[idx])
        ed.exec()
        self.refresh_table()
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
            self.refresh_table()

    def delete_all_students(self):
        ans = QMessageBox.question(
            self, "Delete ALL",
            "This will remove ALL students, uniforms, and instruments. Continue?",
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
        db.delete_all_uniforms()
        db.delete_all_instruments()
        QMessageBox.information(self, "Deleted", "All data cleared.")
        self.refresh_table()

    # --------------------------------------------------------------------------
    # Find / View methods
    # --------------------------------------------------------------------------

    def find_student_popup(self):
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
            vbox.addWidget(QLabel(f"{stu[2]}, {stu[1]} (ID: {stu[0]})"))
            hbox = QHBoxLayout()
            view_btn = QPushButton("View")
            edit_btn = QPushButton("Edit")
            view_btn.clicked.connect(lambda: self._view_single_student(stu, dlg))
            edit_btn.clicked.connect(lambda: self._edit_single_student(stu, dlg))
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
            vbox.addWidget(QLabel("Select a student:"))
            lw = QListWidget()
            for s in students:
                lw.addItem(f"{s[2]}, {s[1]} (ID: {s[0]})")
            vbox.addWidget(lw)
            hbox = QHBoxLayout()
            view_all_btn = QPushButton("View All")
            edit_sel_btn = QPushButton("Edit Selected")
            view_all_btn.clicked.connect(lambda: self._view_section_students(students, section, dlg))
            edit_sel_btn.clicked.connect(lambda: self._edit_section_student(lw, students, dlg))
            hbox.addWidget(view_all_btn)
            hbox.addWidget(edit_sel_btn)
            vbox.addLayout(hbox)
            dlg.setLayout(vbox)
            dlg.exec()

    def _view_single_student(self, stu, dialog):
        headers = [
            "Student ID", "First Name", "Last Name", "Status", "Section",
            "Phone", "Email", "Guardian Name", "Guardian Phone", "Year Came Up",
            "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #",
            "Instrument Name", "Instrument Serial", "Instrument Case"
        ]
        info = "\n".join(
            f"{headers[i]}: {stu[i] if stu[i] is not None else ''}"
            for i in range(len(headers))
        )
        self.show_printable_results("Student Info", info)
        dialog.accept()

    def _edit_single_student(self, stu, dialog):
        ed = EditStudentDialog(stu)
        ed.exec()
        self.refresh_table()
        dialog.accept()

    def _view_section_students(self, students, section, dialog):
        headers = [
            "Student ID", "First Name", "Last Name", "Status", "Section",
            "Phone", "Email", "Guardian Name", "Guardian Phone", "Year Came Up",
            "Shako #", "Hanger #", "Garment Bag", "Coat #", "Pants #",
            "Instrument Name", "Instrument Serial", "Instrument Case"
        ]
        info = ""
        for stu in students:
            block = "\n".join(
                f"{headers[i]}: {stu[i] if stu[i] is not None else ''}"
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
        self.refresh_table()
        dialog.accept()

    # --------------------------------------------------------------------------
    # Uniform methods
    # --------------------------------------------------------------------------

    def add_uniform_popup(self):
        """
        Open dialog to add a new uniform part(s) without assigning to a student.
        Adds to separate tables based on which fields are filled.
        """
        dialog = AddUniformDialog(self)
        if dialog.exec():
            uniform_data = dialog.get_uniform_data()
            conn, cursor = db.connect_db()
            added = []
            # Add shako if filled
            if uniform_data['shako_num']:
                cursor.execute('''INSERT INTO shakos (shako_num, status, notes) VALUES (?, ?, ?)''',
                               (uniform_data['shako_num'], uniform_data['status'], uniform_data['notes']))
                added.append('Shako')
            # Add coat if filled
            if uniform_data['coat_num']:
                cursor.execute('''INSERT INTO coats (coat_num, hanger_num, status, notes) VALUES (?, ?, ?, ?)''',
                               (uniform_data['coat_num'], uniform_data['hanger_num'], uniform_data['status'], uniform_data['notes']))
                added.append('Coat')
            # Add pants if filled
            if uniform_data['pants_num']:
                cursor.execute('''INSERT INTO pants (pants_num, status, notes) VALUES (?, ?, ?)''',
                               (uniform_data['pants_num'], uniform_data['status'], uniform_data['notes']))
                added.append('Pants')
            # Add garment bag if filled
            if uniform_data['garment_bag']:
                cursor.execute('''INSERT INTO garment_bags (bag_num, status, notes) VALUES (?, ?, ?)''',
                               (uniform_data['garment_bag'], uniform_data['status'], uniform_data['notes']))
                added.append('Garment Bag')
            conn.commit()
            conn.close()
            self.show_uniform_table_screen()
            if added:
                QMessageBox.information(self, "Success", f"Added: {', '.join(added)}")
            else:
                QMessageBox.warning(self, "No Data", "No uniform parts were added. Please fill at least one field.")

    def assign_uniform_popup(self):
        # Unified dialog for all fields
        dlg = QDialog(self)
        dlg.setWindowTitle("Assign Uniform")
        v = QVBoxLayout()
        sid_in = QLineEdit()
        sid_in.setPlaceholderText("Student ID (9 digits)")
        shako_in = QLineEdit()
        shako_in.setPlaceholderText("Shako # (blank if not assigning)")
        hanger_in = QLineEdit()
        hanger_in.setPlaceholderText("Hanger # (blank if not assigning)")
        bag_in = QLineEdit()
        bag_in.setPlaceholderText("Garment Bag (blank if not assigning)")
        coat_in = QLineEdit()
        coat_in.setPlaceholderText("Coat # (blank if not assigning)")
        pants_in = QLineEdit()
        pants_in.setPlaceholderText("Pants # (blank if not assigning)")
        v.addWidget(QLabel("Enter Student ID and any uniform parts to assign (leave blank for unassigned):"))
        v.addWidget(sid_in)
        v.addWidget(shako_in)
        v.addWidget(hanger_in)
        v.addWidget(bag_in)
        v.addWidget(coat_in)
        v.addWidget(pants_in)
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
            shako = shako_in.text().strip()
            hanger = hanger_in.text().strip()
            bag = bag_in.text().strip()
            coat = coat_in.text().strip()
            pants = pants_in.text().strip()
            # Convert to int where needed, or None
            shako_num = int(shako) if shako else None
            hanger_num = int(hanger) if hanger else None
            coat_num = int(coat) if coat else None
            pants_num = int(pants) if pants else None
            bag_val = bag if bag else None
            # Validate availability
            missing = []
            not_available = []
            if shako_num is not None:
                if not db.find_shako_by_number(shako_num):
                    missing.append(f"Shako #{shako_num}")
                elif not db.is_shako_available(shako_num):
                    not_available.append(f"Shako #{shako_num}")
            if coat_num is not None:
                if not db.find_coat_by_number(coat_num):
                    missing.append(f"Coat #{coat_num}")
                elif not db.is_coat_available(coat_num):
                    not_available.append(f"Coat #{coat_num}")
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
            # Assign
            db.assign_uniform(sid, shako_num, hanger_num, bag_val, coat_num, pants_num)
            if shako_num is not None:
                db.update_shako(shako_num, student_id=sid, status='Assigned')
            if coat_num is not None:
                db.update_coat(coat_num, student_id=sid, status='Assigned', hanger_num=hanger_num)
            if pants_num is not None:
                db.update_pants(pants_num, student_id=sid, status='Assigned')
            if bag_val:
                db.update_bag(bag_val, student_id=sid, status='Assigned')
            QMessageBox.information(self, "Success", "Uniform assigned.")
            dlg.accept()
            self.show_uniform_table_screen()

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
        # Find all uniforms assigned to this student
        conn, cursor = db.connect_db()
        cursor.execute("SELECT id, shako_num, coat_num, pants_num, garment_bag FROM uniforms WHERE student_id = ? AND is_checked_in = 0", (sid,))
        rows = cursor.fetchall()
        conn.close()
        db.return_uniform(sid)
        for row in rows:
            uniform_id, shako_num, coat_num, pants_num, bag_num = row
            # Clear student_id in uniforms table
            conn2, cursor2 = db.connect_db()
            cursor2.execute("UPDATE uniforms SET student_id = NULL WHERE id = ?", (uniform_id,))
            conn2.commit()
            # Also clear student_id and set status in all component tables
            if shako_num:
                cursor2.execute("UPDATE shakos SET student_id = NULL, status = 'Available' WHERE shako_num = ?", (shako_num,))
            if coat_num:
                cursor2.execute("UPDATE coats SET student_id = NULL, status = 'Available' WHERE coat_num = ?", (coat_num,))
            if pants_num:
                cursor2.execute("UPDATE pants SET student_id = NULL, status = 'Available' WHERE pants_num = ?", (pants_num,))
            if bag_num:
                cursor2.execute("UPDATE garment_bags SET student_id = NULL, status = 'Available' WHERE bag_num = ?", (bag_num,))
            conn2.commit()
            conn2.close()
        QMessageBox.information(self, "Success", "Uniform returned.")
        self.show_uniform_table_screen()

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

    # --------------------------------------------------------------------------
    # Instrument methods
    # --------------------------------------------------------------------------

    def add_instrument_popup(self):
        """
        Open dialog to add a new instrument without assigning to a student.
        """
        dialog = AddInstrumentDialog(self)
        if dialog.exec():
            instrument_data = dialog.get_instrument_data()
            conn, cursor = db.connect_db()
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
            conn.commit()
            conn.close()
            self.view_all_instruments_table()
            QMessageBox.information(self, "Success", "New instrument added successfully!")

    def assign_instrument_popup(self):
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
        serial, ok2 = QInputDialog.getText(self, "Assign Instrument", "Serial #:")
        if not ok2 or not serial.strip():
            return
        serial = serial.strip()
        # Find all instruments with this serial
        matches = []
        for i in db.get_all_instruments():
            # i: id, student_id, name, serial, case, model, condition, status, is_checked_in, notes
            if i[3] == serial:
                matches.append(i)
        if not matches:
            create = QMessageBox.question(self, "Instrument Not Found", f"No instrument with Serial '{serial}' found. Create new?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if create == QMessageBox.StandardButton.Yes:
                self.add_instrument_popup()
            return
        # Filter to available
        available = [i for i in matches if i[7] == 'Available']
        if not available:
            QMessageBox.warning(self, "Not Available", f"No available instrument with Serial '{serial}'.")
            return
        # If more than one, let user pick
        if len(available) > 1:
            dlg = QDialog(self)
            dlg.setWindowTitle("Select Instrument to Assign")
            v = QVBoxLayout()
            table = QTableWidget()
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(["ID", "Name", "Serial", "Case", "Status", "Notes"])
            table.setRowCount(len(available))
            for r, row in enumerate(available):
                table.setItem(r, 0, QTableWidgetItem(str(row[0])))
                table.setItem(r, 1, QTableWidgetItem(str(row[2] or '')))
                table.setItem(r, 2, QTableWidgetItem(str(row[3] or '')))
                table.setItem(r, 3, QTableWidgetItem(str(row[4] or '')))
                table.setItem(r, 4, QTableWidgetItem(str(row[7] or '')))
                table.setItem(r, 5, QTableWidgetItem(str(row[9] or '')))
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            v.addWidget(QLabel(f"Multiple instruments found with Serial '{serial}'. Select one to assign:"))
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
                inst = available[row]
                # Confirm case
                case, ok3 = QInputDialog.getText(self, "Assign Instrument", "Case:", text=str(inst[4] or ''))
                if not ok3 or not case.strip():
                    return
                # Mark as assigned
                conn, cursor = db.connect_db()
                cursor.execute("UPDATE instruments SET status='Assigned', student_id=?, is_checked_in=0 WHERE id=?", (sid, inst[0]))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", f"Instrument ID {inst[0]} assigned.")
                self.view_all_instruments_table()
                dlg.accept()
            assign_btn.clicked.connect(do_assign)
            cancel_btn.clicked.connect(dlg.reject)
            dlg.exec()
        else:
            inst = available[0]
            # Confirm case
            case, ok3 = QInputDialog.getText(self, "Assign Instrument", "Case:", text=str(inst[4] or ''))
            if not ok3 or not case.strip():
                return
            # Mark as assigned
            conn, cursor = db.connect_db()
            cursor.execute("UPDATE instruments SET status='Assigned', student_id=?, is_checked_in=0 WHERE id=?", (sid, inst[0]))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", f"Instrument ID {inst[0]} assigned.")
            self.view_all_instruments_table()

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
    # Debug output removed
        self.view_all_instruments_table()

    def show_outstanding_instruments(self):
        """
        Display all not-returned instruments, optionally filtered by section.
        """
        sec, ok = QInputDialog.getText(self, "Outstanding Instruments",
                                    "Enter section to filter (leave blank for all):")
        if ok and sec.strip():
            rows = db.get_students_with_outstanding_instruments_by_section(sec.strip())
        else:
            rows = db.get_students_with_outstanding_instruments()

        if not rows:
            QMessageBox.information(self, "Info", "All instruments are accounted for.")
            return

        msg = "\n".join(
            f"{r[0]} {r[1]}: {r[2]} (Serial: {r[3]}, Case: {r[4]})"
            for r in rows
        )
        self.show_printable_results("Outstanding Instruments", msg)

    # --------------------------------------------------------------------------
    # Backup & Restore
    # --------------------------------------------------------------------------

    def create_backup(self):
        """
        Save all students, uniforms, and instruments to a text file.
        Each line is prefixed with section name for easy parsing.
        """
        # (fixed version above)

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

        info = f"ID:{student[0]} Name:{student[2]}, {student[1]} Section:{student[4]}"
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
