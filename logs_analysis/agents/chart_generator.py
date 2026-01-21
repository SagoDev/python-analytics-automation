"""Charts Generator"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


class ChartGenerator:
    """
    Generates charts for log analysis.
    """

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _save_chart(self, filename: str) -> None:
        path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(path)
        plt.close()

    def logs_by_hour(self, df: pd.DataFrame) -> None:
        plt.figure()
        plt.plot(df["hour"], df["log_count"])
        plt.title("Log Volume by Hour")
        plt.xlabel("Hour")
        plt.ylabel("Log Count")

        self._save_chart("logs_by_hour.png")

    def errors_by_service(self, df: pd.DataFrame) -> None:
        plt.figure()
        plt.bar(df["service"], df["error_count"])
        plt.title("Errors by Service")
        plt.xlabel("Service")
        plt.ylabel("Error Count")
        plt.xticks(rotation=45, ha="right")

        self._save_chart("errors_by_service.png")

    def log_level_distribution(self, df: pd.DataFrame) -> None:
        plt.figure()
        plt.pie(
            df["count"],
            labels=df["level"],
            autopct="%1.1f%%",
        )
        plt.title("Log Level Distribution")

        self._save_chart("log_level_distribution.png")

    def volume_anomalies(
        self,
        logs_by_hour: pd.DataFrame,
        anomalies: pd.DataFrame,
    ) -> None:
        plt.figure()
        plt.plot(
            logs_by_hour["hour"],
            logs_by_hour["log_count"],
            label="Log Count",
        )

        if not anomalies.empty:
            plt.scatter(
                anomalies["hour"],
                anomalies["log_count"],
                label="Anomaly",
            )

        plt.title("Log Volume Anomalies")
        plt.xlabel("Hour")
        plt.ylabel("Log Count")
        plt.legend()

        self._save_chart("log_volume_anomalies.png")

    def run_charts(
        self,
        *,
        logs_by_hour: pd.DataFrame,
        errors_by_service: pd.DataFrame,
        log_level_distribution: pd.DataFrame,
        volume_anomalies: pd.DataFrame,
    ) -> None:
        """
        Generate all charts for the log analysis pipeline.
        """
        self.logs_by_hour(logs_by_hour)
        self.errors_by_service(errors_by_service)
        self.log_level_distribution(log_level_distribution)
        self.volume_anomalies(
            logs_by_hour=logs_by_hour,
            anomalies=volume_anomalies,
        )
