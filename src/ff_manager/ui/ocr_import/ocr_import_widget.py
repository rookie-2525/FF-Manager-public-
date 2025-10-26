# ui/ocr_import_widget.py
from PySide6.QtCore import Signal,Qt
from PySide6.QtGui import QIntValidator,QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QFileDialog,QTableWidget,QTableWidget, 
    QTableWidgetItem, QHeaderView,QTabWidget,QMessageBox,
    QScrollArea,
)
from PIL import Image

import numpy as np
from datetime import date

# from ff_manager.services.ocr.service import OCRService
from ff_manager.ui.effects.gradient_bg import GradientBackground
from ff_manager.core.constants import (
    HOURS, ITEM_METRICS,ITEM_LABELS_JA, ITEM_ROW, SUMMARY_ROWS,SUMMARY_LABELS_JA, SUMMARY_ROW
    ,TAB_INDEX
    )
from ff_manager.ui.edit_grid.tables import (
    init_item_table,
    clear_table,
    fill_table,
)
from ff_manager.ui.edit_grid.tables import sanitize_int_item
from ffm_ocr.schemas import OcrImportPayload

from ff_manager.services.metrics_service import MetricsService
from ff_manager.services.ocr.fakes import FakePipeline
from ff_manager.services.ocr.ocr_adapter import OcrAdapter

from ff_manager.config import OCR_TEST

class OCRImportWidget(QWidget):

    imported_item = Signal(dict)   # payloadは {metric: {hour: value}}

    def __init__(
            self,
            metrics_service:MetricsService,
            stack,parent=None
            ):
        super().__init__(parent)
        
        # self.svc = OCRService(db)
        self.metrics_service=metrics_service

        self.ocr = OcrAdapter(pipeline=FakePipeline() if OCR_TEST else None)
        self.ocr.finished.connect(self._on_ocr_done)
        self.ocr.failed.connect(self._on_ocr_failed)
        
        #--- テーブル ---

        # self.tables_area = QScrollArea(self)
        # self.tables_area.setWidgetResizable(True)

        # self.tables_container = QWidget(self.tables_area)
        # self.tables_layout = QVBoxLayout(self.tables_container)
        # self.tables_layout.setContentsMargins(0, 0, 0, 0)
        # self.tables_layout.setSpacing(12)
        # self.tables_layout.addStretch()  # 一番下に余白

        # self.tables_area.setWidget(self.tables_container)

        #--- マルチタブ ---
        self.item_tabs = QTabWidget(self)
        self.item_tabs.setDocumentMode(True)           # mac/Winでフラットな見た目
        self.item_tabs.setMovable(True)                # タブ並べ替え可
        self.item_tabs.setTabsClosable(False)          # 必要なら True に
        self.item_tabs.setUsesScrollButtons(True)      # タブが多い時に左右スクロール
        self.item_tabs.setElideMode(Qt.ElideRight)     # ラベル長い時は省略


        #--- button ---
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
        panel.addWidget(self.item_tabs)



        panel.addLayout(foot)

        self.current_image: Image.Image | None = None

        self.btn_open.clicked.connect(self._open)
        self.btn_ocr.clicked.connect(self._run_ocr)
        self.btn_save.clicked.connect(self._save)
        self.btn_back.clicked.connect(lambda: stack.setCurrentIndex(TAB_INDEX["EDIT"]))

    def clear_layout(layout):
        # addStretch を残したい場合は count()-1 まで回す
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            # 最後の stretch を残す例
            if item.spacerItem():
                continue
            w = item.widget()
            if w is not None:
                layout.removeWidget(w)
                w.setParent(None)
                w.deleteLater()
            else:
                # ネストしたレイアウトがある場合
                child = layout.takeAt(i)
                sub = child.layout()
                # if sub:
                #     clear_layout(sub)


    # def on_click_run_ocr(self):
    #     qimg = self.image_preview.currentQImage()
    #     target_date = self.datePicker.date().toPython()         # QDateEdit等から
    #     self.ocr.run_on_qimage(qimg, target_date=target_date)   # 非同期開始

    def _on_ocr_done(self, payload:OcrImportPayload):
        self.table_list=[QTableWidget]
        date=self.ocr.get_date(payload)


        item_info=self.ocr.get_item_info(payload)
        for prod in item_info:
            table=init_item_table(ITEM_METRICS,ITEM_LABELS_JA)
            name:str=prod[0]
            info:dict=prod[1]
            id=self.metrics_service.get_item_id_by_name(name)
            tab_label = self._make_tab_label(name)

            self.metrics_service.save_item_metrics(date,id,info)
            for culmns,data_list in info.items():
                for data in data_list.items():
                    c=ITEM_ROW[culmns]
                    h,v=data[0],data[1]
                    table.item(c,h).setText(str(v))

            self.item_tabs.addTab(table, tab_label)
            self.table_list.append(table)

        

    def _on_ocr_failed(self, msg: str):
        QMessageBox.warning(self, "OCR失敗", msg)


    def _open(self):
        path, _ = QFileDialog.getOpenFileName(self, "画像を選択", "", "Images (*.png *.jpg *.jpeg *.tif)")
        if not path: return
        self.current_image = Image.open(path).convert("RGB")
        pix = QPixmap(path).scaledToWidth(600)
        self.preview.setPixmap(pix)
        self.text.clear()

    def _run_ocr(self):
        # if not self.current_image: return
        # res = self.svc.recognize(self.current_image)
        # self.text.setPlainText(res.full_text)
        
        
        # if self.current_image is None:
        #     return
        # rgb = np.array(self.current_image, copy=True)   # (H,W,3) RGB
        # bgr = rgb[:, :, ::-1]                          # OpenCV/PaddleはBGR想定
        
        bgr = np.zeros((800, 600, 3), dtype=np.uint8)


        self.ocr.run_on_ndarray(bgr, target_date=date(2025,1,1),meta={"source":"dummy"})

    def _save(self):
        """
        解析済みデータをデータベースに反映
        """
        



    def _make_tab_label(self, prod) -> str:
        """
        prod.name や prod.id がある前提の例。
        どちらも無ければ 'Item N' 形式にフォールバック。
        """
        name = getattr(prod, "name", None) or getattr(prod, "label", None) or ""
        pid  = getattr(prod, "id", None)

        base = name.strip() or (f"Item {pid}" if pid is not None else "Item")
        if pid is not None:
            base = f"{base}#{pid}"

        # 長すぎる場合を省略
        max_len = 24
        if len(base) > max_len:
            base = base[:max_len - 1] + "…"
        return base

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
