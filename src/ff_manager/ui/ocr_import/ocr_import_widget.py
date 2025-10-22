# ui/ocr_import_widget.py
from PySide6.QtCore import Signal,Qt
from PySide6.QtGui import QIntValidator,QPixmap
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                                QTextEdit, QFileDialog,QTableWidget,QTableWidget, 
                                QTableWidgetItem, QHeaderView,QTableView
)
from PIL import Image
# from ff_manager.services.ocr.service import OCRService
from ff_manager.ui.effects.gradient_bg import GradientBackground
from ff_manager.core.constants import (
    HOURS, ITEM_METRICS,ITEM_LABELS_JA, ITEM_ROW, SUMMARY_ROWS,SUMMARY_LABELS_JA, SUMMARY_ROW
    ,TAB_INDEX
    )
from ff_manager.ui.edit_grid.tables import sanitize_int_item
from ffm_ocr.schemas import OcrImportPayload

from ff_manager.services.ocr.fakes import FakePipeline
from ff_manager.services.ocr.ocr_adapter import OcrAdapter
from ff_manager.config import OCR_TEST

class OCRImportWidget(QWidget):

    imported_item = Signal(dict)   # payloadは {metric: {hour: value}}

    def __init__(self, db, stack,parent=None):
        super().__init__(parent)
        
        # self.svc = OCRService(db)
        self.ocr = OcrAdapter(pipeline=FakePipeline() if OCR_TEST else None)


        self.btn_open = QPushButton("画像を開く")
        self.btn_ocr  = QPushButton("OCR実行")
        self.btn_save = QPushButton("保存")
        self.preview  = QLabel()
        self.preview.setMinimumSize(480, 240)
        self.text     = QTextEdit()


        self.btn_back=QPushButton("戻る")





        top = QHBoxLayout()
        top.addWidget(self.btn_open)
        top.addWidget(self.btn_ocr)
        top.addStretch()
        top.addWidget(self.btn_save)

        foot=QHBoxLayout()
        foot.addWidget(self.btn_back)
        foot.addStretch()

        root =QVBoxLayout(self)
        bg=GradientBackground(self)
        root.addWidget(bg)

        panel = QVBoxLayout(bg.content)
        panel.addLayout(top)
        panel.addWidget(self.preview)
        # panel.addWidget(self.text)
        # panel.addWidget(table)
        panel.addLayout(foot)

        self.current_image: Image.Image | None = None

        self.btn_open.clicked.connect(self._open)
        # self.btn_ocr.clicked.connect(self._run_ocr)
        self.btn_save.clicked.connect(self._save)
        self.btn_back.clicked.connect(lambda: stack.setCurrentIndex(TAB_INDEX["EDIT"]))

    def _open(self):
        path, _ = QFileDialog.getOpenFileName(self, "画像を選択", "", "Images (*.png *.jpg *.jpeg *.tif)")
        if not path: return
        self.current_image = Image.open(path).convert("RGB")
        pix = QPixmap(path).scaledToWidth(600)
        self.preview.setPixmap(pix)
        self.text.clear()

    def _run_ocr(self):
        if not self.current_image: return
        res = self.svc.recognize(self.current_image)
        self.text.setPlainText(res.full_text)

    def _save(self):
        """
        解析済みデータをEmitして、編集タブへ戻す。
        EditGrid側で fill_table(..., ITEM_ROW) を呼んで反映する想定。
        """
        if not self._parsed_item:
            return
        self.imported_item.emit(self._parsed_item)
        # 画面遷移（編集タブへ）
        self.parent().setCurrentIndex(TAB_INDEX["EDIT"]) if hasattr(self.parent(), "setCurrentIndex") else None


    def _parse_to_item_dict(self, text: str) -> dict[str, dict[int, int]]:
            """
            OCRした全文を、EditGridのitem_tableに流せる
            {metric: {hour: value}} 形式へ整形。
            例: 
            'sold 9=12, 10=7, 11=3\nstock 9=20 10=18'
            → {'sold': {9:12,10:7,11:3}, 'stock': {9:20,10:18}}
            """
            import re
            metrics: dict[str, dict[int, int]] = {}
            # 行ごとに「メトリクス名 + 時刻=値…」を拾う素朴な例
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                # 先頭の単語をmetric名とみなす（日本語/英字どちらでもOKなように緩めに）
                m = re.match(r"^([^\s:：]+)[\s:：]+(.+)$", line)
                if not m:
                    continue
                metric, rest = m.group(1), m.group(2)
                hour_vals: dict[int, int] = {}
                for token in re.split(r"[,\s]+", rest):
                    m2 = re.match(r"^(\d{1,2})\D+(\d+)$", token)  # 9=12 / 09:12 / 9-12 などを許容
                    if not m2:
                        continue
                    h = int(m2.group(1))
                    v = int(m2.group(2))
                    if 0 <= h <= 23:
                        hour_vals[h] = v
                if hour_vals:
                    metrics[metric] = hour_vals
            return metrics


    def _create_table(table_num:int):
        result={}

        for i in range(table_num):
            table = QTableWidget(len(ITEM_METRICS), len(HOURS) + 1)
            table.setHorizontalHeaderLabels([str(h) for h in HOURS] + ["合計"])
            table.setVerticalHeaderLabels([ITEM_LABELS_JA[m] for m in ITEM_METRICS])

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
