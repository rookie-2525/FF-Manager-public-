from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Literal, Optional, Any

Hour = int                        # 0..23
Metric = Literal["prep","sales","waste","display"]  # 仕込み/販売/廃棄/陳列
ByHour = Dict[Hour, int]          # {9: 12, 10: 7, ...}

@dataclass
class ProductSeries:
    name: str                     # 商品名（UI表示名）
    by_metric: Dict[Metric, ByHour] = field(default_factory=dict)
    sku: Optional[str] = None     # 任意: SKU/コード
    notes: Optional[str] = None   # 任意: 補足

@dataclass
class OcrImportPayload:
    version: str                  # スキーマ版（将来の互換に備える）
    date: date                    # 対象日
    customers_by_hour: ByHour     # 客数（時間別）
    products: List[ProductSeries] # 複数商品に対応
    meta: Dict[str, Any] = field(default_factory=dict)  # 画像ID/信頼度など
