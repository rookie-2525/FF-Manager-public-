# ui/ocr_import_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QFileDialog
from PySide6.QtGui import QPixmap
from PIL import Image
from ff_manager.services.ocr.service import OCRService
from ff_manager.ui.effects.gradient_bg import GradientBackground
from ff_manager.core.constants import TAB_INDEX

class OCRImportWidget(QWidget):
    def __init__(self, db, stack,parent=None):
        super().__init__(parent)
        # self.svc = OCRService(db)

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
        panel.addWidget(self.text)
        panel.addLayout(foot)

        self.current_image: Image.Image | None = None

        self.btn_open.clicked.connect(self._open)
        self.btn_ocr.clicked.connect(self._run_ocr)
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
        # ここでDBに保存（あなたの既存 items / 日付等のスキーマに合わせて）
        # まずはテキストをどこかに保存できればOK
        pass
