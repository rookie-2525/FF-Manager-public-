# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QPushButton
from PySide6.QtGui import QPainter, QLinearGradient, QColor
from PySide6.QtCore import Qt

class GradientBackground(QWidget):
    """
    画面全面に縦グラデ（上:濃いティール → 下:エメラルド）
    - リサイズ対応
    - 透過カードを1枚置ける（不要なら削除OK）
    """
    def __init__(self, parent=None, stops=None):
        super().__init__(parent)
        # 画像っぽい色合い（必要なら後で微調整）
        self.stops = stops or [
            (0.0, "#0F2027"),  # deep teal
            (0.55, "#2C5364"), # blue-teal
            (1.0, "#2EBF91"),  # emerald
        ]
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        # 置き場（中に好きなウィジェットを入れて使う）
        self.content = QFrame(self)
        self.content.setObjectName("content")
        self.content.setStyleSheet("""
            QFrame#content {
                background: rgba(255,255,255,0.06);
                border-radius: 12px;
            }
            QLabel, QPushButton { color: white; }
            QPushButton {
                background: rgba(255,255,255,0.16);
                border: 1px solid rgba(255,255,255,0.25);
                padding: 4px 6px; border-radius: 10px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.22); }
        """)
        lay.addWidget(self.content)


    def paintEvent(self, e):
        p = QPainter(self)
        g = QLinearGradient(0, 0, 0, self.height())
        for pos, col in self.stops:
            g.setColorAt(pos, QColor(col))
        p.fillRect(self.rect(), g)
