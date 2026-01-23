"""
Stock risk analysis module.

Detects products at risk of stock-out based on forecasted demand and current stock levels.
"""

import pandas as pd


class StockRiskError(Exception):
    """Custom exception for stock risk errors."""


class StockRisk:
    """
    Analyzes risk of stock-out for products.
    """

    def __init__(self, forecast_df: pd.DataFrame, stock_df: pd.DataFrame) -> None:
        """
        Initialize the stock risk analyzer.

        Args:
            forecast_df: DataFrame with columns ['product', 'forecast_period', 'forecast_demand']
            stock_df: DataFrame with columns ['product', 'current_stock', 'lead_time_days']
        """
        self.forecast_df = forecast_df.copy()
        self.stock_df = stock_df.copy()

        required_forecast_cols = {"product", "forecast_period", "forecast_demand"}
        required_stock_cols = {"product", "current_stock", "lead_time_days"}

        if not required_forecast_cols.issubset(self.forecast_df.columns):
            raise StockRiskError(
                f"Forecast DataFrame must contain columns {required_forecast_cols}"
            )
        if not required_stock_cols.issubset(self.stock_df.columns):
            raise StockRiskError(
                f"Stock DataFrame must contain columns {required_stock_cols}"
            )

    def analyze(self) -> pd.DataFrame:
        """
        Calculate stock-out risk per product.

        Returns:
            DataFrame with columns:
            ['product', 'expected_consumption', 'current_stock', 'stock_out_risk', 'shortage_qty']
        """
        # Aggregate forecasted demand for the lead time
        df = self.forecast_df.merge(self.stock_df, on="product", how="left")

        # Expected consumption = forecast_demand * lead_time_days
        df["expected_consumption"] = df["forecast_demand"] * df["lead_time_days"]

        # Determine stock-out risk
        df["stock_out_risk"] = df["current_stock"] < df["expected_consumption"]

        # Calculate quantity shortage if any
        df["shortage_qty"] = df["expected_consumption"] - df["current_stock"]
        df["shortage_qty"] = df["shortage_qty"].apply(lambda x: max(x, 0))

        # Keep relevant columns and aggregate per product
        result = (
            df.groupby("product")[
                [
                    "expected_consumption",
                    "current_stock",
                    "stock_out_risk",
                    "shortage_qty",
                ]
            ]
            .sum()
            .reset_index()
        )

        return result
