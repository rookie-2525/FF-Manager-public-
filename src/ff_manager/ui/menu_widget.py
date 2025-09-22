# ui/items_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QMessageBox, QAbstractItemView
)
from PySide6.QtSql import QSqlTableModel
from PySide6.QtCore import Qt

from ff_manager.ui.items_widget import ItemsWidget
from ff_manager.ui.edit_grid_widget import EditGridWidget


class MenuWidget(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()

        # ボタン
        self.btn_item_info = QPushButton("商品情報")
        self.btn_item_data = QPushButton("データ")

        btns = QVBoxLayout()
        btns.addWidget(self.btn_item_info)
        btns.addWidget(self.btn_item_data)
        btns.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(btns)

        for btn in (self.btn_item_info,self.btn_item_data):
            btn.setFixedSize(400,100)


        # シグナル
        self.btn_item_info.clicked.connect(lambda: stacked_widget.setCurrentIndex(1))
        self.btn_item_data.clicked.connect(lambda: stacked_widget.setCurrentIndex(2))