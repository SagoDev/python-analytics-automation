"""Scheduler Class"""

from datetime import datetime
from pathlib import Path
import time
from typing import List
import schedule

from utils.logger import get_logger
from .loader import DataLoader
from .cleaner import DataCleaner
from .analyzer import Analyzer
from .chart_generator import ChartGenerator
from .report_generator import ReportExporter


class Scheduler:
    """
    Scheduler for automated execution of the log analytics pipeline.

    Supported schedules:
    - Daily at a specific hour
    - Every N days
    - Every N hours
    """

    def __init__(
        self,
        file_path: List[str | Path],
        charts_output_dir: str | Path = "output/charts",
        reports_output_dir: str | Path = "output/reports",
    ) -> None:
        self.log_paths = [Path(path) for path in file_path]
        self.charts_output_dir = Path(charts_output_dir)
        self.reports_output_dir = Path(reports_output_dir)
        self.logger = get_logger(__name__)

    def run_pipeline(self) -> None:
        """
        Full execution of the log analytics pipeline.
        """
        self.logger.info("Starting log analysis report generation...")

        try:
            # 1. Load data
            self.logger.debug("Step 1: Loading log data")
            loader = DataLoader(self.log_paths)
            df = loader.load()
            self.logger.info("Log data loaded: %d rows", len(df))

            # 2. Clean and preprocess data
            self.logger.debug("Step 2: Cleaning and preprocessing data")
            cleaner = DataCleaner()
            clean_df = cleaner.clean(df)
            self.logger.info("Data cleaned successfully: %d rows", len(clean_df))

            # 3. Analyze data
            self.logger.debug("Step 3: Analyzing log data")
            analyzer = Analyzer()
            analysis_results = analyzer.run_analysis(clean_df)
            self.logger.info("Log analysis completed successfully")

            # 4. Generate charts
            self.logger.debug("Step 4: Generating charts")
            chart_generator = ChartGenerator(self.charts_output_dir)
            chart_generator.run_charts(
                logs_by_hour=analysis_results["logs_by_hour"],
                errors_by_service=analysis_results["errors_by_service"],
                log_level_distribution=analysis_results["log_level_distribution"],
                volume_anomalies=analysis_results["volume_anomalies"],
            )

            # Get chart file paths
            charts = {
                "logs_by_hour": self.charts_output_dir / "logs_by_hour.png",
                "errors_by_service": self.charts_output_dir / "errors_by_service.png",
                "log_level_distribution": self.charts_output_dir
                / "log_level_distribution.png",
                "log_volume_anomalies": self.charts_output_dir
                / "log_volume_anomalies.png",
            }
            self.logger.info("Charts generated successfully")

            # 5. Export PDF report
            self.logger.debug("Step 5: Exporting PDF report")
            pdf_exporter = ReportExporter(self.reports_output_dir)
            pdf_path = pdf_exporter.export_to_pdf(
                clean_df=clean_df,
                kpis=analysis_results["summary_kpis"],
                charts=charts,
                file_name=f"log_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            )

            self.logger.info("Log analysis report successfully generated: %s", pdf_path)

        except Exception as exc:
            self.logger.error("Log analysis pipeline execution failed: %s", exc)
            raise

    def schedule_daily(self, hour: str = "09:00") -> None:
        """
        Schedule the pipeline to run every day at a specific hour.

        Parameters
        ----------
        hour : str
            Time in HH:MM format (24-hour format).
        """
        self.logger.info("Scheduling daily log analysis report at %s", hour)
        schedule.clear()
        schedule.every().day.at(hour).do(self.run_pipeline)
        self._start()

    def schedule_every_n_days(self, days: int) -> None:
        """
        Schedule the pipeline to run every N days.

        Parameters
        ----------
        days : int
            Number of days between executions.
        """
        if days <= 0:
            raise ValueError("Days must be a positive integer.")

        self.logger.info("Scheduling log analysis report every %d days", days)
        schedule.clear()
        schedule.every(days).days.do(self.run_pipeline)
        self._start()

    def schedule_every_n_hours(self, hours: int) -> None:
        """
        Schedule the pipeline to run every N hours.

        Parameters
        ----------
        hours : int
            Number of hours between executions.
        """
        if hours <= 0:
            raise ValueError("Hours must be a positive integer.")

        self.logger.info("Scheduling log analysis report every %d hours", hours)
        schedule.clear()
        schedule.every(hours).hours.do(self.run_pipeline)
        self._start()

    def _start(self) -> None:
        """
        Start the infinite scheduler loop.
        """
        self.logger.info("Log Analysis Scheduler started...")
        while True:
            schedule.run_pending()
            time.sleep(60)
