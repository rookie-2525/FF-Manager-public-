# services/ocr/paddle_engine_table.py
from paddleocr._pipelines import PPStructureV3
import cv2
import os

class PaddleTableEngine:
    def __init__(self, lang: str = "japan", det_limit_side_len: int = 960, use_gpu=True):
        """
        PaddleOCR の表構造解析エンジン（PPStructureV3）を初期化
        """
        # self.engine = PPStructureV3(
        #     lang=lang,
        #     show_log=True,
        #     layout=False,  # 表構造に特化
        #     det_limit_side_len=det_limit_side_len,
        #     device='gpu' if use_gpu else 'cpu'
        # )
        self.engine=PPStructureV3(device="cpu")
    
    def run(self, img_path: str,out_img_path:str):
        """画像を解析してテーブル構造を返す"""

        results = self.engine.predict(img_path)

        res = results[0]  # 最初の表を取り出す
        table_res_list = res.get("table_res_list", [])

        # 最初の表のHTML構造を取得
        html = table_res_list[0].get("pred_html", "") if table_res_list else ""

        # HTMLを保存
        if html:
            with open(out_img_path, "w", encoding="utf-8") as f:
                f.write(html)
            print("✅ HTMLファイルに出力しました: output_table.html")
        else:
            print("⚠️ 表のHTMLが検出されませんでした。")