# ui/chart_area.py
from PySide6.QtWidgets import QPushButton
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ff_manager.core.constants import HOURS, ITEM_LABELS_JA

class ChartArea:
    def __init__(self, parent_widget):
        """簡易グラフ描画エリア"""
        self.parent = parent_widget

        # Figure/Canvas
        self.figure = Figure(figsize=(4, 2))
        self.canvas = FigureCanvas(self.figure)

        # 軸
        self.ax = self.figure.subplots()
        self.ax2 = self.ax.twinx()  # 右軸を保持

        # 初期状態は非表示
        self.canvas.setVisible(False)


    # ---------------- Public API ----------------
    def widget(self):
        """Canvas をレイアウトに埋め込むために返す"""
        return self.canvas

    # def button(self):
    #     """チャート表示ボタンを返す"""
    #     return self.btn_chart

    def refresh(self, data: dict):
        """データを使ってチャートを更新"""
        self.ax.clear()
        self.ax2.clear()
        self.ax.set_xticks(HOURS)

        # 左軸: 商品メトリクス
        for m, la in ITEM_LABELS_JA.items():
            self.ax.plot(HOURS, data[m], label=la)
        self.ax.set_ylim(0, 20)

        # 右軸: 客数
        self.ax2.plot(HOURS, data["customer"], color="black", linestyle="--", label="客数")
        self.ax2.set_ylim(0, 200)

        # 軸ラベルなど
        self.ax.set_xlabel("Hour")
        self.ax.set_ylabel("Count")
        self.ax.legend(loc="upper left")
        self.ax2.legend(loc="upper right")

        self.canvas.draw()

    # ---------------- Internal ----------------
    # def _toggle(self, checked: bool):
    #     self.canvas.setVisible(checked)
    #     if checked:
    #         # 親ウィジェットに更新処理を委譲
    #         self.parent.refresh_chart()
