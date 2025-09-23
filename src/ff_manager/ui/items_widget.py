# ui/items_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QMessageBox, QAbstractItemView, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox,
    QCheckBox,QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtSql import QSqlTableModel, QSqlQuery

from ff_manager.db.repositories.items_repo import ItemsRepository

class ItemsWidget(QWidget):
    def __init__(self, db,stacked_widget, parent=None):
        super().__init__(parent)

        # ==== database ====
        self.db=db

        # === search functionality ===
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("商品名で検索...")
        self.search_edit.textChanged.connect(self.search_items)

        search_layout = QHBoxLayout()
        search_layout.addStretch()
        search_layout.addWidget(QLabel("検索:"))
        search_layout.addWidget(self.search_edit)


        # === tables ===
        self.model = QSqlTableModel(self, db)
        self.model.setTable("items")
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model.select()

        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view.setEditTriggers(QAbstractItemView.DoubleClicked)  # ダブルクリックで編集/
        self.view.setSortingEnabled(True)   #ソート機能/
        self.view.sortByColumn(self.model.fieldIndex("item_id"), Qt.AscendingOrder) # 初期表示は item_id 昇順/
        header=self.view.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(self.model.record().indexOf("item_name"), QHeaderView.Stretch)  # 広めに設定/
        


        # === buttons ===
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

        # ==== layout ====
        layout = QVBoxLayout(self)
        layout.addLayout(search_layout)
        layout.addWidget(self.view)
        layout.addLayout(btns)

        # ==== signal ====
        self.btn_add.clicked.connect(self.on_add_item)
        self.btn_delete.clicked.connect(self.delete_item)
        self.btn_save.clicked.connect(self.save_changes)
        self.btn_revert.clicked.connect(self.revert_changes)
        self.btn_back.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))


    # ------------------------------
    # function
    # ------------------------------
    def search_items(self, text: str):
        if text.strip():
            # 部分一致検索（SQLiteのLIKEは大文字小文字を区別しない）
            self.model.setFilter(f"item_name LIKE '%{text}%'")
        else:
            # 空なら全件表示
            self.model.setFilter("")
        self.model.select()


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




# ------------------------------
# Dialog
# ------------------------------

class ItemDialog(QDialog):
    def __init__(self, db):
        super().__init__(db)
        self.setWindowTitle("商品を追加")

        # # 入力フィールド
        self.name_edit = QLineEdit()
        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("整数で入力")

        self.freshness_combo = QComboBox()
        self.freshness_combo.addItem("4時間","4")
        self.freshness_combo.addItem("6時間","6")
        self.freshness_combo.addItem("7時間","7")

        self.sales_class_combo = QComboBox()
        self.sales_class_combo.addItem("通常", "normal")
        self.sales_class_combo.addItem("限定", "limited")

        self.item_type_combo = QComboBox()
        self.item_type_combo.addItem("常温", "ambient")
        self.item_type_combo.addItem("加温", "heated")
        self.item_type_combo.addItem("中華まん", "chukaman")
        self.item_type_combo.addItem("おでん", "oden")

        self.is_active_check = QCheckBox("販売中")
        self.is_active_check.setChecked(False) 

        # レイアウト
        form = QFormLayout()
        form.addRow("商品名:", self.name_edit)
        form.addRow("価格(税抜):", self.price_edit)
        form.addRow("鮮度:", self.freshness_combo),
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form.addRow("販売区分:", self.sales_class_combo)
        form.addRow("商品タイプ:", self.item_type_combo)
        form.addRow("", self.is_active_check)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def get_data(self):
        return {
            "item_name": self.name_edit.text().strip(),
            "price": int(self.price_edit.text() or 0),
            "freshness": int(self.freshness_combo.currentData() or 0),
            "sales_class": self.sales_class_combo.currentData(),
            "item_type": self.item_type_combo.currentData(),
            "is_active": 1 if self.is_active_check.isChecked() else 0
        }

