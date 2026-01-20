"""KPI Calculator Class"""

from typing import Dict, Any
import pandas as pd


class KPICalculationError(Exception):
    """Custom exception for incident KPI calculation errors."""


class KPICalculator:
    """
    Calculates operational KPIs from a cleaned incident DataFrame.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy()

    def calculate_all(self) -> Dict[str, Any]:
        """
        Calculate all incident KPIs.

        Returns
        -------
        Dict[str, Any]
            Dictionary with KPI results.
        """
        try:
            return {
                "total_tickets": self._total_tickets(),
                "open_tickets": self._open_tickets(),
                "closed_tickets": self._closed_tickets(),
                "backlog_percentage": self._backlog_percentage(),
                "avg_resolution_time": self._average_resolution_time(),
                "median_resolution_time": self._median_resolution_time(),
                "tickets_by_priority": self._tickets_by_priority(),
                "tickets_by_category": self._tickets_by_category(),
                "tickets_by_agent": self._tickets_by_agent(),
                "resolution_time_by_category": self._resolution_time_by_category(),
                "resolution_time_by_agent": self._resolution_time_by_agent(),
                "bottlenecks": self._detect_bottlenecks(),
                "sla_compliance_rate": self._calculate_sla_compliance(),
                "top_category": self._get_top_category(),
                "slowest_category": self._get_slowest_category(),
                "slowest_category_avg": self._get_slowest_category_avg(),
            }
        except Exception as exc:
            raise KPICalculationError(
                f"Error calculating incident KPIs: {exc}"
            ) from exc

    def _total_tickets(self) -> int:
        return int(len(self.df))

    def _open_tickets(self) -> int:
        return int(self.df["is_open"].sum())

    def _closed_tickets(self) -> int:
        return int(self.df["is_closed"].sum())

    def _backlog_percentage(self) -> float:
        if len(self.df) == 0:
            return 0.0
        return round((self._open_tickets() / len(self.df)) * 100, 2)

    def _average_resolution_time(self) -> float:
        """
        Average resolution time in hours (closed tickets only).
        """
        closed_df = self.df[self.df["is_closed"]]
        if closed_df.empty:
            return 0.0
        return round(closed_df["resolution_time_hours"].mean(), 2)

    def _median_resolution_time(self) -> float:
        """
        Median resolution time in hours (closed tickets only).
        """
        closed_df = self.df[self.df["is_closed"]]
        if closed_df.empty:
            return 0.0
        return round(closed_df["resolution_time_hours"].median(), 2)

    def _tickets_by_priority(self) -> pd.DataFrame:
        return (
            self.df.groupby("priority")
            .size()
            .reset_index(name="ticket_count")
            .sort_values("ticket_count", ascending=False)
        )

    def _tickets_by_category(self) -> pd.DataFrame:
        return (
            self.df.groupby("category")
            .size()
            .reset_index(name="ticket_count")
            .sort_values("ticket_count", ascending=False)
        )

    def _tickets_by_agent(self) -> pd.DataFrame:
        return (
            self.df.groupby("agent")
            .size()
            .reset_index(name="ticket_count")
            .sort_values("ticket_count", ascending=False)
        )

    def _resolution_time_by_category(self) -> pd.DataFrame:
        """
        Average resolution time by category (closed tickets only).
        """
        return (
            self.df[self.df["is_closed"]]
            .groupby("category")["resolution_time_hours"]
            .mean()
            .reset_index(name="avg_resolution_time_hours")
            .sort_values("avg_resolution_time_hours", ascending=False)
        )

    def _resolution_time_by_agent(self) -> pd.DataFrame:
        """
        Average resolution time by agent (closed tickets only).
        """
        return (
            self.df[self.df["is_closed"]]
            .groupby("agent")["resolution_time_hours"]
            .mean()
            .reset_index(name="avg_resolution_time_hours")
            .sort_values("avg_resolution_time_hours", ascending=False)
        )

    def _detect_bottlenecks(self) -> Dict[str, pd.DataFrame]:
        """
        Detect operational bottlenecks based on volume and resolution time.
        """
        bottlenecks = {}

        bottlenecks["categories"] = self._resolution_time_by_category().head(5)
        bottlenecks["agents"] = self._resolution_time_by_agent().head(5)

        return bottlenecks

    def _calculate_sla_compliance(self) -> float:
        """
        Calculate SLA compliance rate based on sla_hours column.
        """
        closed_df = self.df[self.df["is_closed"]]
        if closed_df.empty or "sla_hours" not in self.df.columns:
            return 0.0
        
        compliant = (closed_df["resolution_time_hours"] <= closed_df["sla_hours"]).sum()
        total = len(closed_df)
        
        if total == 0:
            return 0.0
        return round((compliant / total) * 100, 1)

    def _get_top_category(self) -> str:
        """
        Get the most frequent category.
        """
        category_counts = self.df["category"].value_counts()
        return category_counts.index[0] if not category_counts.empty else "N/A"

    def _get_slowest_category(self) -> str:
        """
        Get the category with highest average resolution time.
        """
        if "resolution_time_hours" not in self.df.columns:
            return "N/A"
        
        slowest = (
            self.df[self.df["is_closed"]]
            .groupby("category")["resolution_time_hours"]
            .mean()
            .sort_values(ascending=False)
        )
        return slowest.index[0] if not slowest.empty else "N/A"

    def _get_slowest_category_avg(self) -> float:
        """
        Get the average resolution time for the slowest category.
        """
        if "resolution_time_hours" not in self.df.columns:
            return 0.0
        
        slowest = (
            self.df[self.df["is_closed"]]
            .groupby("category")["resolution_time_hours"]
            .mean()
            .sort_values(ascending=False)
        )
        return round(slowest.iloc[0], 2) if not slowest.empty else 0.0