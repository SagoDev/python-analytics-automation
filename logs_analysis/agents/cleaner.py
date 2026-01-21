"""Data Cleaner"""

import pandas as pd


class DataCleaner:
    """
    Cleans and normalizes log data for analysis.
    """

    VALID_LEVELS = {"INFO", "WARNING", "ERROR", "CRITICAL"}

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize log DataFrame.

        Returns
        -------
        pd.DataFrame
            Cleaned DataFrame with normalized fields.
        """
        df = df.copy()

        df = self._convert_timestamp(df)
        df = self._normalize_levels(df)
        df = self._drop_invalid_rows(df)

        return df.reset_index(drop=True)

    def _convert_timestamp(self, df: pd.DataFrame) -> pd.DataFrame:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce",
        )
        return df

    def _normalize_levels(self, df: pd.DataFrame) -> pd.DataFrame:
        df["level"] = df["level"].astype(str).str.strip().str.upper()
        return df

    def _drop_invalid_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        required_columns = ["timestamp", "level", "service", "message"]

        df = df.dropna(subset=required_columns)

        df = df[df["level"].isin(self.VALID_LEVELS)]

        return df
