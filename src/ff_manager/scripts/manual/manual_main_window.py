from PySide6.QtWidgets import QApplication, QMainWindow
import sys

# メインウィンドウクラスを定義
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My PySide6 App")   # ウィンドウタイトル
        self.setGeometry(100, 100, 800, 600)    # x, y, width, height


# 実行エントリーポイント
def main():
    app = QApplication(sys.argv)   # Qtアプリケーションを作成
    window = MainWindow()          # ウィンドウインスタンス
    window.show()                  # ウィンドウ表示
    sys.exit(app.exec())           # イベントループ開始


# src/ff_manager/scripts/manual/manual_main_window.py

# import sys
# from PySide6.QtWidgets import QApplication
# from ff_manager.ui.main_window import MainWindow


# def main():
#     """UI確認用のエントリーポイント"""
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     app.exec()


# # ← 重要: __name__ == "__main__" のブロックは無くてもOK
# # Poetry の script エントリは main() を直接呼ぶから
# if __name__ == "__main__":
#     main()
