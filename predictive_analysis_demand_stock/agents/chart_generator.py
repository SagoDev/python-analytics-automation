"""
Chart generation module for demand and stock analysis.

Generates plots for:
- Historical demand
- Forecasted demand
- Stock-out risk
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


class ChartGeneratorError(Exception):
    """Custom exception for chart generator errors."""


class ChartGenerator:
    """
    Generates charts for demand analysis and stock risk.
    """

    def __init__(self, output_dir: str | Path = "output/charts") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_historical_demand(
        self,
        df: pd.DataFrame,
        product_col="product",
        date_col="date",
        sales_col="quantity_sold",
    ) -> dict:
        """
        Generate line charts of historical demand per product.

        Returns:
            dict of product -> path_to_chart
        """
        charts = {}
        for product, group in df.groupby(product_col):
            plt.figure(figsize=(10, 5))
            plt.plot(group[date_col], group[sales_col], marker="o")
            plt.title(f"Historical Demand: {product}")
            plt.xlabel("Date")
            plt.ylabel("Quantity Sold")
            plt.grid(True)

            file_path = self.output_dir / f"{product}_historical_demand.png"
            plt.savefig(file_path, bbox_inches="tight")
            plt.close()
            charts[product] = file_path

        return charts

    def plot_forecast(
        self,
        forecast_df: pd.DataFrame,
        product_col="product",
        forecast_col="forecast_demand",
    ) -> dict:
        """
        Generate line charts for forecasted demand.

        Returns:
            dict of product -> path_to_chart
        """
        charts = {}
        for product, group in forecast_df.groupby(product_col):
            plt.figure(figsize=(10, 5))
            plt.plot(
                group["forecast_period"],
                group[forecast_col],
                marker="o",
                color="orange",
            )
            plt.title(f"Forecasted Demand: {product}")
            plt.xlabel("Forecast Period")
            plt.ylabel("Predicted Quantity")
            plt.grid(True)

            file_path = self.output_dir / f"{product}_forecast.png"
            plt.savefig(file_path, bbox_inches="tight")
            plt.close()
            charts[product] = file_path

        return charts

    def plot_stock_risk(
        self,
        risk_df: pd.DataFrame,
        product_col="product",
        stock_col="current_stock",
        expected_col="expected_consumption",
    ) -> dict:
        """
        Generate bar charts showing stock vs expected consumption.

        Returns:
            dict of product -> path_to_chart
        """
        charts = {}
        for _, row in risk_df.iterrows():
            product = row[product_col]
            values = [row[stock_col], row[expected_col]]
            labels = ["Current Stock", "Expected Consumption"]

            plt.figure(figsize=(6, 4))
            plt.bar(labels, values, color=["green", "red"])
            plt.title(f"Stock vs Expected Demand: {product}")
            plt.ylabel("Quantity")
            plt.grid(axis="y")

            file_path = self.output_dir / f"{product}_stock_risk.png"
            plt.savefig(file_path, bbox_inches="tight")
            plt.close()
            charts[product] = file_path

        return charts
