# src/ff_manager/db/repositories/ocr_repo.py
import hashlib,time,json
from typing import Optional
from PySide6.QtSql import QSqlQuery

DDL = """
CREATE TABLE IF NOT EXISTS ocr_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path TEXT UNIQUE,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

class OCRCacheRepo:
    def __init__(self, db):
        """OCRキャッシュ用のリポジトリ"""
        self.db = db
        self._ensure_table()

    def _ensure_table(self):
        """キャッシュ用テーブルがなければ作成"""
        q = QSqlQuery(self.db)
        if not q.exec(DDL):
            print("Failed to create table:", q.lastError().text())

    def save_result(self, image_path: str, result: str) -> bool:
        """
        OCR結果をキャッシュに保存（既存なら更新）
        """
        q = QSqlQuery(self.db)
        q.prepare("""
            INSERT OR REPLACE INTO ocr_cache (image_path, result)
            VALUES (:path, :res)
        """)
        q.bindValue(":path", image_path)
        q.bindValue(":res", result)
        ok = q.exec()
        if not ok:
            print("DB save error:", q.lastError().text())
        return ok

    def load_result(self, image_path: str) -> str | None:
        """
        キャッシュからOCR結果を取得
        """
        q = QSqlQuery(self.db)
        q.prepare("SELECT result FROM ocr_cache WHERE image_path=:path")
        q.bindValue(":path", image_path)
        if not q.exec():
            print("DB load error:", q.lastError().text())
            return None

        if q.next():
            return str(q.value(0))
        return None

    @staticmethod
    def build_key(image_bytes: bytes, params: dict) -> str:
        h = hashlib.sha1()
        h.update(image_bytes)
        h.update(json.dumps(params, sort_keys=True).encode("utf-8"))
        return h.hexdigest()

    def get(self, key: str) -> Optional[str]:
        q = QSqlQuery(self.db)
        q.prepare("SELECT result_json FROM ocr_cache WHERE cache_key = :k")
        q.bindValue(":k", key)
        if q.exec() and q.next():
            return str(q.value(0))
        return None
    
    def put(self, key: str, params: dict, result_json: str) -> None:
        q = QSqlQuery(self.db)
        q.prepare("""
            INSERT OR REPLACE INTO ocr_cache (cache_key, created_at, params, result_json)
            VALUES (:k, :t, :p, :r)
        """)
        q.bindValue(":k", key)
        q.bindValue(":t", int(time.time()))
        q.bindValue(":p", json.dumps(params, ensure_ascii=False))
        q.bindValue(":r", result_json)
        q.exec()
