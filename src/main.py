from PyQt6.QtWidgets import QApplication
from ui import EquipmentManagementUI
import db

if __name__ == "__main__":
    db.create_tables()  # Ensure students table is set up
    db.create_uniform_table()  # Ensure uniforms table is set up
    db.create_instrument_table()  # <-- Add this line
    app = QApplication([])
    window = EquipmentManagementUI()
    window.show()
    app.exec()