# Import the QApplication class to initialize the Qt GUI system
from PyQt6.QtWidgets import QApplication

# Import the main UI class that defines the equipment management interface
from ui import EquipmentManagementUI

# Import the database module to set up and interact with tables
import db

# This block runs only when the script is executed directly (not imported)
if __name__ == "__main__":

    # --- Database Setup ---
    # These functions ensure that all required tables exist before launching the app.
    db.create_student_table()           # Creates the 'students' table if missing
    db.create_uniform_table()           # Creates the 'uniforms' table if missing
    db.create_instrument_table()        # Creates the 'instruments' table if missing
    db.initialize_uniform_components()  # Creates any additional uniform-related tables (e.g., shako, coat, pants)

    # --- Launch the GUI ---
    app = QApplication([])              # Initialize the Qt application (empty argument list)
    window = EquipmentManagementUI()    # Create the main window instance
    window.show()                       # Display the window on screen
    app.exec()                          # Start the Qt event loop (waits for user interaction)