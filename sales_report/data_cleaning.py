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
        self._validate_numeric_values()
        self._recalculate_total()

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
        - date -> datetime
        - quantity -> int
        - unit_price -> float
        - total -> float
        """
        self.logger.debug("Converting data types")
        try:
            self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")
            self.df["quantity"] = pd.to_numeric(self.df["quantity"], errors="coerce")
            self.df["unit_price"] = pd.to_numeric(
                self.df["unit_price"], errors="coerce"
            )
            self.df["total"] = pd.to_numeric(self.df["total"], errors="coerce")
            self.logger.debug("Data types converted successfully")
        except KeyError as exc:
            error_msg = "Missing expected column: %s"
            self.logger.error(error_msg, exc)
            raise DataCleaningError(error_msg % exc) from exc

    def _validate_numeric_values(self) -> None:
        """
        Validate numeric business rules:
        - quantity must be > 0
        - unit_price must be >= 0
        - total must be >= 0
        """
        self.logger.debug("Validating numeric values")
        invalid_rows = self.df[
            (self.df["quantity"] <= 0)
            | (self.df["unit_price"] < 0)
            | (self.df["total"] < 0)
        ]

        if not invalid_rows.empty:
            error_msg = "Invalid numeric values found in %d rows."
            self.logger.error(error_msg, len(invalid_rows))
            raise DataCleaningError(error_msg % len(invalid_rows))

        self.logger.debug("Numeric values validated successfully")

    def _recalculate_total(self) -> None:
        """
        Recalculate the total column to ensure consistency:
        total = quantity * unit_price
        """
        self.logger.debug("Recalculating total column")
        self.df["total"] = self.df["quantity"] * self.df["unit_price"]
        self.logger.debug("Total column recalculated successfully")
