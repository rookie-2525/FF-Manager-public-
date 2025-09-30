# ui/main_window.py
import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QStackedWidget,
    QPushButton, QTableView, QMessageBox, QAbstractItemView, QSplitter, QHeaderView,
    QDialog,
)
from PySide6.QtSql import QSqlTableModel
from PySide6.QtCore import Qt, QModelIndex, QTimer

from ff_manager.config import (TEST_MODE,WINDOW_TITLE,WINDOW_SIZE,TABLE,HEADER_JP)
from ff_manager.core.constants import TAB_INDEX

from ff_manager.db.migrations import ensure_schema_and_migrate
from ff_manager.db.aggregate import rebuild_daily_for_date, normalize_date
from ff_manager.db.repositories.items_repo import ItemsRepository

from ff_manager.services.chart_service import ChartService
from ff_manager.services.metrics_service import MetricsService

from ff_manager.ui.panels import build_buttons_column,ButtonType
from ff_manager.ui.styles import apply_table_style
from ff_manager.ui.edit_grid_widget import EditGridWidget
from ff_manager.ui.items_widget import ItemsWidget
from ff_manager.ui.menu_widget import MenuWidget
from ff_manager.ui.charts_widget import ChartsWidget

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
        self.chart_service = ChartService(db)
        self.metrics_service=MetricsService(db)

        self.stack = QStackedWidget()
        self.stack.addWidget(MenuWidget(self.stack))                # menu
        self.stack.addWidget(ItemsWidget(self.db,self.stack))       # items
        self.stack.addWidget(EditGridWidget(self.metrics_service,self.items_repo,self.stack))    # edit
        self.stack.addWidget(ChartsWidget(self.chart_service,self.stack))   # chart
        self.setCentralWidget(self.stack)

        # self.grid = EditGridWidget(self.db,self.stack)
        self.setCentralWidget(self.stack)

   
    def _on_saved(self, date_iso: str):
        
            if not rebuild_daily_for_date(self.db, date_iso):
                # 失敗しても編集結果は保存済み。通知のみ。
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "サマリ更新", f"{date_iso} の日次サマリ更新に失敗しました。")


