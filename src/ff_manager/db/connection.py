# db/connection.py
from PySide6.QtSql import QSqlDatabase,QSqlQuery

def get_db(db_path: str) -> QSqlDatabase:
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(db_path)
    if not db.open():
        raise RuntimeError("データベースを開けませんでした。")

    # SQLiteの外部キー制約を有効化（必ず最初に一回）
    QSqlQuery(db).exec("PRAGMA foreign_keys=ON")
    return db