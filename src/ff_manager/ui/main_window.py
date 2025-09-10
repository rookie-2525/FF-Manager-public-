# ui/main_window.py
import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QTableView, QMessageBox, QAbstractItemView, QSplitter, QHeaderView,
    QDialog,
)
from PySide6.QtSql import QSqlTableModel
from PySide6.QtCore import Qt, QModelIndex, QTimer

from ff_manager.config import (WINDOW_TITLE,WINDOW_SIZE,TABLE,HEADER_JP)
from ff_manager.db.migrations import ensure_schema_and_migrate

from ff_manager.ui.panels import build_buttons_column,ButtonType
from ff_manager.ui.styles import apply_table_style
from ff_manager.ui.edit_grid_widget import EditGridWidget

from ff_manager.db.aggregate import rebuild_daily_for_date, normalize_date

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db

        # --- ウィンドウ ---
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(*WINDOW_SIZE)

        # --- DBの構築（マイグレーション） ---
        try:
            ensure_schema_and_migrate(self.db, TABLE)
        except Exception as e:
            QMessageBox.critical(self, "Migration Error", str(e))
            sys.exit(1)

        self.grid = EditGridWidget(self.db)
        self.setCentralWidget(self.grid)

        # 「保存完了」を受けて日次サマリ再計算（アプリ側の責務）
        self.grid.saved.connect(self._on_saved)


   
    def _on_saved(self, date_iso: str):
            if not rebuild_daily_for_date(self.db, date_iso):
                # 失敗しても編集結果は保存済み。通知のみ。
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "サマリ更新", f"{date_iso} の日次サマリ更新に失敗しました。")


     
    # def open_edit_grid(self):
    #     dlg = EditGridDialog(self.db, self)
    #     if dlg.exec() == QDialog.Accepted:
    #         # ダイアログで保存が完了 → 指定日のサマリを再計算（商品＆客数）
    #         date_iso = dlg._date_iso()  # ダイアログの選択日
    #         if date_iso:
    #             if not rebuild_daily_for_date(self.db, date_iso):
    #                 QMessageBox.warning(self, "サマリ更新", f"{date_iso} の日次サマリ更新に失敗しました。")
    #         # メインのモデルを再読込（表示を更新したい場合）
    #         if hasattr(self, "model"):
    #             self.model.select()
    
