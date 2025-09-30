# src/ff_manager/db/repositories/metrics_repo.py
from __future__ import annotations
from typing import Dict
from PySide6.QtSql import QSqlQuery

from ff_manager.core.constants import (
    HOURS,ITEM_METRICS,ITEM_LABELS_JA,ITEM_ROW,SUMMARY_ROWS,SUMMARY_ROW,SUMMARY_LABELS_JA
    )

class MetricsRepository:
    def __init__(self, db):
        self.db = db

    # ---------- 商品×時間メトリクス ----------
    def fetch_item_metrics(self, date_iso: str, item_id: int) -> Dict[str, Dict[int, int]]:
        """
        商品ごとの時間別メトリクスを取得する。

        Args:
            date_iso (str): 'YYYY-MM-DD' 形式の日付
            item_id (int): 対象商品のID

        Returns:
            Dict[str, Dict[int, int]]: 例 {"sold": {9: 12, 10: 5}, "discarded": {9: 1}}
        """
        q = QSqlQuery(self.db)
        q.prepare("""
            SELECT metric, hour, value
            FROM fact_hourly_long
            WHERE date=:d AND item_id=:it
        """)
        q.bindValue(":d", date_iso)
        q.bindValue(":it", item_id)
        q.exec()
        # 返却フォーマットを保証
        out: Dict[str, Dict[int, int]] = {m:{} for m in ITEM_METRICS}
        while q.next():
            m = str(q.value(0))
            h = int(q.value(1))
            v = int(q.value(2))

            if m not in ITEM_METRICS:
                raise ValueError(f"Unknown metric '{m}' in DB for item {item_id}")

            out[m][h]=v
        return out

    def upsert_item_metrics(self, date_iso: str, item_id: int, data: Dict[str, Dict[int, int]]) -> None:
        """
        商品の時間ごとの値を INSERT/UPDATE (UPSERT) する

        Args:
            date_iso (str): 'YYYY-MM-DD' 形式の日付
            item_id (int): 対象商品のID
            data (Dict[str, Dict[int, int]]):商品の時間別メトリクス
        """
        q = QSqlQuery(self.db)
        q.prepare("""
            INSERT INTO fact_hourly_long(date,hour,item_id,metric,value)
            VALUES(:d,:h,:it,:m,:v)
            ON CONFLICT(date,hour,item_id,metric) DO UPDATE SET value=excluded.value
        """)
        for m, by_hour in data.items():
            for h, v in by_hour.items():
                q.bindValue(":d", date_iso)
                q.bindValue(":h", h)
                q.bindValue(":it", item_id)
                q.bindValue(":m", m)
                q.bindValue(":v", v)
                if not q.exec():
                    raise RuntimeError(q.lastError().text())

    # ---------- 客数（時間別/日別） ----------
    def fetch_hourly_customers(self, date_iso: str) -> Dict[int, int]:
        """
        時間別の客数を取得する

        Args:
            date_iso (str): 'YYYY-MM-DD' 形式の日付

        Returns:
            Dict[int, int]: 例 {9: 12, 10: 5}
        """
        q = QSqlQuery(self.db)
        q.prepare("""SELECT hour, customer_count FROM fact_hourly_customer WHERE date=:d""")
        q.bindValue(":d", date_iso)
        q.exec()
        out: Dict[int, int] = {}
        while q.next():
            out[int(q.value(0))] = int(q.value(1))
        return out

    def upsert_hourly_customers(self, date_iso: str, by_hour: Dict[int, int]) -> None:
        """
        時間別の客数をINSERT/UPDATE (UPSERT)する

        Args:
            date_iso (str): 'YYYY-MM-DD' 形式の日付
            by_hour (Dict[int,int]):時間別客数データ 例{9: 12, 10: 5}
        """
        q = QSqlQuery(self.db)
        q.prepare("""
            INSERT INTO fact_hourly_customer(date,hour,customer_count)
            VALUES(:d,:h,:c)
            ON CONFLICT(date,hour) DO UPDATE SET customer_count=excluded.customer_count
        """)
        for h, c in by_hour.items():
            q.bindValue(":d", date_iso)
            q.bindValue(":h", h)
            q.bindValue(":c", c)
            if not q.exec():
                raise RuntimeError(q.lastError().text())

    def upsert_daily_customer_from_hourly(self, date_iso: str) -> None:
        """
        1日の合計客数を再計算してINSERT/UPDATE (UPSERT)する

        Args:
            date_iso (str): 'YYYY-MM-DD' 形式の日付
        """
        q = QSqlQuery(self.db)
        q.prepare("""
            INSERT INTO fact_daily_customer(date, customer_count)
            VALUES(:d, (SELECT COALESCE(SUM(customer_count),0) FROM fact_hourly_customer WHERE date=:d))
            ON CONFLICT(date) DO UPDATE SET customer_count=excluded.customer_count
        """)
        q.bindValue(":d", date_iso)
        if not q.exec():
            raise RuntimeError(q.lastError().text())

    # ---------- 全商品合計（サマリ） ----------
    def fetch_summary_metrics(self, date_iso: str) -> Dict[str, Dict[int, int]]:
        """
        その日付の全商品を合算した値を取得

        Args:
            date_iso (str): 'YYYY-MM-DD' 形式の日付
        returns:
            Dict[str,Dict[int,int]]:例 {"sold": {9: 12, 10: 5}, "discarded": {9: 1}}
        """
        q = QSqlQuery(self.db)
        q.prepare("""
            SELECT metric, hour, SUM(value) as total_value
            FROM fact_hourly_long
            WHERE date=:d
            GROUP BY metric, hour
        """)
        q.bindValue(":d", date_iso)
        q.exec()
        out: Dict[str, Dict[int, int]] = {}
        while q.next():
            m = str(q.value(0)); h = int(q.value(1)); v = int(q.value(2))
            out.setdefault(m, {})[h] = v
        return out
