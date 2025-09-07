# main.py
import sys
from PySide6.QtWidgets import QApplication, QMessageBox

from config import DB_PATH
from db.connection import get_db
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        db = get_db(DB_PATH)
    except Exception as e:
        QMessageBox.critical(None, "DB Error", str(e))
        sys.exit(1)

    w = MainWindow(db)
    w.show()
    sys.exit(app.exec())
