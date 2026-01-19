"""RFM Analyzer"""

from datetime import datetime
import pandas as pd
from logger import get_logger


class RFMAnalysisError(Exception):
    """Custom exception for RFM analysis errors."""


class RFMAnalyzer:
    """
    Computes Recency, Frequency and Monetary metrics per customer.
    """

    def __init__(self, df: pd.DataFrame, reference_date: datetime | None = None):
        self.df = df.copy()
        self.reference_date = reference_date or df["purchase_date"].max()
        self.logger = get_logger(__name__)

    def calculate_rfm(self) -> pd.DataFrame:
        """
        Calculate RFM metrics per customer.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
            ['customer_id', 'recency', 'frequency', 'monetary']
        """
        self.logger.info("Starting RFM calculation")

        try:
            rfm = (
                self.df.groupby("customer_id")
                .agg(
                    recency=(
                        "purchase_date",
                        lambda x: (self.reference_date - x.max()).days,
                    ),
                    frequency=("purchase_date", "count"),
                    monetary=("order_value", "sum"),
                )
                .reset_index()
            )

            self.logger.debug("RFM calculation completed successfully")
            return rfm

        except Exception as exc:
            error_msg = "Error calculating RFM metrics: %s"
            self.logger.error(error_msg, exc)
            raise RFMAnalysisError(error_msg % exc) from exc
