from __future__ import annotations

# 時間帯(0-23)
HOURS=list(range(24))

# 商品系メトリクス
ITEM_METRICS=["prepared","sold","discarded","stock"]
ITEM_LABELS_JA = {
    "prepared"  : "仕込",
    "sold"      : "販売",
    "discarded" : "廃棄",
    "stock"     : "陳列",
}
ITEM_ROW={m:i for i,m in enumerate(ITEM_METRICS)}

# サマリ表の行
SUMMARY_ROWS=["customer"]+ITEM_METRICS
SUMMARY_LABELS_JA={"customer":"客数",**ITEM_LABELS_JA}

SUMMARY_ROW={m:i for i,m in enumerate(SUMMARY_ROWS)}

