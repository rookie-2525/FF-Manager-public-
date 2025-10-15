# ui/main_window.py
import sys
from PySide6.QtWidgets import (
    QMainWindow, QStackedWidget, QMessageBox
)
from ff_manager.config import (WINDOW_TITLE,WINDOW_SIZE,TABLE)

from ff_manager.db.migrations import ensure_schema_and_migrate
from ff_manager.db.aggregate import rebuild_daily_for_date
from ff_manager.db.repositories.items_repo import ItemsRepository

from ff_manager.services.chart_service import ChartService
from ff_manager.services.metrics_service import MetricsService

from ff_manager.ui.edit_grid.edit_grid_widget import EditGridWidget
from ff_manager.ui.items.items_widget import ItemsWidget
from ff_manager.ui.menu.menu_widget import MenuWidget
from ff_manager.ui.chart_widget.charts_widget import ChartsWidget
from ff_manager.ui.ocr_import.ocr_import_widget import OCRImportWidget

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db

        # --- ウィンドウ ---
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(*WINDOW_SIZE)

        # --- DBの構築 ---
        try:
            ensure_schema_and_migrate(self.db, TABLE)
        except Exception as e:
            QMessageBox.critical(self, "Migration Error", str(e))
            sys.exit(1)

        self.items_repo=ItemsRepository(db)

        # --- service ---
        self.metrics_service=MetricsService(db)
        self.chart_service = ChartService(db)

        self.stack = QStackedWidget()

        self.stack.addWidget(MenuWidget(self.stack))    # menu

        self.stack.addWidget(ItemsWidget(self.db,self.stack))   # items
        
        self.stack.addWidget(EditGridWidget(
             self.metrics_service,
             self.chart_service,
             self.items_repo,
             self.stack))    # edit
        
        self.stack.addWidget(ChartsWidget(self.chart_service,self.stack))   # chart
        
        self.stack.addWidget(OCRImportWidget(db,self.stack))   # ocr


        self.setCentralWidget(self.stack)


   
    def _on_saved(self, date_iso: str):
        
            if not rebuild_daily_for_date(self.db, date_iso):
                # 失敗しても編集結果は保存済み。通知のみ。
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "サマリ更新", f"{date_iso} の日次サマリ更新に失敗しました。")


