# ui/edit_grid_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDateEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QMessageBox, QSizePolicy,QStackedWidget,
    QHeaderView
)
from PySide6.QtCore import Qt, QDate, Signal,QTimer
from PySide6.QtGui import QIntValidator
from PySide6.QtSql import QSqlQuery

from ff_manager.core.constants import (
    HOURS, ITEM_METRICS,ITEM_LABELS_JA, ITEM_ROW, SUMMARY_ROWS,SUMMARY_LABELS_JA, SUMMARY_ROW
    ,TAB_INDEX
    )

from ff_manager.db.repositories.items_repo import ItemsRepository

from ff_manager.services.metrics_service import MetricsService
from ff_manager.services.chart_service import ChartService

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ff_manager.config import TEST_MODE

from ff_manager.ui.edit_grid.tables import (
    init_summary_table,
    init_item_table,
    clear_table,
    fill_table,
)

from ff_manager.ui.edit_grid.chart_area import ChartArea
from ff_manager.ui.effects.gradient_bg import GradientBackground
from ff_manager.ui.ocr_import import ocr_import_widget

DEFAULT_DATE=(2025,1,1)


class EditGridWidget(QWidget):
    saved = Signal(str)   # 保存完了時に 'YYYY-MM-DD' を通知

    def __init__(
            self,
            metrics_service:MetricsService,
            chart_service:ChartService,
            items_repo:ItemsRepository,
            stacked_widget:QStackedWidget,
            parent=None
            ):
        super().__init__(parent)

        # ==== service ====
        self.items_repo=items_repo
        self.metrics_service = metrics_service
        self.chart_service=chart_service

        # ==== table ====
        self.summary_table = init_summary_table(SUMMARY_ROWS, SUMMARY_LABELS_JA)
        self.item_table = init_item_table(ITEM_METRICS, ITEM_LABELS_JA)

        # ==== ui ====
        self.chart_area = ChartArea(self)
        self._init_header()
        self._init_footer()
        self._init_layout(stacked_widget)

        
        self.load_item_and_summary()

        # signal
        self._connect_signals(stacked_widget)

    # ========== public API ==========

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

    def _shift_date(self, days: int = 0, months: int = 0):
        """日付を days 日または months ヶ月ずらす"""
        d = self.date_edit.date()
        if days:
            d = d.addDays(days)
        if months:
            d = d.addMonths(months)
        self.date_edit.setDate(d) 

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

    def _sanitize_int_item(self, item: QTableWidgetItem, validator: QIntValidator):
            text = (item.text() or "").strip()
            if text == "":
                item.setText("0"); return
            pos = 0
            if validator.validate(text, pos)[0] != QIntValidator.Acceptable:
                try: int(text)
                except Exception: item.setText("0")

    def _shift_item(self,idx:int=0):

        current_index = self.item_combo.currentIndex()

        # 範囲チェック
        if current_index+idx >= 0 and current_index+idx < self.item_combo.count():
            self.item_combo.setCurrentIndex(current_index + idx)


    def _init_header(self):
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        if TEST_MODE:
            self.date_edit.setDate(QDate(*DEFAULT_DATE))
        else:
            self.date_edit.setDate(QDate.currentDate())

        self.btn_prev_day=QPushButton("<")
        self.btn_next_day=QPushButton(">")
        self.btn_prev_month=QPushButton("<<")
        self.btn_next_month=QPushButton(">>")

        self.item_combo = QComboBox()
        self.item_combo.setEditable(False)
        self._reload_items()
        self.btn_prev_item=QPushButton("<")
        self.btn_next_item=QPushButton(">")

        self.btn_read_img=QPushButton("画像から読み取り")


        for btn in (
            self.btn_prev_month, 
            self.btn_prev_day, 
            self.btn_next_day, 
            self.btn_next_month,
            self.btn_prev_item,
            self.btn_next_item):
            btn.setFixedSize(28, 24)

        # グラフボタン
        self.btn_chart = QPushButton("グラフ")
        self.btn_chart.setCheckable(True)
        self.btn_chart.toggled.connect(self._toggle_chart)


    def _init_footer(self):
        self.btn_save = QPushButton("保存")
        self.btn_revert = QPushButton("やり直し")
        self.btn_back = QPushButton("戻る")

        for btn in (self.btn_save,self.btn_revert,self.btn_back):
            btn.setFixedSize(58,32)



    def _toggle_chart(self, checked: bool):
        self.chart_area.widget().setVisible(checked)
        if checked:
            self._refresh_chart()

    def _refresh_chart(self):
        d = self._date_iso()
        item_name = self._item_name()
        item_id = self.metrics_service.get_item_id_by_name(item_name)
        if item_id is None:
            return

        data = self.chart_service.get_item_vs_customer(d, item_id)
        self.chart_area.refresh(data)
 

    # ---------------- layout ----------------
    def _init_layout(self,stack:QStackedWidget):

        date_form = QHBoxLayout()
        date_form.addWidget(QLabel("日付:"))
        date_form.addWidget(self.btn_prev_month)
        date_form.addWidget(self.btn_prev_day)
        date_form.addWidget(self.date_edit)
        date_form.addWidget(self.btn_next_day)
        date_form.addWidget(self.btn_next_month)
        date_form.addStretch()
        date_form.addWidget(self.btn_read_img)

        summary_grid=QVBoxLayout()
        summary_grid.addLayout(date_form)
        summary_grid.addWidget(self.summary_table)

        item_form=QHBoxLayout()
        item_form.addWidget(QLabel("商品:"))
        item_form.addWidget(self.btn_prev_item)
        item_form.addWidget(self.item_combo)
        item_form.addWidget(self.btn_next_item)
        item_form.addStretch()

        item_grid = QVBoxLayout()
        item_grid.addLayout(item_form)
        item_grid.addWidget(self.item_table)
        item_grid.addWidget(self.btn_chart)
        item_grid.addWidget(self.chart_area.widget())

        foot = QHBoxLayout()
        foot.addWidget(self.btn_back)
        foot.addStretch()
        foot.addWidget(self.btn_save)
        foot.addWidget(self.btn_revert)


        root=QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0)

        bg=GradientBackground(self)
        root.addWidget(bg)

        panel = QVBoxLayout(bg.content)
        panel.setContentsMargins(20,20,20,20)
        panel.addLayout(summary_grid)
        panel.addLayout(item_grid)
        panel.addStretch()
        panel.addLayout(foot)


    # ---------------- signal ----------------
    def _connect_signals(self,stack:QStackedWidget):
        self.btn_save.clicked.connect(self.save_item_and_summary)
        self.btn_revert.clicked.connect(self.load_item_and_summary)
        self.btn_back.clicked.connect(lambda: stack.setCurrentIndex(0))

        # 日単位移動
        self.btn_prev_day.clicked.connect(lambda: self._shift_date(days=-1))
        self.btn_next_day.clicked.connect(lambda: self._shift_date(days=1))

        # 月単位移動
        self.btn_prev_month.clicked.connect(lambda: self._shift_date(months=-1))
        self.btn_next_month.clicked.connect(lambda: self._shift_date(months=1))

        # 日付や商品が変わったら自動読み込み
        self.date_edit.dateChanged.connect(self.reload_all)
        self.item_combo.currentTextChanged.connect(self.reload_all)

        # 商品移動
        self.btn_prev_item.clicked.connect(lambda: self._shift_item(idx=-1))
        self.btn_next_item.clicked.connect(lambda: self._shift_item(idx=1))


        self.btn_read_img.clicked.connect(lambda: stack.setCurrentIndex(TAB_INDEX["OCR"]))

        # self.btn_chart.clicked.connect(lambda: stacked_widget.setCurrentIndex(TAB_INDEX["CHARTS"]))


    # ========= データ操作 =========

    def load_item_and_summary(self):
        d = self._date_iso()
        name = self._item_name()
        if not d or not name:
            self.clear_table(self.item_table)
            self.clear_table(self.summary_table)
            return

        item_id = self.metrics_service.get_item_id_by_name(name)
        if item_id is None:
            QMessageBox.information(self, "未登録", "商品を追加してください。")
            return

        # --- Serviceからまとめて取得 ---
        data = self.metrics_service.load(d, item_id)

        # --- 商品テーブル ---
        clear_table(self.item_table)
        fill_table(self.item_table, data["item"], ITEM_ROW)

        # --- サマリテーブル ---
        clear_table(self.summary_table)
        customer_data = {"customer": data["customers"]}
        fill_table(self.summary_table, customer_data, SUMMARY_ROW)
        fill_table(self.summary_table, data["summary"], SUMMARY_ROW)

        # 合計値更新
        self.update_summary_table(d)

    def save_item_and_summary(self):
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
            self.load_item_and_summary()
        except Exception as e:
            QMessageBox.warning(self, "保存失敗", str(e))

    def update_summary_table(self, date_str: str):
        data = self.metrics_service.fetch_summary(date_str)
        fill_table(self.summary_table, data["summary"], SUMMARY_ROW)

    def reload_all(self):
        d = self._date_iso()
        name = self._item_name()
        if not d or not name:
            clear_table(self.item_table)
            clear_table(self.summary_table)
            self._refresh_chart()            
            return

        item_id = self.metrics_service.get_item_id_by_name(name)
        if item_id is None:
            QMessageBox.information(self, "未登録", "商品を追加してください。")
            return

        # --- テーブル更新 ---
        data = self.metrics_service.load(d, item_id)
        clear_table(self.item_table)
        fill_table(self.item_table, data["item"], ITEM_ROW)

        clear_table(self.summary_table)
        customer_data = {"customer": data["customers"]}
        fill_table(self.summary_table, customer_data, SUMMARY_ROW)
        fill_table(self.summary_table, data["summary"], SUMMARY_ROW)

        # --- グラフ更新 ---
        self._refresh_chart()
