"""Data Cleaner Class"""

import pandas as pd


class DataCleaningError(Exception):
    """Custom exception for data cleaning errors."""


class DataCleaner:
    """
    Cleans and prepares historical sales data for demand analysis
    and forecasting.
    """

    def __init__(self, sales_df: pd.DataFrame) -> None:
        self.df = sales_df.copy()

    def clean(self, frequency: str = "D") -> pd.DataFrame:
        """
        Execute full data cleaning and aggregation pipeline.

        Parameters
        ----------
        frequency : str
            Aggregation frequency:
            - 'D' = daily
            - 'W' = weekly
            - 'M' = monthly

        Returns
        -------
        pd.DataFrame
            Cleaned and aggregated DataFrame.
        """
        self._convert_date()
        self._convert_quantity()
        self._drop_invalid_rows()
        self._aggregate_by_frequency(frequency)
        self._sort_data()

        return self.df

    def _convert_date(self) -> None:
        """Convert date column to datetime."""
        try:
            self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")
        except KeyError as exc:
            raise DataCleaningError("Missing 'date' column") from exc

    def _convert_quantity(self) -> None:
        """Convert quantity_sold to numeric."""
        try:
            self.df["quantity_sold"] = pd.to_numeric(
                self.df["quantity_sold"], errors="coerce"
            )
        except KeyError as exc:
            raise DataCleaningError("Missing 'quantity_sold' column") from exc

    def _drop_invalid_rows(self) -> None:
        """
        Remove rows with:
        - Null dates
        - Null quantities
        - Non-positive quantities
        """
        self.df.dropna(subset=["date", "quantity_sold"], inplace=True)
        self.df = self.df[self.df["quantity_sold"] > 0]

    def _aggregate_by_frequency(self, frequency: str) -> None:
        """
        Aggregate sales by product and time frequency.
        """
        if frequency not in {"D", "W", "M"}:
            raise DataCleaningError("Invalid frequency. Use 'D', 'W', or 'M'.")

        self.df = (
            self.df.set_index("date")
            .groupby("product")
            .resample(frequency)["quantity_sold"]
            .sum()
            .reset_index()
        )

    def _sort_data(self) -> None:
        """Sort data by product and date."""
        self.df.sort_values(by=["product", "date"], inplace=True)
