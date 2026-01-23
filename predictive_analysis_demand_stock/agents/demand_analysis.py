"""Demand analyisis class"""

import pandas as pd


class DemandAnalysisError(Exception):
    """Custom exception for demand analysis errors."""


class DemandAnalysis:
    """
    Performs historical demand analysis per product.
    """

    def __init__(self, sales_df: pd.DataFrame) -> None:
        self.df = sales_df.copy()

        if not {"product", "date", "quantity_sold"}.issubset(self.df.columns):
            raise DemandAnalysisError(
                "DataFrame must contain 'product', 'date', and 'quantity_sold' columns"
            )

    def average_demand(self) -> pd.DataFrame:
        """
        Calculate average demand per product.
        """
        return (
            self.df.groupby("product")["quantity_sold"]
            .mean()
            .reset_index(name="avg_demand")
        )

    def demand_variability(self) -> pd.DataFrame:
        """
        Calculate demand variability metrics per product.
        """
        variability = (
            self.df.groupby("product")["quantity_sold"]
            .agg(["mean", "std"])
            .reset_index()
        )

        variability["cv"] = variability["std"] / variability["mean"]

        return variability.rename(
            columns={
                "mean": "avg_demand",
                "std": "std_demand",
            }
        )

    def seasonality_by_month(self) -> pd.DataFrame:
        """
        Analyze monthly seasonality per product.
        """
        df = self.df.copy()
        df["month"] = df["date"].dt.month

        return (
            df.groupby(["product", "month"])["quantity_sold"]
            .mean()
            .reset_index(name="avg_monthly_demand")
        )

    def seasonality_by_weekday(self) -> pd.DataFrame:
        """
        Analyze weekday seasonality per product.
        """
        df = self.df.copy()
        df["weekday"] = df["date"].dt.dayofweek

        return (
            df.groupby(["product", "weekday"])["quantity_sold"]
            .mean()
            .reset_index(name="avg_weekday_demand")
        )
