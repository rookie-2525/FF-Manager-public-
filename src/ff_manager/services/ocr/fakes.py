# tests or 開発用にどこかに置く（例: src/ff_manager/services/ocr/fakes.py）
from datetime import date
from ffm_ocr.schemas import OcrImportPayload, ProductSeries

class FakePipeline:
    """本物と同じインターフェースだけ持つ超軽量モック"""
    def __init__(self, *args, **kwargs):
        pass

    def run(self, image_nd):
        # 実際はセルを返すが、UIテストでは不要なので何も使わない
        return []  # ダミー

    def to_payload(self, cells, target_date, meta=None):
        # 固定の結果を返す（UIが表示できることが目的）
        return OcrImportPayload(
            version="1.0",
            date=target_date if isinstance(target_date, date) else date.today(),
            customers_by_hour={9: 18, 10: 22, 11: 35},
            products=[
                ProductSeries(
                    name="商品A",
                    by_metric={
                        "prep":    {9:12, 10:10, 11:8},
                        "sales":   {9:11, 10:9,  11:9},
                        "waste":   {10:1},
                        "display": {9:12, 10:10, 11:8}
                    }
                ),
                ProductSeries(
                    name="商品B",
                    by_metric={
                        "prep":  {9:6, 10:6},
                        "sales": {9:5, 10:7}
                    }
                )
            ],
            meta=meta or {"source": "fake"}
        )
