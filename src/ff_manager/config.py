# config.py
import os

TEST_MODE = os.getenv("TEST_MODE", "0") == "1"

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