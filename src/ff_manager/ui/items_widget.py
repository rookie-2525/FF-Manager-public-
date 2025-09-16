# ui/items_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QMessageBox, QAbstractItemView
)
from PySide6.QtSql import QSqlTableModel
from PySide6.QtCore import Qt

class ItemsWidget(QWidget):
    def __init__(self, db,stacked_widget, parent=None):
        super().__init__(parent)

        self.model = QSqlTableModel(self, db)
        self.model.setTable("items")
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model.select()

        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view.setEditTriggers(QAbstractItemView.DoubleClicked)  # ダブルクリックで編集
        self.view.horizontalHeader().setStretchLastSection(True)

        # ボタン
        self.btn_add = QPushButton("追加")
        self.btn_delete = QPushButton("削除")
        self.btn_save = QPushButton("保存")
        self.btn_revert = QPushButton("やり直し")
        self.btn_back = QPushButton("戻る")

        btns = QHBoxLayout()
        btns.addWidget(self.btn_back)
        btns.addStretch()
        btns.addWidget(self.btn_add)
        btns.addWidget(self.btn_delete)
        btns.addStretch()
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_revert)

        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.addLayout(btns)

        # シグナル
        self.btn_add.clicked.connect(self.add_item)
        self.btn_delete.clicked.connect(self.delete_item)
        self.btn_save.clicked.connect(self.save_changes)
        self.btn_revert.clicked.connect(self.revert_changes)
        self.btn_back.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))

    def add_item(self):
        row = self.model.rowCount()
        self.model.insertRow(row)

    def delete_item(self):
        row = self.view.currentIndex().row()
        if row >= 0:
            if QMessageBox.question(self, "確認", "この商品を削除しますか？",
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.model.removeRow(row)

    def save_changes(self):
        if not self.model.submitAll():
            QMessageBox.warning(self, "保存失敗", self.model.lastError().text())
        else:
            self.model.select()

    def revert_changes(self):
        self.model.revertAll()
        self.model.select()
