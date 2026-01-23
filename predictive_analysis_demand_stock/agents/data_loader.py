"""Data Loader class"""

from pathlib import Path
from typing import List
import pandas as pd


class DataLoaderError(Exception):
    """Custom exception for data loading errors."""


class DataLoader:
    """
    Loads and validates input data for demand forecasting and stock analysis.

    Supported datasets:
    - Sales history
    - Current stock levels
    """

    SALES_REQUIRED_COLUMNS: List[str] = [
        "date",
        "product",
        "quantity_sold",
    ]

    STOCK_REQUIRED_COLUMNS: List[str] = [
        "product",
        "current_stock",
        "lead_time_days",
    ]

    def __init__(
        self,
        sales_file: str | Path,
        stock_file: str | Path,
    ) -> None:
        self.sales_file = Path(sales_file)
        self.stock_file = Path(stock_file)

    def load_sales_data(self) -> pd.DataFrame:
        """
        Load and validate historical sales data.
        """
        df = self._load_file(self.sales_file)
        df = self._normalize_columns(df)
        self._validate_schema(df, self.SALES_REQUIRED_COLUMNS)
        return df

    def load_stock_data(self) -> pd.DataFrame:
        """
        Load and validate current stock data.
        """
        df = self._load_file(self.stock_file)
        df = self._normalize_columns(df)
        self._validate_schema(df, self.STOCK_REQUIRED_COLUMNS)
        return df

    def _load_file(self, file_path: Path) -> pd.DataFrame:
        """
        Load a CSV or Excel file based on extension.
        """
        if not file_path.exists():
            raise DataLoaderError(f"File not found: {file_path}")

        suffix = file_path.suffix.lower()

        try:
            if suffix == ".csv":
                return pd.read_csv(file_path)
            elif suffix in {".xlsx", ".xls"}:
                return pd.read_excel(file_path)
            else:
                raise DataLoaderError(
                    f"Unsupported file format: {suffix}. "
                    "Only CSV and Excel files are supported."
                )
        except Exception as exc:
            raise DataLoaderError(f"Error loading file {file_path}: {exc}") from exc

    @staticmethod
    def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names:
        - Strip whitespace
        - Lowercase
        - Replace spaces with underscores
        """
        df = df.copy()
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        return df

    @staticmethod
    def _validate_schema(df: pd.DataFrame, required_columns: List[str]) -> None:
        """
        Validate required columns in the DataFrame.
        """
        missing_columns = set(required_columns) - set(df.columns)

        if missing_columns:
            raise DataLoaderError(
                f"Missing required columns: {sorted(missing_columns)}"
            )
