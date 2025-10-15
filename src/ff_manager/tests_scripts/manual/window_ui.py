from PySide6.QtWidgets import (
    QApplication, QWidget,QMessageBox, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout, QPushButton
)
import sys

from ff_manager.config import DB_PATH
from ff_manager.db.connection import get_db
from ff_manager.ui.ocr_import.ocr_import_widget import OCRImportWidget


def main():
    app = QApplication(sys.argv)
    try:
        db = get_db(DB_PATH)
    except Exception as e:
        QMessageBox.critical(None, "DB Error", str(e))
        sys.exit(1)
    w = OCRImportWidget(db)
    # w=QWidget()
    w.resize(1000, 400)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()