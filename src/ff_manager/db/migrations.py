# db/migrations.py
from PySide6.QtSql import QSqlQuery

def ensure_schema_and_migrate(db, table: str):
    db.transaction()
    try:
        q = QSqlQuery(db)
        cur = _get_schema_version(db)

         # v1: 商品マスタ
        if cur < 1:
            q.exec("""
            CREATE TABLE IF NOT EXISTS items(
                item_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name     TEXT NOT NULL UNIQUE,
                price         INTEGER NOT NULL,
                freshness     INTEGER,
                sales_class   TEXT CHECK(sales_class IN ('normal','limited')), 
                item_type     TEXT CHECK(item_type IN ('ambient','heated','chukaman','oden')),
                is_active     INTEGER NOT NULL DEFAULT 1
            )""")
            q.exec("CREATE INDEX IF NOT EXISTS idx_items_name ON items(item_name)")
            _set_schema_version(db, 1); cur = 1

        # v2: 時間別ロング（商品メトリクス）
        if cur < 2:
            q.exec("""
            CREATE TABLE IF NOT EXISTS fact_hourly_long(
                date    TEXT    NOT NULL,     -- 'YYYY-MM-DD'
                hour    INTEGER NOT NULL,     -- 0..23
                item_id INTEGER NOT NULL,
                metric  TEXT    NOT NULL CHECK(metric IN ('prepared','sold','discarded','stock')),
                value   INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(date, hour, item_id, metric),
                FOREIGN KEY(item_id) REFERENCES items(item_id) ON DELETE RESTRICT
            )""")
            q.exec("CREATE INDEX IF NOT EXISTS idx_fhl_item_date ON fact_hourly_long(item_id, date)")
            _set_schema_version(db, 2); cur = 2

        # v3: 時間別 来客数（全体）
        if cur < 3:
            q.exec("""
            CREATE TABLE IF NOT EXISTS fact_hourly_customer(
                date TEXT NOT NULL,
                hour INTEGER NOT NULL,
                customer_count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(date, hour)
            )""")
            _set_schema_version(db, 3); cur = 3

        # v4: 日次サマリ（商品ごと）
        if cur < 4:
            q.exec("""
            CREATE TABLE IF NOT EXISTS fact_daily(
                date TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                prepared  INTEGER NOT NULL DEFAULT 0,
                sold      INTEGER NOT NULL DEFAULT 0,
                discarded INTEGER NOT NULL DEFAULT 0,
                stock_end INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(date, item_id),
                FOREIGN KEY(item_id) REFERENCES items(item_id) ON DELETE RESTRICT
            )""")
            q.exec("CREATE INDEX IF NOT EXISTS idx_fd_item_date ON fact_daily(item_id, date)")
            _set_schema_version(db, 4); cur = 4

        # v5: 日次サマリ（来客数・全体）
        if cur < 5:
            q.exec("""
            CREATE TABLE IF NOT EXISTS fact_daily_customer(
                date TEXT PRIMARY KEY,
                customer_count INTEGER NOT NULL DEFAULT 0
            )""")
            _set_schema_version(db, 5); cur = 5

        db.commit()
    except Exception as e:
        db.rollback()
        raise e

def _get_schema_version(db) -> int:
    q = QSqlQuery(db)
    q.exec("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'")
    if not q.next():  # 初回
        # バージョン管理用のテーブルを新規作成
        QSqlQuery(db).exec("CREATE TABLE schema_version(version INTEGER NOT NULL)")
        QSqlQuery(db).exec("INSERT INTO schema_version(version) VALUES(0)")
        return 0
    
    # すでにある場合は version の値を返す
    q.exec("SELECT version FROM schema_version LIMIT 1")
    return (q.next() and int(q.value(0))) or 0

def _set_schema_version(db, v: int):
    QSqlQuery(db).exec(f"UPDATE schema_version SET version={v}")

def _add_column_if_missing(db, table: str, column: str, typ: str, default=None):
    q = QSqlQuery(db)
    q.exec(f"PRAGMA table_info({table})")
    cols = set()
    while q.next():
        cols.add(q.value(1))
    if column in cols:
        return
    if default is None:
        QSqlQuery(db).exec(f"ALTER TABLE {table} ADD COLUMN {column} {typ}")
    else:
        QSqlQuery(db).exec(
            f"ALTER TABLE {table} ADD COLUMN {column} {typ} DEFAULT '{default}'"
        )

def _sqlite_supports_drop_column(db) -> bool:
    q = QSqlQuery(db)
    q.exec("SELECT sqlite_version()")
    q.next()
    ver = str(q.value(0))
    try:
        major, minor, patch = map(int, ver.split("."))
        return (major, minor, patch) >= (3, 35, 0)
    except Exception:
        return False

def _drop_column_compat(db, table: str, column: str):
    # 存在確認
    q = QSqlQuery(db)
    q.exec(f"PRAGMA table_info({table})")
    cols = []
    col_types = {}
    notnull = {}
    dflts = {}
    while q.next():
        name = q.value(1)
        cols.append(name)
        col_types[name] = q.value(2) or "TEXT"
        notnull[name] = bool(q.value(3))
        dflts[name] = q.value(4)

    if column not in cols:
        return

    if _sqlite_supports_drop_column(db):
        QSqlQuery(db).exec(f"ALTER TABLE {table} DROP COLUMN {column}")
        return

    keep = [c for c in cols if c != column]
    defs = []
    for c in keep:
        t = col_types.get(c, "TEXT")
        nn = " NOT NULL" if notnull.get(c, False) and c != "id" else ""
        dv = dflts.get(c)
        dv_sql = f" DEFAULT {dv}" if dv is not None else ""
        if c == "id":
            defs.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
        else:
            defs.append(f"{c} {t}{nn}{dv_sql}")
    create_sql = f"CREATE TABLE {table}_new({', '.join(defs)})"

    ok = QSqlQuery(db).exec(create_sql)
    if not ok:
        raise RuntimeError("failed to create temp table")

    ok = QSqlQuery(db).exec(
        f"INSERT INTO {table}_new({', '.join(keep)}) SELECT {', '.join(keep)} FROM {table}"
    )
    if not ok:
        raise RuntimeError("failed to copy data")

    ok = QSqlQuery(db).exec(f"DROP TABLE {table}")
    if not ok:
        raise RuntimeError("failed to drop old table")

    ok = QSqlQuery(db).exec(f"ALTER TABLE {table}_new RENAME TO {table}")
    if not ok:
        raise RuntimeError("failed to rename new table")

def _recreate_with_schema(db, table: str, columns: list[tuple[str, str]]):
    """
    指定した列定義のみを持つテーブルに“作り直す”。既存データは捨てる簡易版。
    columns: [("colname", "TYPE CONSTRAINTS"), ...]
    """
    from PySide6.QtSql import QSqlQuery
    q = QSqlQuery(db)

    # 古いテーブルがあればリネーム → 破棄
    q.exec(f"DROP TABLE IF EXISTS {table}_old")
    q.exec(f"ALTER TABLE {table} RENAME TO {table}_old")  # 失敗しても気にしない
    # 新テーブルを作成
    defs = ", ".join([f"{name} {decl}" for name, decl in columns])
    if not q.exec(f"CREATE TABLE {table}({defs})"):
        # 失敗時は元に戻す努力
        q.exec(f"DROP TABLE IF EXISTS {table}")
        q.exec(f"ALTER TABLE {table}_old RENAME TO {table}")
        raise RuntimeError("新スキーマ作成に失敗しました")

    # 旧テーブル破棄（存在すれば）
    q.exec(f"DROP TABLE IF EXISTS {table}_old")
