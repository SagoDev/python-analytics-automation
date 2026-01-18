"""Chart Generator Class"""

from pathlib import Path
from typing import Dict, Any
import matplotlib.pyplot as plt
import pandas as pd
from logger import get_logger


class ChartGenerationError(Exception):
    """Custom exception for chart generation errors."""


class ChartsGenerator:
    """
    Generates charts from KPI results and saves them as image files.
    """

    def __init__(self, output_dir: str | Path = "output/charts") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(__name__)

    def generate_all(self, kpis: Dict[str, Any]) -> Dict[str, Path]:
        """
        Generate all charts based on provided KPIs.

        Returns
        -------
        Dict[str, Path]
            Dictionary mapping chart names to their file paths.
        """
        self.logger.info("Starting chart generation")
        try:
            charts = {
                "sales_by_month": self._sales_by_month_chart(kpis["sales_by_month"]),
                "sales_by_product": self._sales_by_product_chart(
                    kpis["sales_by_product"]
                ),
                "sales_by_category": self._sales_by_category_chart(
                    kpis["sales_by_category"]
                ),
            }

            for chart_name, chart_path in charts.items():
                self.logger.debug("Generated chart: %s -> %s", chart_name, chart_path)

            self.logger.info("Successfully generated %d charts", len(charts))
            return charts
        except Exception as exc:
            error_msg = "Error generating charts: %s"
            self.logger.error(error_msg, exc)
            raise ChartGenerationError(error_msg % exc) from exc

    def _sales_by_month_chart(self, df: pd.DataFrame) -> Path:
        """
        Line chart of sales evolution by month.
        """
        self.logger.debug("Creating sales by month chart")
        file_path = self.output_dir / "sales_by_month.png"

        plt.figure(figsize=(8, 5))
        plt.plot(df["month"], df["total_sales"], marker="o")
        plt.title("Sales by Month")
        plt.xlabel("Month")
        plt.ylabel("Total Sales")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()

        self.logger.debug("Sales by month chart saved: %s", file_path)
        return file_path

    def _sales_by_product_chart(self, df: pd.DataFrame) -> Path:
        """
        Bar chart of sales by product (Top 10).
        """
        self.logger.debug("Creating sales by product chart")
        file_path = self.output_dir / "sales_by_product.png"

        top_df = df.head(10)

        plt.figure(figsize=(8, 5))
        plt.bar(top_df["product"], top_df["total_sales"])
        plt.title("Top 10 Products by Sales")
        plt.xlabel("Product")
        plt.ylabel("Total Sales")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()

        self.logger.debug("Sales by product chart saved: %s", file_path)
        return file_path

    def _sales_by_category_chart(self, df: pd.DataFrame) -> Path:
        """
        Bar chart of sales by category.
        """
        self.logger.debug("Creating sales by category chart")
        file_path = self.output_dir / "sales_by_category.png"

        plt.figure(figsize=(8, 5))
        plt.bar(df["category"], df["total_sales"])
        plt.title("Sales by Category")
        plt.xlabel("Category")
        plt.ylabel("Total Sales")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()

        self.logger.debug("Sales by category chart saved: %s", file_path)
        return file_path
