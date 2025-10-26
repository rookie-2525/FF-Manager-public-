from PySide6.QtWidgets import (
    QApplication, QWidget,QMessageBox, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout, QPushButton,
    QStackedWidget
)
import sys

from ff_manager.config import DB_PATH
from ff_manager.db.connection import get_db
from ff_manager.ui.ocr_import.ocr_import_widget import OCRImportWidget

from ff_manager.services.metrics_service import MetricsService

from ff_manager.config import (WINDOW_SIZE)

def main():
    app = QApplication(sys.argv)
    try:
        db = get_db(DB_PATH)
    except Exception as e:
        QMessageBox.critical(None, "DB Error", str(e))
        sys.exit(1)

    metrics_service=MetricsService(db)

    stack=QStackedWidget()
    stack.addWidget(OCRImportWidget(metrics_service,stack))
    # w = OCRImportWidget(db)
    stack.resize(WINDOW_SIZE[0], WINDOW_SIZE[1])
    stack.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()