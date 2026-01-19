"""Scheduler Class"""

from datetime import datetime
from pathlib import Path
import time
import schedule

from data_loader import DataLoader
from data_cleaner import DataCleaner
from charts_generator import ChartsGenerator
from kpi_calculator import KPICalculator
from report_exporter import ReportExporter
from rfm_segmenter import RFMSegmenter
from rfm_analyzer import RFMAnalyzer

from logger import get_logger


class Scheduler:
    """
    Scheduler for automated execution of customers report pipeline.
    It allows running pipeline:
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
        self.charts_output_dir = charts_output_dir
        self.reports_output_dir = reports_output_dir
        self.logger = get_logger(__name__)

    def run_pipeline(self) -> None:
        """
        Full execution of the customers report automation pipeline.
        """
        self.logger.info("Starting customers report generation...")

        try:
            # 1. Load data
            self.logger.debug("Step 1: Loading data")
            loader = DataLoader(self.input_file)
            df = loader.load()
            self.logger.info("Data loaded successfully: %d rows", len(df))

            # 2. Clean data
            self.logger.debug("Step 2: Cleaning data")
            cleaner = DataCleaner(df)
            clean_df = cleaner.clean()
            self.logger.info("Data cleaned successfully: %d rows", len(clean_df))

            # 3. Calculate KPI's
            rfm_df = RFMAnalyzer(clean_df).calculate_rfm()
            rfm_df = RFMSegmenter(rfm_df).segment()

            self.logger.debug("Step 3: Calculating RFM")
            kpi_calculator = KPICalculator(rfm_df)
            kpis = kpi_calculator.calculate_all()
            self.logger.info("KPIs calculated successfully")

            # 4. Generate charts
            self.logger.debug("Step 4: Generating charts")
            charts_generator = ChartsGenerator(self.charts_output_dir)
            charts = charts_generator.generate_charts(kpis)
            self.logger.info("Charts generated successfully: %d charts", len(charts))

            # 5. Export PDF report
            self.logger.debug("Step 6: Exporting PDF report")
            pdf_exporter = ReportExporter(self.reports_output_dir)
            pdf_path = pdf_exporter.export_to_pdf(
                clean_df=clean_df,
                kpis=kpis,
                charts=charts,
                file_name=f"rfm_customers_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            )

            self.logger.info("PDF report successfully generated: %s", pdf_path)

        except Exception as e:
            self.logger.error("Pipeline execution failed: %s", e)
            raise

    def schedule_daily(self, hour: str = "09:00") -> None:
        """
        Schedule the pipeline to run every day at a specific hour.

        Parameters
        ----------
        hour : str
            Time in HH:MM format (24-hour format).
        """
        self.logger.info("Scheduling daily execution at %s", hour)
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

        self.logger.info("Scheduling execution every %d days", days)
        schedule.clear()
        schedule.every(days).days.do(self.run_pipeline)
        self._start()

    def _start(self) -> None:
        """
        Start the infinite scheduler loop.
        """
        self.logger.info("customers Report Scheduler started...")
        while True:
            schedule.run_pending()
            time.sleep(60)
