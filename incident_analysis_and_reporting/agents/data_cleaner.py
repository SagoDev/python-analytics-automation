"""Data Cleaner Class"""

import pandas as pd


class DataCleaningError(Exception):
    """Custom exception for incident data cleaning errors."""


class DataCleaner:
    """
    Cleans and enriches support ticket data to prepare it for analysis.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy()

    def clean(self) -> pd.DataFrame:
        """
        Execute the full incident data cleaning pipeline.

        Returns
        -------
        pd.DataFrame
            Cleaned and enriched incident DataFrame.
        """
        self._drop_empty_rows()
        self._drop_duplicates()
        self._normalize_text_columns()
        self._convert_datetime_columns()
        self._calculate_resolution_times()
        self._create_status_flags()

        return self.df

    def _drop_empty_rows(self) -> None:
        """Remove completely empty rows."""
        self.df.dropna(how="all", inplace=True)

    def _drop_duplicates(self) -> None:
        """Remove duplicate tickets based on ticket_id."""
        if "ticket_id" in self.df.columns:
            self.df.drop_duplicates(subset=["ticket_id"], inplace=True)
        else:
            self.df.drop_duplicates(inplace=True)

    def _normalize_text_columns(self) -> None:
        """
        Normalize text columns:
        - strip whitespace
        - lowercase
        """
        text_columns = ["category", "priority", "status", "agent", "team"]

        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip().str.lower()

    def _convert_datetime_columns(self) -> None:
        """
        Convert date columns to datetime.
        """
        try:
            self.df["created_at"] = pd.to_datetime(
                self.df["created_at"], errors="coerce"
            )
            self.df["closed_at"] = pd.to_datetime(self.df["closed_at"], errors="coerce")
        except KeyError as exc:
            raise DataCleaningError(f"Missing datetime column: {exc}") from exc

    def _remove_open_tickets(self) -> None:
        """
        Remove rows where tickets are still open (closed_at is missing).

        This method filters out tickets that haven't been closed yet,
        keeping only resolved tickets for analysis.
        """
        initial_count = len(self.df)
        self.df.dropna(subset=["closed_at"], inplace=True)
        removed_count = initial_count - len(self.df)

        if removed_count > 0:
            print(f"Removed {removed_count} open tickets from dataset")

    def _calculate_resolution_times(self) -> None:
        """
        Calculate resolution time in hours and days.

        Tickets without closed_at are considered open and will have
        NaN resolution times.
        """
        self.df["resolution_time_hours"] = (
            self.df["closed_at"] - self.df["created_at"]
        ).dt.total_seconds() / 3600

        self.df["resolution_time_days"] = self.df["resolution_time_hours"] / 24

        # Invalid resolution times (negative)
        invalid_times = self.df["resolution_time_hours"] < 0
        if invalid_times.any():
            raise DataCleaningError(
                "Found negative resolution times. Check created_at / closed_at values."
            )

    def _create_status_flags(self) -> None:
        """
        Create operational flags:
        - is_open
        - is_closed
        """
        self.df["is_closed"] = self.df["closed_at"].notna()
        self.df["is_open"] = ~self.df["is_closed"]
