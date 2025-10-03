# services/ocr/types.py
from dataclasses import dataclass
from typing import List, Tuple

Box = List[Tuple[int,int]]  # 4点 (x,y) のリスト

@dataclass
class OCRLine:
    text: str
    conf: float
    box: Box

@dataclass
class OCRResult:
    lines: List[OCRLine]
    full_text: str
