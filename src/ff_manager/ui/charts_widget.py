# ui/charts_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
# from ff_manager.services.chart_service import ChartService

class ChartsWidget(QWidget):
    def __init__(self, chart_service,stacked_widget, parent=None):
        super().__init__(parent)
        self.chart_service = chart_service

        # メトリクス選択
        self.metric_combo = QComboBox()
        self.metric_combo.addItems(["customer","prepared","sold","discarded","stock"])

        # matplotlib キャンバス
        self.canvas = FigureCanvas(Figure(figsize=(6,4)))
        self.ax = self.canvas.figure.subplots()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("メトリクス:"))
        layout.addWidget(self.metric_combo)
        layout.addWidget(self.canvas)

        # signal
        self.metric_combo.currentTextChanged.connect(self.update_chart)

        self.update_chart()  # 初期描画

    def update_chart(self):
        metric = self.metric_combo.currentText()

        # とりあえず固定の期間・商品
        data = self.chart_service.get_metric_timeseries(("2025-01-01","2025-01-01"), metric)

        self.ax.clear()
        for date, values in data.items():
            hours = list(values.keys())
            vals = list(values.values())
            self.ax.plot(hours, vals, marker="o", label=date)

        self.ax.set_title(f"{metric} 時系列")
        self.ax.set_xlabel("時間")
        self.ax.set_ylabel("数値")
        self.ax.legend()
        self.canvas.draw()
