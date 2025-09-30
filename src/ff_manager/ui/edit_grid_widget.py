# ui/edit_grid_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDateEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QMessageBox, QSizePolicy,
    QHeaderView
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtSql import QSqlQuery

from ff_manager.core.constants import (
    HOURS, ITEM_METRICS,ITEM_LABELS_JA, ITEM_ROW, SUMMARY_ROWS,SUMMARY_LABELS_JA, SUMMARY_ROW
    ,TAB_INDEX
    )

from ff_manager.db.repositories.items_repo import ItemsRepository

from ff_manager.services.metrics_service import MetricsService

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ff_manager.config import TEST_MODE

DEFAULT_DATE=(2025,1,1)


class EditGridWidget(QWidget):
    saved = Signal(str)   # 保存完了時に 'YYYY-MM-DD' を通知

    def __init__(self,metrics_service:MetricsService,items_repo:ItemsRepository,stacked_widget, parent=None):
        super().__init__(parent)

        # ==== service ====
        self.items_repo=items_repo
        self.metrics_service = metrics_service

        # ==== header ====
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        if TEST_MODE:
            self.date_edit.setDate(QDate(*DEFAULT_DATE))
        else:
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
        self._init_table()

        # ==== 簡易グラフ ====
        self.figure=Figure(figsize=(4,2))
        self.item_canvas = FigureCanvas(self.figure)
        self.ax = self.item_canvas.figure.subplots()
        self.item_canvas.setVisible(False)  # 初期は非表示

        self.btn_chart = QPushButton("グラフ")
        self.btn_chart.setCheckable(True)  # 折り畳み用にトグル可能にする
        self.btn_chart.toggled.connect(self._toggle_chart)


        # ==== layout ====

        date_form = QHBoxLayout()
        date_form.addWidget(QLabel("日付:"))
        date_form.addWidget(self.btn_prev_month)
        date_form.addWidget(self.btn_prev_day)
        date_form.addWidget(self.date_edit)
        date_form.addWidget(self.btn_next_day)
        date_form.addWidget(self.btn_next_month)
        date_form.addStretch()


        summary_grid=QVBoxLayout()
        summary_grid.addLayout(date_form)
        summary_grid.addWidget(self.summary_table)


        item_form=QHBoxLayout()
        item_form.addWidget(QLabel("商品:"))
        item_form.addWidget(self.item_combo)
        # date_form.addSpacing(12)
        item_form.addStretch()


        item_grid = QVBoxLayout()
        item_grid.addLayout(item_form)
        item_grid.addWidget(self.item_table)
        item_grid.addWidget(self.item_canvas)
        item_grid.addWidget(self.btn_chart)


        foot = QHBoxLayout()
        foot.addWidget(self.btn_back)
        foot.addStretch()
        foot.addWidget(self.btn_save)
        foot.addWidget(self.btn_revert)

        root = QVBoxLayout(self)
        root.addLayout(summary_grid)
        root.addLayout(item_grid)
        root.addStretch()
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
        self.date_edit.dateChanged.connect(self.refresh_view)
        self.item_combo.currentTextChanged.connect(self.refresh_view)

        # self.btn_chart.clicked.connect(lambda: stacked_widget.setCurrentIndex(TAB_INDEX["CHARTS"]))

        self._clear_tables(self.item_table)
        self._clear_tables(self.summary_table)
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
        cur = self._item_name()
        self.item_combo.clear()
        for nm in self.metrics_service.fetch_item_names():
            self.item_combo.addItem(nm)
        if cur:
            i = self.item_combo.findText(cur)
            if i >= 0:
                self.item_combo.setCurrentIndex(i)

    def _init_table(self):
        """
        テーブルの初期化

        """
        self._init_summary_table()
        self._init_item_table()

    def _init_summary_table(self):
        """
        summary_tableの初期化

        Args:
        Returns:

        """
        self.summary_table = QTableWidget(len(SUMMARY_ROWS), len(HOURS)+1)
        self.summary_table.setHorizontalHeaderLabels([str(h) for h in HOURS]+["合計"])
        self.summary_table.setVerticalHeaderLabels([SUMMARY_LABELS_JA[m] for m in SUMMARY_ROWS])

        validator = QIntValidator(0, 1_000_000, self)
        for r in range(self.summary_table.rowCount()):
            for c in range(self.summary_table.columnCount()):
                it = QTableWidgetItem("0")
                it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if r == 0:
                    if c==24:
                        it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    else:
                        it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
                else:
                    it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.summary_table.setItem(r, c, it)
        self.summary_table.itemChanged.connect(lambda item: self._sanitize_int_item(item, validator))

        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)     # 余白を均等に配分
        # self.summary_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _init_item_table(self):
        """
        item_tableの初期化

        Args:
        Returns:

        """
        self.item_table = QTableWidget(len(ITEM_METRICS), len(HOURS)+1)
        self.item_table.setHorizontalHeaderLabels([str(h) for h in HOURS]+["合計"])
        self.item_table.setVerticalHeaderLabels([ITEM_LABELS_JA[m] for m in ITEM_METRICS])

        validator = QIntValidator(0, 1_000_000, self)
        for r in range(self.item_table.rowCount()):
            for c in range(self.item_table.columnCount()):
                it = QTableWidgetItem("0")
                it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
                self.item_table.setItem(r, c, it)
        self.item_table.itemChanged.connect(lambda item: self._sanitize_int_item(item, validator))

        self.item_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)     # 余白を均等に配分
        # self.item_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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

    def _fill_table(self, table, data: dict, row_map: dict):
        """
        dict のデータを QTableWidget に流し込む共通関数

        Args:
            table (QTableWidget): 対象テーブル
            data (dict): {metric: {hour: value}} または {metric: {hour: total}}
            row_map (dict): metric -> row index の対応
        """
        for m, by_hour in data.items():
            if m not in row_map:
                continue
            r = row_map[m]
            for h, v in by_hour.items():
                if 0 <= h <= 23:
                    table.item(r, h).setText(str(v))

        # 合計列
        for r in range(table.rowCount()):
            total = sum(int(table.item(r, c).text()) for c in range(24))
            table.item(r, 24).setText(str(total))

    def _shift_date(self, days: int = 0, months: int = 0):
        """日付を days 日または months ヶ月ずらす"""
        d = self.date_edit.date()
        if days:
            d = d.addDays(days)
        if months:
            d = d.addMonths(months)
        self.date_edit.setDate(d) 

    def _toggle_chart(self, checked: bool):
        self.item_canvas.setVisible(checked)
        if checked:
            self._update_chart()

    def _update_chart(self):
        """テーブルの内容からグラフを描画"""
        self.ax.clear()

        # --- 各アイテム指標 ---
        for r, metric in enumerate(ITEM_METRICS):
            values = [int(self.item_table.item(r, h).text()) for h in HOURS]
            self.ax.plot(HOURS, values, marker="o", label=metric)

        self.ax.set_xlabel("時間")
        self.ax.set_ylabel("数量（仕込/販売/廃棄/陳列）")
        self.ax.set_xticks(HOURS)

        # --- 右Y軸: 客数 ---
        ax2 = self.ax.twinx()  # 右側のY軸を追加
        customer_values = [int(self.summary_table.item(0, h).text()) for h in HOURS]
        ax2.plot(HOURS, customer_values, marker="o", color="black", label="客数")
        ax2.set_ylabel("客数")
        ax2.set_ylim(0, 200)  # 必要なら固定範囲

        # --- 凡例の統合 ---
        lines1, labels1 = self.ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        self.ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

        self.ax.grid(True)
        self.item_canvas.draw()

    # ========== main operations ==========
    def load_current(self):
        d = self._date_iso()
        name = self._item_name()
        if not d or not name:
            self._clear_tables(self.item_table)
            self._clear_tables(self.summary_table)
            return

        item_id = self.metrics_service.get_item_id_by_name(name)
        if item_id is None:
            QMessageBox.information(self, "未登録", "商品を追加してください。")
            return

        # --- Serviceからまとめて取得 ---
        data = self.metrics_service.load(d, item_id)

        # --- 商品テーブル ---
        self._clear_tables(self.item_table)
        self._fill_table(self.item_table, data["item"], ITEM_ROW)

        # --- サマリテーブル ---
        self._clear_tables(self.summary_table)
        customer_data = {"customer": data["customers"]}
        self._fill_table(self.summary_table, customer_data, SUMMARY_ROW)
        self._fill_table(self.summary_table, data["summary"], SUMMARY_ROW)

        # 合計値更新
        self.update_summary_table(d)

    def save_current(self):
        d = self._date_iso()
        name = self._item_name()
        item_id = self.metrics_service.get_item_id_by_name(name)
        if item_id is None:
            QMessageBox.warning(self, "未登録", "商品を追加してください。")
            return

        try:
            self.metrics_service.save(d, item_id, self.item_table, self.summary_table)
            self.saved.emit(d)
            QMessageBox.information(self, "保存完了", f"{d} のデータを保存しました。")
            self.load_current()
        except Exception as e:
            QMessageBox.warning(self, "保存失敗", str(e))

    def update_summary_table(self, date_str: str):
        data = self.metrics_service.fetch_summary(date_str)
        self._fill_table(self.summary_table, data["summary"], SUMMARY_ROW)

    def refresh_view(self):
        """テーブルとグラフをまとめて更新する共通関数"""
        d = self._date_iso()
        name = self._item_name()
        if not d or not name:
            self._clear_tables(self.item_table)
            self._clear_tables(self.summary_table)
            self._update_chart()
            return

        item_id = self.metrics_service.get_item_id_by_name(name)
        if item_id is None:
            QMessageBox.information(self, "未登録", "商品を追加してください。")
            return

        # --- データ取得 ---
        data = self.metrics_service.load(d, item_id)

        # --- item table 更新 ---
        self._clear_tables(self.item_table)
        self._fill_table(self.item_table, data["item"], ITEM_ROW)

        # --- summary table 更新 ---
        self._clear_tables(self.summary_table)
        customer_data = {"customer": data["customers"]}
        self._fill_table(self.summary_table, customer_data, SUMMARY_ROW)
        self._fill_table(self.summary_table, data["summary"], SUMMARY_ROW)

        # --- グラフ更新 ---
        self._update_chart()
