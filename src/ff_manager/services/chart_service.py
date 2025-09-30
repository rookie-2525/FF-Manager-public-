# services/chart_service.py
from ff_manager.services.metrics_service import MetricsService

class ChartService:
    def __init__(self, db):
        self.metrics_service = MetricsService(db)

    def get_metric_timeseries(
        self,
        date_range: tuple[str, str],
        metric: str,
        item_id: int | None = None
    ) -> dict[str, dict[int, int]]:
        """
        Args:
            date_range: (start_date, end_date) "YYYY-MM-DD" 形式
            metric: "prepared", "sold", "discarded", "stock", "customer"
            item_id: Noneなら全商品合計

        Returns:
            {date: {hour: value}}
        """
        result = {}

        # TODO: 実際は date_range 全体をループして取得
        d = date_range[0]  # まず1日分だけ
        if item_id:
            metrics = self.metrics_service.load_item_metrics(d, item_id)
            result[d] = metrics.get(metric, {})
        else:
            metrics = self.metrics_service.load_summary_metrics(d)
            result[d] = metrics.get(metric, {})

        return result
