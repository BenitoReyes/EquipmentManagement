from PyQt6.QtWidgets import QApplication
from ui import EquipmentManagementUI
import db

if __name__ == "__main__":
    db.create_tables()  # Ensure database is set up
    db.create_uniform_table()  # Create uniform table if it doesn't exist
    app = QApplication([])
    window = EquipmentManagementUI()
    window.show()
    app.exec()