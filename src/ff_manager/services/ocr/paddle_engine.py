# services/ocr/paddle_engine.py
from paddleocr import PaddleOCR
from .types import OCRLine, OCRResult

class PaddleEngine:
    def __init__(self, lang: str = "japan", use_angle_cls: bool = True):
        self.ocr = PaddleOCR(use_angle_cls=use_angle_cls, lang=lang)  # 初回はモデルDL

    def run(self, img) -> OCRResult:
        """
        img: numpy ndarray (BGR or GRAY) / file path 両方OK
        """
        res = self.ocr.ocr(img, cls=True)
        lines = []
        for page in res:
            for box, (txt, conf) in page:
                # box: 4点のfloat座標
                lines.append(OCRLine(text=txt, conf=float(conf), box=[tuple(map(int, p)) for p in box]))
        full = "\n".join(l.text for l in lines)
        return OCRResult(lines=lines, full_text=full)
