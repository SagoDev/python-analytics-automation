"""KPI Calculator Class"""

from typing import Dict, Any
import pandas as pd
from logger import get_logger


class KPICalculationError(Exception):
    """Custom exception for KPI calculation errors."""


class KPICalculator:
    """
    Calculates RFM-based customer KPIs from a cleaned customer transactions DataFrame.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy()
        self.logger = get_logger(__name__)

    def calculate_all(self) -> Dict[str, Any]:
        """
        Calculate all RFM KPIs and return them in a structured dictionary.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing all KPI results.
        """
        self.logger.info("Starting RFM KPI calculations")
        try:
            kpis = {
                "total_customers": self._total_customers(),
                "active_customers": self._active_customers(),
                "churn_risk_customers": self._churn_risk_customers(),
                "avg_recency": self._avg_recency(),
                "avg_frequency": self._avg_frequency(),
                "avg_monetary": self._avg_monetary(),
                "top_segment": self._top_segment(),
                "most_valuable_customer": self._most_valuable_customer(),
                "customers_by_segment": self._customers_by_segment(),
                "customers_by_churn_risk": self._customers_by_churn_risk(),
                "recency_vs_frequency": self._recency_vs_frequency(),
                "monetary_by_segment": self._monetary_by_segment(),
            }

            self.logger.debug("All RFM KPIs calculated successfully")
            return kpis

        except Exception as exc:
            error_msg = "Error calculating RFM KPIs: %s"
            self.logger.error(error_msg, exc)
            raise KPICalculationError(error_msg % exc) from exc

    def _total_customers(self) -> int:
        """Total number of unique customers."""
        return int(self.df["customer_id"].nunique())

    def _active_customers(self) -> int:
        """
        Customers considered active.
        Assumes recency in days and threshold <= 90 days.
        """
        return int(self.df[self.df["recency"] <= 90]["customer_id"].nunique())

    def _churn_risk_customers(self) -> int:
        """
        Customers at risk of churn.
        Assumes recency > 180 days.
        """
        return int(self.df[self.df["recency"] > 180]["customer_id"].nunique())

    def _avg_recency(self) -> float:
        """Average recency in days."""
        return float(self.df["recency"].mean())

    def _avg_frequency(self) -> float:
        """Average purchase frequency per customer."""
        return float(self.df["frequency"].mean())

    def _avg_monetary(self) -> float:
        """Average monetary value per customer."""
        return float(self.df["monetary"].mean())

    def _top_segment(self) -> pd.Series:
        """
        Segment with the largest number of customers.

        Returns
        -------
        pd.Series
            Index: segment
            Value: number of customers
        """
        if "rfm_segment" not in self.df.columns:
            return pd.Series(dtype=int)

        return (
            self.df.groupby("rfm_segment")["customer_id"]
            .nunique()
            .sort_values(ascending=False)
            .head(1)
        )

    def _most_valuable_customer(self) -> pd.Series:
        """
        Customer with highest monetary value.

        Returns
        -------
        pd.Series
            Index: customer_id
            Value: monetary value
        """
        return (
            self.df.groupby("customer_id")["monetary"]
            .max()
            .sort_values(ascending=False)
            .head(1)
        )

    def _customers_by_segment(self) -> pd.DataFrame:
        """
        Number of customers per RFM segment.

        Returns
        -------
        pd.DataFrame
            Columns: ['rfm_segment', 'customers']
        """
        if "rfm_segment" not in self.df.columns:
            return pd.DataFrame(columns=["rfm_segment", "customers"])

        return (
            self.df.groupby("rfm_segment")["customer_id"]
            .nunique()
            .reset_index()
            .rename(columns={"customer_id": "customers"})
            .sort_values("customers", ascending=False)
        )

    def _customers_by_churn_risk(self) -> pd.Series:
        """
        Number of customers by churn risk level.

        Returns
        -------
        pd.Series
            Index: churn risk level
            Value: number of customers
        """
        # Define churn risk based on recency
        risk_levels = pd.cut(
            self.df["recency"],
            bins=[0, 30, 90, 180, float('inf')],
            labels=["Low Risk", "Medium Risk", "High Risk", "Very High Risk"]
        )
        
        return self.df.groupby(risk_levels)["customer_id"].nunique()

    def _recency_vs_frequency(self) -> pd.DataFrame:
        """
        Recency vs Frequency data for scatter plot.

        Returns
        -------
        pd.DataFrame
            Columns: ['recency', 'frequency']
        """
        return self.df[["recency", "frequency"]].copy()

    def _monetary_by_segment(self) -> pd.DataFrame:
        """
        Total monetary value by RFM segment.

        Returns
        -------
        pd.DataFrame
            Columns: ['rfm_segment', 'monetary']
        """
        if "rfm_segment" not in self.df.columns:
            return pd.DataFrame(columns=["rfm_segment", "monetary"])

        return (
            self.df.groupby("rfm_segment")["monetary"]
            .sum()
            .reset_index()
            .sort_values("monetary", ascending=False)
        )