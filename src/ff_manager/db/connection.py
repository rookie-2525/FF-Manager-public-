# db/connection.py
import sqlite3
from PySide6.QtSql import QSqlDatabase,QSqlQuery
from ff_manager.config import DB_PATH
from pathlib import Path


def get_db(db_path: str) -> QSqlDatabase:
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(db_path)
    if not db.open():
        raise RuntimeError("データベースを開けませんでした。")

    # SQLiteの外部キー制約を有効化（必ず最初に一回）
    QSqlQuery(db).exec("PRAGMA foreign_keys=ON")
    return db


def get_sqlite_connection(db_path: str | None = None) -> sqlite3.Connection:
    """
    SQLiteの接続を返す。存在しない場合は新規作成。

    Args:
        db_path (str | None): データベースファイルパス（Noneなら config.DB_PATH）

    Returns:
        sqlite3.Connection
    """
    path = Path(db_path or DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row  # カラム名でアクセス可能に
    return conn