from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout, QPushButton
)
import sys


class MetricsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFM (KPIサンプル)")

        # 左側の表（テスト用に5行24列）
        self.table = QTableWidget(5, 24)
        self.table.setHorizontalHeaderLabels([str(i) for i in range(24)])
        self.table.setVerticalHeaderLabels(["客数", "仕込", "販売", "廃棄", "陳列"])
        for r in range(5):
            for c in range(24):
                self.table.setItem(r, c, QTableWidgetItem("0"))

        # 右側の KPI 表示
        kpi_box = QGroupBox("KPI")
        kpi_layout = QGridLayout()

        self.kpi_sales = QLabel("販売合計: 0")
        self.kpi_discard = QLabel("廃棄合計: 0")
        self.kpi_stock = QLabel("在庫率: 0 %")
        self.kpi_customer = QLabel("客数合計: 0")

        kpi_layout.addWidget(self.kpi_sales, 0, 0)
        kpi_layout.addWidget(self.kpi_discard, 1, 0)
        kpi_layout.addWidget(self.kpi_stock, 2, 0)
        kpi_layout.addWidget(self.kpi_customer, 3, 0)

        kpi_box.setLayout(kpi_layout)

        # 「KPI更新」ボタン
        update_btn = QPushButton("KPI更新")
        update_btn.clicked.connect(self.update_kpis)

        # 横並びレイアウト
        hbox = QHBoxLayout()
        hbox.addWidget(self.table, stretch=3)
        hbox.addWidget(kpi_box, stretch=1)

        # 全体レイアウト
        layout = QVBoxLayout(self)
        layout.addLayout(hbox)
        layout.addWidget(update_btn)

    def update_kpis(self):
        """テーブルの値からKPIを計算して更新"""
        total_sales = sum(int(self.table.item(2, c).text()) for c in range(24))
        total_discard = sum(int(self.table.item(3, c).text()) for c in range(24))
        total_customer = sum(int(self.table.item(0, c).text()) for c in range(24))

        self.kpi_sales.setText(f"販売合計: {total_sales}")
        self.kpi_discard.setText(f"廃棄合計: {total_discard}")
        self.kpi_customer.setText(f"客数合計: {total_customer}")

        stock_rate = 0 if total_sales == 0 else round((total_discard / total_sales) * 100, 1)
        self.kpi_stock.setText(f"在庫率: {stock_rate} %")


def main():
    app = QApplication(sys.argv)
    w = MetricsWidget()
    w.resize(1000, 400)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()