# config.py
import os
from matplotlib import rcParams, font_manager

TEST_MODE = os.getenv("TEST_MODE", "0") == "1"
OCR_TEST = os.getenv("OCR_TEST", "0") == "1"

# --- 環境ごとのフォント設定 ---
if os.name == "nt":  # Windows
    FONT_PATH = "C:/Windows/Fonts/meiryo.ttc"
elif os.name == "posix":  # macOS/Linux
    FONT_PATH = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"  # Macの例
else:
    FONT_PATH = None

if FONT_PATH and os.path.exists(FONT_PATH):
    rcParams["font.family"] = font_manager.FontProperties(fname=FONT_PATH).get_name()



DB_PATH = r"data\prot.db" if TEST_MODE else r"data\FF_info.db"


WINDOW_TITLE = "FFM (prot)" if TEST_MODE else "FF Manager"
WINDOW_SIZE = [900,550]

TABLE = "items"


HEADER_JP = {
    "log_id":"log ID",
    "date":"日付",
    "hour":"時間",
    "customer_count":"客数",
    "item_id":"商品名",
    "prepared":"仕込数",
    "sold":"販売数",
    "discarded":"廃棄数",
    "stock":"陳列数",
}