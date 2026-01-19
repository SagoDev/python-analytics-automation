"""Data Loader Class"""

from pathlib import Path

import pandas as pd
from logger import get_logger


class DataLoaderError(Exception):
    """Custom exception for data loading errors."""


class DataLoader:
    """
    Handles loading customers data from CSV or Excel files and
    performs basic schema validation and column normalization.
    """

    REQUIRED_COLUMNS = [
        "customer_id",
        "purchase_date",
        "order_id",
        "order_value",
    ]

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)
        self.logger = get_logger(__name__)

    def load(self) -> pd.DataFrame:
        """
        Load a CSV or Excel file into a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            Raw DataFrame loaded from the file.

        Raises
        ------
        DataLoaderError
            If the file does not exist, format is not supported,
            or required columns are missing.
        """
        self.logger.info("Loading data from: %s", self.file_path)

        if not self.file_path.exists():
            self.logger.error("File not found: %s", self.file_path)
            raise DataLoaderError("File not found: %s", self.file_path)

        try:
            df = self._read_file()
            self.logger.debug(
                "File read successfully: %d rows, %d columns", len(df), len(df.columns)
            )

            df = self._normalize_columns(df)
            self.logger.debug("Columns normalized successfully")

            self._validate_schema(df)
            self.logger.info("Data loaded and validated successfully")

            return df
        except Exception as e:
            self.logger.error("Error loading data: %s", e)
            raise

    def _read_file(self) -> pd.DataFrame:
        """
        Read the input file based on its extension.

        Supported formats:
        - .csv
        - .xlsx
        - .xls
        """
        suffix = self.file_path.suffix.lower()
        self.logger.debug("Reading file with format: %s", suffix)

        try:
            if suffix == ".csv":
                df = pd.read_csv(self.file_path)
            elif suffix in {".xlsx", ".xls"}:
                df = pd.read_excel(self.file_path)
            else:
                error_msg = "Unsupported file format: %s. Only CSV and Excel files are supported."
                self.logger.error(error_msg, suffix)
                raise DataLoaderError(error_msg % suffix)

            self.logger.debug("File read successfully: %d rows", len(df))
            return df
        except Exception as exc:
            error_msg = "Error reading file: %s"
            self.logger.error(error_msg, exc)
            raise DataLoaderError(error_msg % exc) from exc

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names:
        - Strip whitespace
        - Convert to lowercase
        - Replace spaces with underscores
        """
        df = df.copy()
        original_columns = df.columns.tolist()
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        if original_columns != df.columns.tolist():
            self.logger.debug(
                "Columns normalized: %s -> %s", original_columns, df.columns.tolist()
            )

        return df

    def _validate_schema(self, df: pd.DataFrame) -> None:
        """
        Validate that all required columns exist in the DataFrame.

        Raises
        ------
        DataLoaderError
            If any required column is missing.
        """
        missing_columns = set(self.REQUIRED_COLUMNS) - set(df.columns)

        if missing_columns:
            error_msg = "Missing required columns: %s"
            sorted_cols = sorted(missing_columns)
            self.logger.error(error_msg, sorted_cols)
            raise DataLoaderError(error_msg % sorted_cols)

        self.logger.debug("Schema validation passed")
