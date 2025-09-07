# db/aggregate.py
from PySide6.QtSql import QSqlQuery

# --- 日付ユーティリティ（YYYY-MM-DD に正規化：2025/1/2 → 2025-01-02） ---
def normalize_date(s: str) -> str:
    if not s:
        return ""
    t = s.strip().replace(".", "-").replace("/", "-")
    try:
        y, m, d = [int(p) for p in t.split("-")]
        return f"{y:04d}-{m:02d}-{d:02d}"
    except Exception:
        return ""

# --- 指定日の「商品ごと日次」を再計算（UPSERT） ---
def rebuild_daily_products_for_date(db, date_iso: str) -> bool:
    """
    fact_hourly_long → fact_daily を date_iso(YYYY-MM-DD) だけ再計算してUPSERT
    戻り値: 成否（True/False）
    """
    if not date_iso:
        return False
    q = QSqlQuery(db)
    q.prepare("""
        INSERT INTO fact_daily(date,item_id,prepared,sold,discarded,stock_end)
        SELECT
          h.date, h.item_id,
          SUM(CASE WHEN h.metric='prepared'  THEN h.value ELSE 0 END) AS prepared,
          SUM(CASE WHEN h.metric='sold'      THEN h.value ELSE 0 END) AS sold,
          SUM(CASE WHEN h.metric='discarded' THEN h.value ELSE 0 END) AS discarded,
          COALESCE((
            SELECT h2.value
            FROM fact_hourly_long h2
            WHERE h2.date = h.date AND h2.item_id = h.item_id AND h2.metric='stock'
            ORDER BY h2.hour DESC
            LIMIT 1
          ), 0) AS stock_end
        FROM fact_hourly_long h
        WHERE h.date = :d
        GROUP BY h.date, h.item_id
        ON CONFLICT(date, item_id) DO UPDATE SET
          prepared  = excluded.prepared,
          sold      = excluded.sold,
          discarded = excluded.discarded,
          stock_end = excluded.stock_end
    """)
    q.bindValue(":d", date_iso)
    return q.exec()

# --- 指定日の「日次客数」を再計算（UPSERT） ---
def rebuild_daily_customer_for_date(db, date_iso: str) -> bool:
    """
    fact_hourly_customer → fact_daily_customer を date_iso だけ再計算してUPSERT
    戻り値: 成否（True/False）
    """
    if not date_iso:
        return False
    q = QSqlQuery(db)
    q.prepare("""
        INSERT INTO fact_daily_customer(date, customer_count)
        SELECT :d, COALESCE(SUM(customer_count), 0)
        FROM fact_hourly_customer
        WHERE date = :d
        ON CONFLICT(date) DO UPDATE SET
          customer_count = excluded.customer_count
    """)
    q.bindValue(":d", date_iso)
    return q.exec()

# --- まとめて（指定日） ---
def rebuild_daily_for_date(db, date_iso: str) -> bool:
    """
    指定日の商品サマリ＆客数サマリをまとめて再計算。
    トランザクションでまとめて成功/失敗を統一。
    """
    if not date_iso:
        return False
    db.transaction()
    try:
        ok1 = rebuild_daily_products_for_date(db, date_iso)
        ok2 = rebuild_daily_customer_for_date(db, date_iso)
        if not (ok1 and ok2):
            raise RuntimeError("daily rebuild failed")
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False

# --- 全期間を作り直す（必要な時だけ手動で呼ぶ） ---
def rebuild_daily_all(db) -> bool:
    q = QSqlQuery(db)
    ok = q.exec("DELETE FROM fact_daily") and q.exec("DELETE FROM fact_daily_customer")
    if not ok:
        return False
    # 商品サマリ全期間
    ok = q.exec("""
        INSERT INTO fact_daily(date,item_id,prepared,sold,discarded,stock_end)
        SELECT
          h.date, h.item_id,
          SUM(CASE WHEN h.metric='prepared'  THEN h.value ELSE 0 END),
          SUM(CASE WHEN h.metric='sold'      THEN h.value ELSE 0 END),
          SUM(CASE WHEN h.metric='discarded' THEN h.value ELSE 0 END),
          COALESCE((
            SELECT h2.value
            FROM fact_hourly_long h2
            WHERE h2.date=h.date AND h2.item_id=h.item_id AND h2.metric='stock'
            ORDER BY h2.hour DESC LIMIT 1
          ),0)
        FROM fact_hourly_long h
        GROUP BY h.date, h.item_id
    """)
    if not ok:
        return False
    # 客数サマリ全期間
    ok = q.exec("""
        INSERT INTO fact_daily_customer(date, customer_count)
        SELECT date, SUM(customer_count)
        FROM fact_hourly_customer
        GROUP BY date
    """)
    return ok
