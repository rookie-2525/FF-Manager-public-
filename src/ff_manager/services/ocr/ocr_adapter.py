from PySide6.QtCore import QObject, Signal, QRunnable, Slot, QThreadPool,QDate
import numpy as np
from typing import Optional
from ffm_ocr.pipeline import OcrPipeline
from ffm_ocr.schemas import OcrImportPayload, ProductSeries
# QImage→ndarray
from ff_manager.ui.utils.image import qimage_to_ndarray  
from ff_manager.core.constants import ITEM_LABELS_JA

class OcrAdapter(QObject):
    finished = Signal(object)          # payload を返す
    failed = Signal(str)
    progress = Signal(int)             # 任意: 0-100

    # def __init__(self, lang="japan", use_gpu=False, model_name="RT-DETR-L_wired_table_cell_det", parent=None):
    def __init__(self,pipeline:Optional[OcrPipeline]=None, parent=None):
        super().__init__(parent)
        self.pipe = pipeline or OcrPipeline()
        self.pool = QThreadPool.globalInstance()

    def run_on_qimage(self, qimage, target_date, meta: Optional[dict]=None):
        img = qimage_to_ndarray(qimage)     # BGR/RGB注意（ヘルパ内で吸収）
        self._submit(img, target_date, meta or {})

    def run_on_ndarray(self, img_nd: np.ndarray, target_date, meta: Optional[dict]=None):
        self._submit(img_nd, target_date, meta or {})

    def _submit(self, img_nd, target_date, meta):
        worker = _OcrWorker(self.pipe, img_nd, target_date, meta)
        worker.finished.connect(self.finished)
        worker.failed.connect(self.failed)
        worker.progress.connect(self.progress)
        self.pool.start(worker)

    def get_item_info(self,payload: OcrImportPayload) -> list[list[str,dict[str, dict[int,int]]]]:
        ret=[]

        for prod in payload.products:

            info: dict[str, dict[int,int]] = {}
            name=prod.name
            for m, series in prod.by_metric.items():
                info[m] = {int(h): int(v) for h, v in series.items()}
            item=[name,info]
            ret.append(item)
        return ret

    def get_date(self, payload: OcrImportPayload)->QDate:
        d=payload.date
        return QDate(d.year,d.month,d.day)
    


class _OcrWorker(QObject, QRunnable):
    finished = Signal(object)   # OcrImportPayload
    failed = Signal(str)
    progress = Signal(int)

    def __init__(self, pipe: OcrPipeline, img_nd, target_date, meta):
        QObject.__init__(self)
        QRunnable.__init__(self)
        self.pipe = pipe
        self.img_nd = img_nd
        self.target_date = target_date
        self.meta = meta
        self.setAutoDelete(True)  # 使い捨て（デフォルトTrue）

    @Slot()
    def run(self):
        try:
            # （必要ならここで self.progress.emit(…）を入れる）
            cells = self.pipe.run(self.img_nd)
            payload = self.pipe.to_payload(cells, self.target_date, meta=self.meta)
            self.finished.emit(payload)
        except Exception as e:
            self.failed.emit(str(e))
