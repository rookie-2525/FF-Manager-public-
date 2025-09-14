# from PySide6.QtWidgets import QApplication, QMainWindow
# import sys

# # メインウィンドウクラスを定義
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("My PySide6 App")   # ウィンドウタイトル
#         self.setGeometry(100, 100, 800, 600)    # x, y, width, height


# # 実行エントリーポイント
# def main():
#     app = QApplication(sys.argv)   # Qtアプリケーションを作成
#     window = MainWindow()          # ウィンドウインスタンス
#     window.show()                  # ウィンドウ表示
#     sys.exit(app.exec())           # イベントループ開始

# src/ff_manager/scripts/manual/manual_main_window.py

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox
)
# from ff_manager.config import DB_PATH
# from ff_manager.db.connection import get_db
# from ff_manager.ui.main_window import MainWindow

# from ff_manager.db.repositories.items_repo import list_item_names, get_item_id_by_name, add_item

class ProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("商品情報の入力")

        # 入力フォーム
        self.name_edit = QLineEdit()
        self.category_edit = QLineEdit()
        self.freshness_edit = QLineEdit()

        form = QFormLayout()
        form.addRow("商品名:", self.name_edit)
        form.addRow("カテゴリ:", self.category_edit)
        form.addRow("鮮度:", self.freshness_edit)

        # OK / Cancel ボタン
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)  # OKで閉じる
        buttons.rejected.connect(self.reject)  # Cancelで閉じる

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def get_data(self):
        """入力されたデータを辞書で返す"""
        return {
            "name": self.name_edit.text(),
            "category": self.category_edit.text(),
            "freshness": self.freshness_edit.text(),
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("メイン画面")

        self.button = QPushButton("商品情報を追加")
        self.button.clicked.connect(self.open_product_dialog)

        layout = QVBoxLayout()
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_product_dialog(self):
        dialog = ProductDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            QMessageBox.information(self, "入力結果", f"商品名: {data['name']}\nカテゴリ: {data['category']}\n鮮度: {data['freshness']}")



def main():
    app = QApplication(sys.argv)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
