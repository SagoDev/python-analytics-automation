"""KPI Calculator Class"""

from typing import Dict, Any
import pandas as pd
from logger import get_logger


class KPICalculationError(Exception):
    """Custom exception for KPI calculation errors."""


class KPICalculator:
    """
    Calculates business KPIs from a cleaned sales DataFrame.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy()
        self.logger = get_logger(__name__)

    def calculate_all(self) -> Dict[str, Any]:
        """
        Calculate all KPIs and return them in a structured dictionary.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing all KPI results.
        """
        self.logger.info("Starting KPI calculations")
        try:
            kpis = {
                "total_sales": self._total_sales(),
                "total_transactions": self._total_transactions(),
                "average_ticket": self._average_ticket(),
                "top_product": self._top_product(),
                "top_category": self._top_category(),
                "top_seller": self._top_seller(),
                "sales_by_month": self._sales_by_month(),
                "sales_by_product": self._sales_by_product(),
                "sales_by_category": self._sales_by_category(),
            }

            self.logger.debug("All KPIs calculated successfully")
            return kpis
        except Exception as exc:
            error_msg = "Error calculating KPIs: %s"
            self.logger.error(error_msg, exc)
            raise KPICalculationError(error_msg % exc) from exc

    def _total_sales(self) -> float:
        """Total amount of sales."""
        return float(self.df["total"].sum())

    def _total_transactions(self) -> int:
        """Total number of transactions."""
        return int(len(self.df))

    def _average_ticket(self) -> float:
        """Average sale value per transaction."""
        if len(self.df) == 0:
            return 0.0
        return float(self.df["total"].mean())

    def _top_product(self) -> pd.Series:
        """
        Product with highest total sales.

        Returns
        -------
        pd.Series
            Index: product
            Value: total sales
        """
        return (
            self.df.groupby("product")["total"]
            .sum()
            .sort_values(ascending=False)
            .head(1)
        )

    def _top_category(self) -> pd.Series:
        """
        Category with highest total sales.
        """
        return (
            self.df.groupby("category")["total"]
            .sum()
            .sort_values(ascending=False)
            .head(1)
        )

    def _top_seller(self) -> pd.Series:
        """
        Seller with highest total sales.
        """
        return (
            self.df.groupby("seller")["total"]
            .sum()
            .sort_values(ascending=False)
            .head(1)
        )

    def _sales_by_month(self) -> pd.DataFrame:
        """
        Sales aggregated by month.

        Returns
        -------
        pd.DataFrame
            Columns: ['month', 'total_sales']
        """
        df = self.df.copy()
        df["month"] = df["date"].dt.to_period("M").astype(str)

        result = (
            df.groupby("month")["total"]
            .sum()
            .reset_index()
            .rename(columns={"total": "total_sales"})
            .sort_values("month")
        )
        return result

    def _sales_by_product(self) -> pd.DataFrame:
        """
        Sales aggregated by product.
        """
        return (
            self.df.groupby("product")["total"]
            .sum()
            .reset_index()
            .rename(columns={"total": "total_sales"})
            .sort_values("total_sales", ascending=False)
        )

    def _sales_by_category(self) -> pd.DataFrame:
        """
        Sales aggregated by category.
        """
        return (
            self.df.groupby("category")["total"]
            .sum()
            .reset_index()
            .rename(columns={"total": "total_sales"})
            .sort_values("total_sales", ascending=False)
        )
