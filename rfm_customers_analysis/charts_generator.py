"""Chart Generator Class"""

from pathlib import Path
from typing import Any, Dict
import matplotlib.pyplot as plt
import pandas as pd
from logger import get_logger


class ChartGenerationError(Exception):
    """Custom exception for chart generation errors."""


class ChartsGenerator:
    """
    Generates charts for RFM customer analysis based on precomputed KPIs.
    """

    def __init__(self, output_dir: str | Path = "output/charts") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(__name__)

    def generate_charts(self, kpis: Dict[str, Any]) -> Dict[str, Path]:
        """Generate Charts"""
        self.logger.info("Starting RFM chart generation")

        try:
            charts = {}

            if "customers_by_segment" in kpis:
                charts["customers_by_segment"] = self._customers_by_segment(
                    kpis["customers_by_segment"]
                )

            if "customers_by_churn_risk" in kpis:
                charts["customers_by_churn_risk"] = self._customers_by_churn_risk(
                    kpis["customers_by_churn_risk"]
                )

            if "recency_vs_frequency" in kpis:
                charts["recency_vs_frequency"] = self._recency_vs_frequency(
                    kpis["recency_vs_frequency"]
                )

            if "monetary_by_segment" in kpis:
                charts["monetary_by_segment"] = self._monetary_by_segment(
                    kpis["monetary_by_segment"]
                )

            self.logger.info("Successfully generated %d charts", len(charts))
            return charts

        except Exception as exc:
            self.logger.error("Error generating charts: %s", exc)
            raise ChartGenerationError(str(exc)) from exc

    def _customers_by_segment(self, df: pd.DataFrame) -> Path:
        path = self.output_dir / "customers_by_segment.png"

        plt.figure(figsize=(8, 5))
        plt.bar(df["rfm_segment"], df["customers"])
        plt.title("Customers by RFM Segment")
        plt.xlabel("Segment")
        plt.ylabel("Number of Customers")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(path)
        plt.close()

        return path

    def _customers_by_churn_risk(self, series: pd.Series) -> Path:
        path = self.output_dir / "customers_by_churn_risk.png"

        plt.figure(figsize=(6, 4))
        plt.bar(series.index.astype(str), series.values)
        plt.title("Customers by Churn Risk")
        plt.xlabel("Churn Risk")
        plt.ylabel("Number of Customers")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()

        return path

    def _recency_vs_frequency(self, df: pd.DataFrame) -> Path:
        path = self.output_dir / "recency_vs_frequency.png"

        plt.figure(figsize=(8, 6))
        plt.scatter(df["recency"], df["frequency"], alpha=0.6)
        plt.title("Recency vs Frequency")
        plt.xlabel("Recency (days)")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()

        return path

    def _monetary_by_segment(self, df: pd.DataFrame) -> Path:
        path = self.output_dir / "monetary_by_segment.png"

        plt.figure(figsize=(8, 5))
        plt.bar(df["rfm_segment"], df["monetary"])
        plt.title("Total Monetary Value by Segment")
        plt.xlabel("Segment")
        plt.ylabel("Total Monetary Value")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(path)
        plt.close()

        return path
