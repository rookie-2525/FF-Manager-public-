# tables.py
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView,QTableView
from PySide6.QtGui import QIntValidator
from PySide6.QtCore import Qt

from ff_manager.core.constants import HOURS


def init_summary_table(summary_rows, summary_labels) -> QTableWidget:
    """
    サマリ用テーブルを初期化して返す
    """
    table = QTableWidget(len(summary_rows), len(HOURS) + 1)
    table.setHorizontalHeaderLabels([str(h) for h in HOURS] + ["合計"])
    table.setVerticalHeaderLabels([summary_labels[m] for m in summary_rows])

    table.setObjectName("dataTable")

    validator = QIntValidator(0, 1_000_000, table)
    for r in range(table.rowCount()):
        for c in range(table.columnCount()):
            it = QTableWidgetItem("0")
            it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if r == 0:
                if c == 24:
                    it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                else:
                    it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
            else:
                it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            table.setItem(r, c, it)
    table.itemChanged.connect(lambda item: sanitize_int_item(item, validator))

    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
    return table

def init_item_table(item_metrics, item_labels) -> QTableWidget:
    """
    商品用テーブルを初期化して返す
    """
    table = QTableWidget(len(item_metrics), len(HOURS) + 1)
    table.setHorizontalHeaderLabels([str(h) for h in HOURS] + ["合計"])
    table.setVerticalHeaderLabels([item_labels[m] for m in item_metrics])

    table.setObjectName("dataTable")

    validator = QIntValidator(0, 1_000_000, table)
    for r in range(table.rowCount()):
        for c in range(table.columnCount()):
            it = QTableWidgetItem("0")
            it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
            table.setItem(r, c, it)
    table.itemChanged.connect(lambda item: sanitize_int_item(item, validator))

    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
    return table


def sanitize_int_item(item: QTableWidgetItem, validator: QIntValidator):
    """
    入力を整数に制限する（空文字や不正値は 0 に補正）
    """
    text = (item.text() or "").strip()
    if text == "":
        item.setText("0")
        return
    pos = 0
    if validator.validate(text, pos)[0] != QIntValidator.Acceptable:
        try:
            int(text)
        except Exception:
            item.setText("0")


def clear_table(table: QTableWidget):
    """全セルを 0 でクリア"""
    for r in range(table.rowCount()):
        for c in range(table.columnCount()):
            table.item(r, c).setText("0")


def fill_table(table: QTableWidget, data: dict, row_map: dict):
    """
    dict のデータを QTableWidget に流し込む共通関数

    Args:
        table (QTableWidget): 対象テーブル
        data (dict): {metric: {hour: value}}
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

