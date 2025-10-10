# src/ff_manager/ui/styles/theme.py
from pathlib import Path

def load_qss() -> str:
    """ui/styles/widgets.qss を読み込んで返すだけ（最小）"""
    here = Path(__file__).parent
    widgets_qss = (here / "widgets.qss").read_text(encoding="utf-8")
    return widgets_qss
