# services/ocr/paddle_engine_table.py
import cv2
import numpy as np
from ff_manager.services.ocr.preprocess import preprocess_for_ocr,_deskew
from paddleocr import TableCellsDetection
from PIL import Image
import tempfile
from pathlib import Path
import os

class PaddleTableEngine:
    def __init__(self):
        # ===== 1. モデル準備 =====
        self.model = TableCellsDetection(model_name="RT-DETR-L_wired_table_cell_det")






    def run(self, img_path: str,out_img_path:str):

        pil_img=Image.open(img_path).convert("RGB")


        # 前処理
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        img=self.preproc(pil_img,out_img_path)


        # output = self.model.predict(img.name, threshold=0.3, batch_size=1)
        # # 一時ファイルに保存してパス渡し
        # with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        #     cv2.imwrite(tmp.name, img)
        #     output = self.model.predict(tmp.name, threshold=0.3, batch_size=1)
        

        # for res in output:
        #     res.save_to_img(out_img_path)

