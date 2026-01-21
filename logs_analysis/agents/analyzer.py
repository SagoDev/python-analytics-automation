"""Analyzer"""

import pandas as pd


class Analyzer:
    """
    Performs statistical analysis and anomaly detection on log data.
    """

    def _calculate_summary_kpis(self, df: pd.DataFrame) -> dict:
        total_logs = len(df)
        error_logs = len(df[df["level"].isin(["ERROR", "CRITICAL"])])

        error_rate = error_logs / total_logs if total_logs > 0 else 0

        return {
            "total_logs": total_logs,
            "error_logs": error_logs,
            "error_rate": round(error_rate, 4),
        }

    def _logs_by_hour(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["hour"] = df["timestamp"].dt.floor("H")

        return (
            df.groupby("hour").size().reset_index(name="log_count").sort_values("hour")
        )

    def _errors_by_service(self, df: pd.DataFrame) -> pd.DataFrame:
        errors = df[df["level"].isin(["ERROR", "CRITICAL"])]

        return (
            errors.groupby("service")
            .size()
            .reset_index(name="error_count")
            .sort_values("error_count", ascending=False)
        )

    def _log_level_distribution(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.groupby("level")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )

    def _detect_volume_anomalies(
        self,
        logs_by_hour: pd.DataFrame,
        std_multiplier: float = 2.0,
    ) -> pd.DataFrame:
        mean = logs_by_hour["log_count"].mean()
        std = logs_by_hour["log_count"].std()

        threshold = mean + std_multiplier * std

        anomalies = logs_by_hour[logs_by_hour["log_count"] > threshold].copy()

        anomalies["threshold"] = threshold

        return anomalies

    def run_analysis(
        self,
        df: pd.DataFrame,
        *,
        std_multiplier: float = 2.0,
    ) -> dict:
        """
        Execute the full log analysis pipeline.

        Returns
        -------
        dict
            Dictionary containing all analysis outputs.
        """
        summary_kpis = self._calculate_summary_kpis(df)

        logs_hourly = self._logs_by_hour(df)
        errors_service = self._errors_by_service(df)
        level_distribution = self._log_level_distribution(df)
        anomalies = self._detect_volume_anomalies(
            logs_by_hour=logs_hourly,
            std_multiplier=std_multiplier,
        )

        return {
            "summary_kpis": summary_kpis,
            "logs_by_hour": logs_hourly,
            "errors_by_service": errors_service,
            "log_level_distribution": level_distribution,
            "volume_anomalies": anomalies,
        }
