# ui/items_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QMessageBox, QAbstractItemView, QInputDialog,
    QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox
)
from PySide6.QtSql import QSqlTableModel, QSqlQuery

from ff_manager.db.repositories.items_repo import ItemsRepository

class ItemsWidget(QWidget):
    def __init__(self, db,stacked_widget, parent=None):
        super().__init__(parent)

        self.db=db

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
        self.btn_add.clicked.connect(self.on_add_item)
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

    def on_add_item(self):
        dlg = ItemDialog(self)  # UI側の入力フォーム
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()

            item_name=data["item_name"]

            if not item_name:
                QMessageBox.warning(self, "入力エラー", "商品名は必須です。")
                return
            if ItemsRepository(self.db).get_item_id_by_name(item_name) != None:
                QMessageBox.warning(self, "追加失敗", "同名の商品が既に存在する可能性があります。")
                return

            row = self.model.rowCount()
            self.model.insertRow(row)

            # データを1セルずつ埋める
            self.model.setData(self.model.index(row, self.model.record().indexOf("item_name")), data["item_name"])
            self.model.setData(self.model.index(row, self.model.record().indexOf("price")), data["price"])
            self.model.setData(self.model.index(row, self.model.record().indexOf("freshness")), data["freshness"])
            self.model.setData(self.model.index(row, self.model.record().indexOf("sales_class")), data["sales_class"])
            self.model.setData(self.model.index(row, self.model.record().indexOf("item_type")), data["item_type"])
            self.model.setData(self.model.index(row, self.model.record().indexOf("is_active")), data["is_active"])
            # self.model.select()  # 再読み込み


    # ---------- item ----------

class ItemDialog(QDialog):
    def __init__(self, db):
        super().__init__(db)
        self.setWindowTitle("商品を追加")

        # 入力フィールド
        self.name_edit = QLineEdit()
        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("整数で入力")
        self.freshness_edit = QLineEdit()
        self.sales_class_combo = QComboBox()
        self.sales_class_combo.addItems(["normal", "limited"])
        self.item_type_combo = QComboBox()
        self.item_type_combo.addItems(["ambient", "heated"])
        self.is_active_combo = QComboBox()
        self.is_active_combo.addItems(["1", "0"])  # 1=有効, 0=無効

        # レイアウト
        form = QFormLayout()
        form.addRow("商品名:", self.name_edit)
        form.addRow("価格:", self.price_edit)
        form.addRow("鮮度:", self.freshness_edit),
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form.addRow("販売区分:", self.sales_class_combo)
        form.addRow("商品タイプ:", self.item_type_combo)
        form.addRow("販売中:", self.is_active_combo)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def get_data(self):
        return {
            "item_name": self.name_edit.text().strip(),
            "price": int(self.price_edit.text() or 0),
            "freshness": int(self.freshness_edit.text() or 0),
            "sales_class": self.sales_class_combo.currentText(),
            "item_type": self.item_type_combo.currentText(),
            "is_active": int(self.is_active_combo.currentText()),
        }

    