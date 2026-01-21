"""Data Loader"""

from pathlib import Path
from typing import List

import pandas as pd


class DataLoader:
    """
    Loads and parses log files into a structured DataFrame.
    """

    def __init__(self, log_paths: List[Path]) -> None:
        self.log_paths = log_paths

    def load(self) -> pd.DataFrame:
        """
        Load and parse all configured log files.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
            - timestamp (str)
            - level (str)
            - service (str)
            - message (str)
        """
        records: list[dict] = []

        for path in self.log_paths:
            if not path.exists():
                raise FileNotFoundError(f"Log file not found: {path}")

            with path.open("r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    parsed = self._parse_line(line.strip(), path, line_number)
                    if parsed:
                        records.append(parsed)

        return pd.DataFrame.from_records(records)

    def _parse_line(
        self,
        line: str,
        path: Path,
        line_number: int,
    ) -> dict | None:
        """
        Parse a single log line.
        """
        if not line:
            return None

        parts = [part.strip() for part in line.split("|", maxsplit=3)]

        if len(parts) != 4:
            # Invalid or malformed line; skip safely
            return None

        timestamp, level, service, message = parts

        return {
            "timestamp": timestamp,
            "level": level,
            "service": service,
            "message": message,
            "source_file": path.name,
            "line_number": line_number,
        }
