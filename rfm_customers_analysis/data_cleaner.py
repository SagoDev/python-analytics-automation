"""Data Cleaner Class"""

import pandas as pd
from logger import get_logger


class DataCleaningError(Exception):
    """Custom exception for data cleaning errors."""


class DataCleaner:
    """
    Applies data cleaning rules to a sales DataFrame in order to
    ensure consistency and data quality before KPI calculations.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy()
        self.logger = get_logger(__name__)

    def clean(self) -> pd.DataFrame:
        """
        Execute the full data cleaning pipeline.

        Returns
        -------
        pd.DataFrame
            Cleaned and validated DataFrame.
        """
        self.logger.info("Starting data cleaning process")
        original_rows = len(self.df)

        self._drop_empty_rows()
        self._drop_duplicates()
        self._normalize_text_columns()
        self._convert_data_types()

        final_rows = len(self.df)
        self.logger.info(
            "Data cleaning completed. Removed %d rows", original_rows - final_rows
        )

        return self.df

    def _drop_empty_rows(self) -> None:
        """Remove rows that are completely empty."""
        original_count = len(self.df)
        self.df.dropna(how="all", inplace=True)
        removed = original_count - len(self.df)
        if removed > 0:
            self.logger.debug("Removed %d empty rows", removed)

    def _drop_duplicates(self) -> None:
        """Remove duplicated rows."""
        original_count = len(self.df)
        self.df.drop_duplicates(inplace=True)
        removed = original_count - len(self.df)
        if removed > 0:
            self.logger.debug("Removed %d duplicate rows", removed)

    def _normalize_text_columns(self) -> None:
        """
        Normalize string columns:
        - Strip whitespace
        - Convert to lowercase
        """
        text_columns = ["product", "category", "seller"]
        self.logger.debug("Normalizing text columns: %s", text_columns)

        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip().str.lower()
                self.logger.debug("Normalized column: %s", col)

    def _convert_data_types(self) -> None:
        """
        Convert column data types:
        - purchase_date -> datetime
        - order_value -> int
        """
        self.logger.debug("Converting data types")
        try:
            self.df["purchase_date"] = pd.to_datetime(
                self.df["purchase_date"], errors="coerce"
            )
            self.df["order_value"] = pd.to_numeric(
                self.df["order_value"], errors="coerce"
            )
            self.logger.debug("Data types converted successfully")
        except KeyError as exc:
            error_msg = "Missing expected column: %s"
            self.logger.error(error_msg, exc)
            raise DataCleaningError(error_msg % exc) from exc
