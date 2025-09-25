# ui/edit_grid_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDateEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QMessageBox, QSizePolicy,
    QHeaderView, QAbstractScrollArea, QInputDialog,
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtSql import QSqlQuery

from ff_manager.db.repositories.items_repo import ItemsRepository


METRICS = ["customer","prepared", "sold", "discarded", "stock"]
HOURS = list(range(24))

class EditGridWidget(QWidget):
    saved = Signal(str)   # 保存完了時に 'YYYY-MM-DD' を通知

    def __init__(self, db,stacked_widget, parent=None):
        super().__init__(parent)

        # ==== database ====
        self.db = db

        # ==== header ====
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        self.item_combo = QComboBox()
        self.item_combo.setEditable(False)
        self._reload_items()

        self.btn_prev_day=QPushButton("<")
        self.btn_next_day=QPushButton(">")
        self.btn_prev_month=QPushButton("<<")
        self.btn_next_month=QPushButton(">>")
        self.btn_save = QPushButton("保存")
        self.btn_revert = QPushButton("やり直し")
        self.btn_back = QPushButton("戻る")


        for btn in (self.btn_prev_month, self.btn_prev_day, self.btn_next_day, self.btn_next_month):
            btn.setFixedSize(28, 24)


        # ==== grid ====

        # --- item table ---
        self.item_table = QTableWidget(len(METRICS), len(HOURS))
        self.item_table.setHorizontalHeaderLabels([str(h) for h in HOURS])
        self.item_table.setVerticalHeaderLabels(["客数","仕込", "販売", "廃棄", "陳列"])
        self._init_table(self.item_table,True)

        self.item_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # --- sum table ---
        self.sum_table = QTableWidget(4, len(HOURS))
        self.sum_table.setHorizontalHeaderLabels([str(h) for h in HOURS])
        self.sum_table.setVerticalHeaderLabels(["仕込", "販売", "廃棄", "陳列"])
        self._init_table(self.sum_table,False)

        self.sum_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        # ==== layout ====

        head = QHBoxLayout()
        head.addWidget(QLabel("日付:"))
        head.addWidget(self.btn_prev_month)
        head.addWidget(self.btn_prev_day)
        head.addWidget(self.date_edit)
        head.addWidget(self.btn_next_day)
        head.addWidget(self.btn_next_month)
        head.addSpacing(12)
        head.addWidget(QLabel("商品:"))
        head.addWidget(self.item_combo)
        head.addStretch()

        grids = QVBoxLayout()
        grids.addWidget(self.item_table)
        grids.addWidget(self.sum_table)

        foot = QHBoxLayout()
        foot.addWidget(self.btn_back)
        foot.addStretch()
        foot.addWidget(self.btn_save)
        foot.addWidget(self.btn_revert)

        root = QVBoxLayout(self)
        root.addLayout(head)
        root.addLayout(grids)
        root.addLayout(foot)


        #=== signal ===

        self.btn_save.clicked.connect(self.save_current)
        self.btn_revert.clicked.connect(self.load_current)
        self.btn_back.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))

        # 日単位移動
        self.btn_prev_day.clicked.connect(lambda: self._shift_date(days=-1))
        self.btn_next_day.clicked.connect(lambda: self._shift_date(days=1))

        # 月単位移動
        self.btn_prev_month.clicked.connect(lambda: self._shift_date(months=-1))
        self.btn_next_month.clicked.connect(lambda: self._shift_date(months=1))

        # 日付や商品が変わったら自動読み込み
        self.date_edit.dateChanged.connect(self.load_current)
        self.item_combo.currentTextChanged.connect(self.load_current)


        self._clear_tables(self.item_table)
        self._clear_tables(self.sum_table)
        self.load_current()



    # ========== public API（親から呼べる） ==========
    def setDate(self, qdate: QDate):
        self.date_edit.setDate(qdate)

    def setItemName(self, name: str):
        if name and self.item_combo.findText(name) == -1:
            self.item_combo.addItem(name)
        self.item_combo.setCurrentText(name)

    def reloadItems(self):
        self._reload_items()

    # ========== internal ==========
    def _date_iso(self) -> str:
        return self.date_edit.date().toString("yyyy-MM-dd")

    def _item_name(self) -> str:
        return (self.item_combo.currentText() or "").strip()


    def _reload_items(self):
        """
        Args:
            url (str): 取得対象のURL。
            timeout (int, optional): タイムアウト秒数（デフォルトは30秒）。

        Returns:
            dict: パース済みのJSONレスポンス。
        """
        cur = self._item_name()
        self.item_combo.clear()
        for nm in ItemsRepository.list_item_names(self.db):
            self.item_combo.addItem(nm)
        if cur:
            # 現在の選択を維持
            i = self.item_combo.findText(cur)
            if i >= 0:
                self.item_combo.setCurrentIndex(i)

    def _init_table(self, table: QTableWidget,is_edit:bool):
        """
        テーブルの初期化

        Args:
            table (QTableWidget): 取得対象のQTableWidget
            is_edit(bool): 編集許可の有無
        Returns:

        """
        validator = QIntValidator(0, 1_000_000, self)
        for r in range(table.rowCount()):
            for c in range(table.columnCount()):
                it = QTableWidgetItem("0")
                it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if is_edit:
                    it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
                else:
                    it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                table.setItem(r, c, it)
        table.itemChanged.connect(lambda item: self._sanitize_int_item(item, validator))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)     # 余白を均等に配分


    def _sanitize_int_item(self, item: QTableWidgetItem, validator: QIntValidator):
        text = (item.text() or "").strip()
        if text == "":
            item.setText("0"); return
        pos = 0
        if validator.validate(text, pos)[0] != QIntValidator.Acceptable:
            try: int(text)
            except Exception: item.setText("0")

    def _clear_tables(self,table:QTableWidget):
        for r in range(table.rowCount()):
            for c in range(table.columnCount()):
                table.item(r, c).setText("0")


    # ---------- load ----------
    def load_current(self):
        d = self._date_iso()
        name = self._item_name()
        if not d or not name:
            self._clear_tables(self.item_table)
            self._clear_tables(self.sum_table)
            return

        item_id = ItemsRepository(self.db).get_item_id_by_name(name)
        if item_id < 0:
            QMessageBox.information(self, "未登録", "商品を追加してください。")
            return

        self._clear_tables(self.item_table)
        self._clear_tables(self.sum_table)

        # ---- 商品メトリクス（行1..4） ----
        q = QSqlQuery(self.db)
        q.prepare("""
            SELECT metric, hour, value
            FROM fact_hourly_long
            WHERE date=:d AND item_id=:it
            ORDER BY hour
        """)
        q.bindValue(":d", d)
        q.bindValue(":it", item_id)
        q.exec()

        row_of = {"prepared": 1, "sold": 2, "discarded": 3, "stock": 4}

        while q.next():
            m = q.value(0)
            h = int(q.value(1))
            v = int(q.value(2))
            if m in row_of and 0 <= h <= 23:
                self.item_table.item(row_of[m], h).setText(str(v))

        # ---- 客数（行0） ----
        qc = QSqlQuery(self.db)
        qc.prepare("""
            SELECT hour, customer_count
            FROM fact_hourly_customer
            WHERE date=:d
            ORDER BY hour
        """)
        qc.bindValue(":d", d)
        qc.exec()

        while qc.next():
            h = int(qc.value(0))
            v = int(qc.value(1))
            if 0 <= h <= 23:
                # ★ 統合テーブルなので self.item_table の row=0 に入れる
                self.item_table.item(0, h).setText(str(v))

        self.load_summary(d)

    # ---------- save (UPSERT only; サマリは親で) ----------
    def save_current(self):
        d = self._date_iso()
        name = self._item_name()
        # if not d or not name:
        #     QMessageBox.information(self, "入力不足", "日付と商品名を入力してください。"); return

        item_id = ItemsRepository(self.db).get_item_id_by_name(name)
        if item_id < 0:
            QMessageBox.warning(self, "未登録", "商品を追加してください。"); return

        self.db.transaction()
        try:
            # 1) 商品メトリクス（行1..4）
            q = QSqlQuery(self.db)
            q.prepare("""
                INSERT INTO fact_hourly_long(date,hour,item_id,metric,value)
                VALUES(:d,:h,:it,:m,:v)
                ON CONFLICT(date, hour, item_id, metric) DO UPDATE SET value= excluded.value
            """)
            metric_of_row = {1:"prepared", 2:"sold", 3:"discarded", 4:"stock"}
            for r in (1,2,3,4):
                mname = metric_of_row[r]
                for h in HOURS:
                    v = int(self.item_table.item(r, h).text() or 0)
                    q.bindValue(":d", d); q.bindValue(":h", h)
                    q.bindValue(":it", item_id); q.bindValue(":m", mname)
                    q.bindValue(":v", v)
                    if not q.exec(): raise RuntimeError(q.lastError().text())

            # 2) 客数（行0）
            qc = QSqlQuery(self.db)
            qc.prepare("""
                INSERT INTO fact_hourly_customer(date,hour,customer_count)
                VALUES(:d,:h,:c)
                ON CONFLICT(date,hour) DO UPDATE SET customer_count=excluded.customer_count
            """)
            for h in HOURS:
                c = int(self.item_table.item(0, h).text() or 0)
                qc.bindValue(":d", d); qc.bindValue(":h", h); qc.bindValue(":c", c)
                if not qc.exec(): raise RuntimeError(qc.lastError().text())

            # 3) 日次客数サマリを更新
            qd = QSqlQuery(self.db)
            qd.prepare("""
                INSERT INTO fact_daily_customer(date, customer_count)
                VALUES(:d, (
                    SELECT SUM(customer_count) FROM fact_hourly_customer WHERE date=:d
                ))
                ON CONFLICT(date) DO UPDATE SET customer_count=excluded.customer_count
            """)
            qd.bindValue(":d", d)
            if not qd.exec():
                raise RuntimeError(qd.lastError().text())

            self.db.commit()
            self.saved.emit(d)
            QMessageBox.information(self, "保存完了", f"{d} のデータを保存しました。")

            self.load_summary(d)


        except Exception as e:
            self.db.rollback()
            QMessageBox.warning(self, "保存失敗", str(e))


    # ---------- day ----------
    def _shift_date(self, days: int = 0, months: int = 0):
        """日付を days 日または months ヶ月ずらす"""
        d = self.date_edit.date()
        if days:
            d = d.addDays(days)
        if months:
            d = d.addMonths(months)
        self.date_edit.setDate(d)  


    def load_summary(self, date_str: str):
        """全商品の合計をロード"""
        q = QSqlQuery(self.db)
        q.prepare("""
            SELECT metric, hour, SUM(value) as total_value
            FROM fact_hourly_long
            WHERE date=:d
            GROUP BY metric, hour
        """)
        q.bindValue(":d", date_str)
        q.exec()

        row_of = {"prepared": 0, "sold": 1, "discarded": 2, "stock": 3}
        while q.next():
            m, h, v = q.value(0), int(q.value(1)), int(q.value(2))
            if m in row_of and 0 <= h <= 23:
                self.sum_table.setItem(row_of[m], h, QTableWidgetItem(str(v)))

