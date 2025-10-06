# services/ocr/service.py
import cv2
import json, io, logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import asdict
from PIL import Image
import numpy as np
from .preprocess import preprocess_for_ocr
from .paddle_engine import PaddleEngine
from ff_manager.services.ocr.paddle_engine_table import PaddleTableEngine 
from .types import OCRResult
from ff_manager.db.repositories.ocr_repo import OCRCacheRepo


logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self, db, timeout_sec: int = 10):
        self.engine = PaddleEngine(lang="japan", use_angle_cls=True)
        self.engine_table=PaddleTableEngine(lang="japan")
        self.cache = OCRCacheRepo(db)
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.timeout = timeout_sec

    def _bytes_and_params(self, pil_img: Image.Image) -> tuple[bytes, dict]:
        """ キャッシュ前処理 """

        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        return buf.getvalue(), {"pre": "deskew+adaptive+denoise", "engine": "paddle(japan)"}

    def recognize(self, pil_img: Image.Image) -> OCRResult:
        # キャッシュキー
        raw_bytes, params = self._bytes_and_params(pil_img)
        key = self.cache.build_key(raw_bytes, params)

        # キャッシュ命中
        hit = self.cache.get(key)
        if hit:
            data = json.loads(hit)
            lines = [tuple(l) for l in data["lines"]]  # ここは本来 types で復元してもOK
            # 簡略化のため full_text だけ返す
            return OCRResult(lines=[], full_text=data["full_text"])

        # 前処理
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        proc = preprocess_for_ocr(bgr)

        # OCR（タイムアウト管理）
        fut = self.pool.submit(self.engine.run, proc)
        try:
            result: OCRResult = fut.result(timeout=self.timeout)
        except TimeoutError:
            logger.exception("OCR timeout")
            raise RuntimeError("OCR timeout")

        # キャッシュ保存
        payload = {
            "full_text": result.full_text,
            "lines": [[l.text, l.conf, l.box] for l in result.lines],
        }
        self.cache.put(key, params, json.dumps(payload, ensure_ascii=False))
        return result
