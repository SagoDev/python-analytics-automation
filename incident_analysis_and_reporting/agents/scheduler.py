"""Scheduler Class"""

from datetime import datetime
from pathlib import Path
import time
from typing import Any
import schedule

from utils.logger import get_logger
from .data_loader import DataLoader
from .data_cleaner import DataCleaner
from .charts_generator import ChartsGenerator
from .kpi_calculator import KPICalculator
from .report_exporter import ReportExporter


class Scheduler:
    """
    Scheduler for automated execution of the  and support
    analytics pipeline.

    Supported schedules:
    - Daily at a specific hour
    - Every N days
    """

    def __init__(
        self,
        input_file: str | Path,
        charts_output_dir: str | Path = "output/charts",
        reports_output_dir: str | Path = "output/reports",
    ) -> None:
        self.input_file = Path(input_file)
        self.charts_output_dir = Path(charts_output_dir)
        self.reports_output_dir = Path(reports_output_dir)
        self.logger = get_logger(__name__)

    def run_pipeline(self) -> None:
        """
        Full execution of the  and support analytics pipeline.
        """
        self.logger.info("Starting  & support report generation...")

        try:
            # 1. Load data
            self.logger.debug("Step 1: Loading ticket data")
            loader = DataLoader(self.input_file)
            df = loader.load()
            self.logger.info("Ticket data loaded: %d rows", len(df))

            # 2. Clean and preprocess data
            self.logger.debug("Step 2: Cleaning and preprocessing data")
            cleaner = DataCleaner(df)
            clean_df = cleaner.clean()
            self.logger.info("Data cleaned successfully: %d rows", len(clean_df))

            # 3. Calculate KPIs
            self.logger.debug("Step 3: Calculating  KPIs")
            kpi_calculator = KPICalculator(clean_df)
            kpis = kpi_calculator.calculate_all()
            self.logger.info("KPIs calculated successfully")

            # 4. Generate charts
            self.logger.debug("Step 4: Generating charts")
            chart_generator = ChartsGenerator(self.charts_output_dir)
            charts: dict[str, Any] = {
                "tickets_by_category": chart_generator.tickets_by_category(clean_df),
                "tickets_by_priority": chart_generator.tickets_by_priority(clean_df),
                "avg_resolution_time_by_category": chart_generator.avg_resolution_time_by_category(
                    clean_df
                ),
                "ticket_status_distribution": chart_generator.ticket_status_distribution(
                    clean_df
                ),
                "tickets_created_vs_resolved": chart_generator.tickets_created_vs_resolved(
                    clean_df
                ),
            }
            self.logger.info("Charts generated successfully")

            # 5. Export PDF report
            self.logger.debug("Step 5: Exporting PDF report")
            pdf_exporter = ReportExporter(self.reports_output_dir)
            pdf_path = pdf_exporter.export_to_pdf(
                clean_df=clean_df,
                kpis=kpis,
                charts=charts,
                file_name=f"tickets_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            )

            self.logger.info(" report successfully generated: %s", pdf_path)

        except Exception as exc:
            self.logger.error(" pipeline execution failed: %s", exc)
            raise

    def schedule_daily(self, hour: str = "09:00") -> None:
        """
        Schedule the pipeline to run every day at a specific hour.

        Parameters
        ----------
        hour : str
            Time in HH:MM format (24-hour format).
        """
        self.logger.info("Scheduling daily  report at %s", hour)
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

        self.logger.info("Scheduling  report every %d days", days)
        schedule.clear()
        schedule.every(days).days.do(self.run_pipeline)
        self._start()

    def _start(self) -> None:
        """
        Start the infinite scheduler loop.
        """
        self.logger.info(" & Support Scheduler started...")
        while True:
            schedule.run_pending()
            time.sleep(60)
