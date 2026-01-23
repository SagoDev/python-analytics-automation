"""
Chart generation module for demand and stock analysis.

Generates plots for:
- Historical demand
- Forecasted demand
- Stock-out risk
"""

from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


class ChartGeneratorError(Exception):
    """Custom exception for chart generator errors."""


class ChartGenerator:
    """
    Generates charts for demand analysis and stock risk.
    """

    def __init__(self, output_dir: str | Path = "output/charts") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Color palette for products
        self.product_colors = {
            "Product_1": "#1f77b4",  # Blue
            "Product_2": "#ff7f0e",  # Orange
            "Product_3": "#2ca02c",  # Green
            "Product_4": "#d62728",  # Red
            "Product_5": "#9467bd",  # Purple
        }
        self.forecast_color = "#013220"  # Dark green

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

    def plot_individual_product_forecasts(
        self,
        clean_sales_df: pd.DataFrame,
        forecast_df: pd.DataFrame,
    ) -> dict:
        """
        Create individual charts for each product showing historical weeks + forecast.

        Returns:
            dict: {product_name: chart_path}
        """
        charts = {}

        # Prepare weekly sales data
        weekly_sales = clean_sales_df.copy()
        weekly_sales["iso_week"] = weekly_sales["date"].dt.isocalendar().week
        weekly_sales["iso_year"] = weekly_sales["date"].dt.isocalendar().year

        # Calculate weekly totals by product
        weekly_product = (
            weekly_sales.groupby(["iso_year", "iso_week", "product"])["quantity_sold"]
            .sum()
            .reset_index()
        )

        # Get forecast data
        forecast_product = forecast_df.copy()

        # Create chart for each product
        for product in weekly_product["product"].unique():
            # Get historical data for this product
            product_data = weekly_product[weekly_product["product"] == product]

            # Prepare weeks 1-4 (historical)
            historical_weeks = []
            historical_values = []

            for week_num in range(1, 5):  # Weeks 1-4
                week_data = product_data[product_data["iso_week"] == week_num]
                if not week_data.empty:
                    historical_weeks.append(f"Week {week_num}")
                    historical_values.append(week_data["quantity_sold"].sum())
                else:
                    historical_weeks.append(f"Week {week_num}")
                    historical_values.append(0)

            # Get forecast value for week 5
            forecast_value = 0
            if forecast_product is not None and len(forecast_product) > 0:
                product_forecast = forecast_product[
                    forecast_product["product"] == product
                ]
                if len(product_forecast) > 0:
                    forecast_value = product_forecast["forecast_demand"].sum()

            # Combine data
            weeks = historical_weeks + ["Week 5\n(Forecast)"]
            values = historical_values + [forecast_value]
            colors = [self.product_colors.get(product, "#1f77b4")] * 4 + [
                self.forecast_color
            ]

            # Create chart
            plt.figure(figsize=(8, 6))
            bars = plt.bar(
                weeks, values, color=colors, alpha=0.8, edgecolor="black", linewidth=1
            )

            # Add value labels on bars
            for bar, value in zip(bars, values):
                plt.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(values) * 0.02,
                    f"{int(value)}",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    fontsize=10,
                )

            # Add forecast label
            if forecast_value > 0:
                plt.text(
                    4,
                    forecast_value + max(values) * 0.05,
                    "FORECAST",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    color=self.forecast_color,
                    fontsize=9,
                )

            # Styling
            plt.title(
                f"Weekly Sales & Forecast - {product}", fontsize=14, fontweight="bold"
            )
            plt.xlabel("Week", fontsize=12)
            plt.ylabel("Units Sold", fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.ylim(0, max(values) * 1.2 if max(values) > 0 else 10)

            # Add legend
            import matplotlib.patches as mpatches

            historical_patch = mpatches.Patch(
                color=self.product_colors.get(product, "#1f77b4"),
                alpha=0.8,
                label="Historical",
            )
            forecast_patch = mpatches.Patch(
                color=self.forecast_color, alpha=0.8, label="Forecast"
            )
            plt.legend(
                handles=[historical_patch, forecast_patch],
                loc="upper right",
                framealpha=1,
            )

            # Save chart
            file_path = self.output_dir / f"{product}_weekly_forecast.png"
            plt.savefig(file_path, bbox_inches="tight", dpi=300)
            plt.close()

            charts[product] = file_path

        return charts

    def create_combined_product_pages(
        self,
        weekly_charts: dict,
        stock_charts: dict,
    ) -> dict:
        """
        Combine each product's weekly forecast chart with its stock risk chart.

        Returns:
            dict: {product_name: combined_chart_path}
        """
        combined_charts = {}

        for product in weekly_charts.keys():
            if product in stock_charts:
                # Load images
                weekly_img = Image.open(weekly_charts[product])
                stock_img = Image.open(stock_charts[product])

                # Resize images if needed
                weekly_width, weekly_height = weekly_img.size
                stock_width, stock_height = stock_img.size

                # Create new image (weekly on top, stock on bottom)
                combined_width = max(weekly_width, stock_width)
                combined_height = weekly_height + stock_height + 20  # 20px gap

                combined_img = Image.new(
                    "RGB", (combined_width, combined_height), "white"
                )

                # Paste weekly chart (top)
                combined_img.paste(weekly_img, (0, 0))

                # Paste stock chart (bottom, centered horizontally if needed)
                stock_x = (combined_width - stock_width) // 2
                combined_img.paste(stock_img, (stock_x, weekly_height + 20))

                # Save combined chart
                combined_path = self.output_dir / f"{product}_combined.png"
                combined_img.save(combined_path, dpi=(300, 300))
                combined_charts[product] = combined_path

        return combined_charts

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
