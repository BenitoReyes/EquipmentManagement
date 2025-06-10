from PyQt6.QtWidgets import QApplication
from ui import EquipmentManagementUI
import db

if __name__ == "__main__":
    db.create_tables()  # Ensure database is set up

    app = QApplication([])
    window = EquipmentManagementUI()
    window.show()
    app.exec()