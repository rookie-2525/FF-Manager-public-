# ui/styles.py
TABLE_SELECTED_ROW_QSS = """
QTableView::item:selected {
    background-color: #ccffcc;  /* 選択背景 */
    color: black;               /* 文字色   */
}
"""

def apply_table_style(view):
    view.setStyleSheet(TABLE_SELECTED_ROW_QSS)
