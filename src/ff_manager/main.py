# main.py
import sys
from PySide6.QtWidgets import QApplication, QMessageBox

from ff_manager.config import DB_PATH
from ff_manager.db.connection import get_db
from ff_manager.ui.main_window import MainWindow

from ff_manager.ui.styles.theme import load_qss

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(load_qss())  
    try:
        db = get_db(DB_PATH)
    except Exception as e:
        QMessageBox.critical(None, "DB Error", str(e))
        sys.exit(1)

    w = MainWindow(db)
    w.show()
    sys.exit(app.exec())



if __name__ == "__main__":
    main()
