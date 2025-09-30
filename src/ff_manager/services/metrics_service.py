# services/metrics_service.py
from typing import Dict
from PySide6.QtWidgets import QTableWidget
from ff_manager.db.repositories.metrics_repo import MetricsRepository
from ff_manager.db.repositories.items_repo import ItemsRepository
from ff_manager.core.constants import HOURS, ITEM_ROW, SUMMARY_ROW


class MetricsService:
    def __init__(self, db):
        self.db = db
        self.repo_items=ItemsRepository(db)
        self.repo = MetricsRepository(db)

    # ---------- 読み込み ----------
    def load(self, date_iso: str, item_id: int) -> Dict[str, Dict[str, Dict[int, int]]]:
        """
        指定日付・商品IDのメトリクスをまとめて取得する

        Args:
            date_iso (str): 'YYYY-MM-DD' 形式の日付
            item_id (int): 対象商品のID
        Returns:
            {
                "item": {metric: {hour: value}},
                "customers": {hour: value},
                "summary": {metric: {hour: total}}
            }
        """
        item_data = self.repo.fetch_item_metrics(date_iso, item_id)
        cust_data = self.repo.fetch_hourly_customers(date_iso)
        summary_data = self.repo.fetch_summary_metrics(date_iso)

        return {
            "item": item_data,
            "customers": cust_data,
            "summary": summary_data,
        }
    
    def fetch_summary(self, date_iso: str) -> dict:
        """
        サマリ用のデータをまとめて返す

        Returns:
            {
                "customers": {hour: value},
                "summary": {metric: {hour: total}}
            }
        """
        cust_data = self.repo.fetch_hourly_customers(date_iso)
        summary_data = self.repo.fetch_summary_metrics(date_iso)
        return {"customers": cust_data, "summary": summary_data}

    def load_item_metrics(self, date_iso: str, item_id: int) -> Dict[str, Dict[int, int]]:
        return self.repo.fetch_item_metrics(date_iso, item_id)

    def load_hourly_customers(self, date_iso: str) -> Dict[int, int]:
        return self.repo.fetch_hourly_customers(date_iso)

    def load_summary_metrics(self, date_iso: str) -> Dict[str, Dict[int, int]]:
        return self.repo.fetch_summary_metrics(date_iso)

    # ---------- 保存 ----------
    def save(self, date_iso: str, item_id: int, item_table: QTableWidget, summary_table: QTableWidget):
        """トランザクション内で商品・客数・日次サマリを保存"""
        self.db.transaction()
        try:
            # 商品メトリクス
            item_data = self._extract_table_data(item_table, ITEM_ROW)
            self.repo.upsert_item_metrics(date_iso, item_id, item_data)

            # 客数
            cust_row = SUMMARY_ROW["customer"]
            cust_by_hour = {
                h: int(summary_table.item(cust_row, h).text() or 0)
                for h in range(len(HOURS))
            }
            self.repo.upsert_hourly_customers(date_iso, cust_by_hour)

            # 日次サマリ
            self.repo.upsert_daily_customer_from_hourly(date_iso)

            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def _extract_table_data(self, table, row_map: dict) -> dict:
        """
        QTableWidget の内容を dict に変換する共通関数

        Args:
            table (QTableWidget): 対象のテーブル
            row_map (dict): metric -> row index の対応

        Returns:
            dict: {metric: {hour: value}}
        """
        data = {}
        for m, r in row_map.items():
            by_hour = {}
            for h in range(24):  # 合計列は無視
                text = table.item(r, h).text() or "0"
                by_hour[h] = int(text)
            data[m] = by_hour
        return data


    def get_item_id_by_name(self, name: str) -> int | None:
        """商品名から item_id を取得"""
        return self.repo_items.get_item_id_by_name(name)
    
    def fetch_item_names(self) -> list[str]:
        """商品名一覧を取得"""
        return self.repo_items.list_item_names()
    
    