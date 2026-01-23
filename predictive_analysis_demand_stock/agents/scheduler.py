"""
Scheduler Class for Stock & Demand Forecasting

Automates the execution of the full pipeline:
1. Load historical sales and stock data
2. Clean and aggregate
3. Analyze demand
4. Forecast future demand
5. Detect stock-out risk
6. Generate charts
7. Export PDF report
"""

from datetime import datetime
from pathlib import Path
import time
import schedule

from utils.logger import get_logger
from .data_loader import DataLoader
from .data_cleaner import DataCleaner
from .forecasting import Forecasting
from .stock_risk import StockRisk
from .chart_generator import ChartGenerator
from .report_exporter import ReportExporter


class Scheduler:
    """
    Scheduler for automated execution of the stock & demand forecasting pipeline.

    Supported schedules:
    - Daily at a specific hour
    - Every N days
    """

    def __init__(
        self,
        sales_file: str | Path,
        stock_file: str | Path,
        charts_output_dir: str | Path = "output/charts",
        reports_output_dir: str | Path = "output/reports_pdf",
    ) -> None:
        self.sales_file = Path(sales_file)
        self.stock_file = Path(stock_file)
        self.charts_output_dir = Path(charts_output_dir)
        self.reports_output_dir = Path(reports_output_dir)
        self.logger = get_logger(__name__)

    def run_pipeline(self) -> None:
        """
        Full execution of the stock & demand forecasting pipeline.
        """
        self.logger.info("Starting Stock & Demand Forecasting pipeline...")

        try:
            # 1. Load sales and stock data
            self.logger.debug("Step 1: Loading sales and stock data")
            loader = DataLoader(self.sales_file, self.stock_file)
            sales_df, stock_df = loader.load_sales_data(), loader.load_stock_data()
            self.logger.info(
                "Data loaded successfully: %d sales rows, %d stock rows",
                len(sales_df),
                len(stock_df),
            )

            # 2. Clean and preprocess sales data
            self.logger.debug("Step 2: Cleaning and aggregating sales data")
            cleaner = DataCleaner(sales_df)
            clean_sales_df = cleaner.clean(frequency="W")
            self.logger.info("Sales data cleaned: %d rows", len(clean_sales_df))

            # 3. Forecast demand
            self.logger.debug("Step 4: Forecasting demand")
            forecaster = Forecasting(
                clean_sales_df,
                date_col="date",
                product_col="product",
                sales_col="quantity_sold",
            )
            forecast_df = forecaster.combined_forecast(
                periods=1, trend_weight=0.4, seasonal_weight=0.4, noise_weight=0.2
            )  # next 1 week
            self.logger.info(
                "Forecast completed for %d products", forecast_df["product"].nunique()
            )

            # 4. Stock risk analysis
            self.logger.debug("Step 5: Analyzing stock risk")
            risk_analyzer = StockRisk(forecast_df, stock_df)
            stock_risk_df = risk_analyzer.analyze()
            self.logger.info("Stock risk analysis completed")

            # 5. Generate charts
            self.logger.debug("Step 6: Generating charts")
            chart_gen = ChartGenerator(self.charts_output_dir)
            individual_charts = chart_gen.plot_individual_product_forecasts(
                clean_sales_df, forecast_df
            )
            charts = {**individual_charts}
            self.logger.info("Charts generated successfully")

            # 6. Export PDF report
            self.logger.debug("Step 7: Exporting PDF report")
            pdf_exporter = ReportExporter(self.reports_output_dir)
            pdf_path = pdf_exporter.export_pdf(
                clean_sales_df=clean_sales_df,
                forecast_df=forecast_df,
                stock_risk_df=stock_risk_df,
                charts_dict=charts,
                file_name=f"stock_forecast_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            )
            self.logger.info("PDF report successfully generated: %s", pdf_path)

        except Exception as exc:
            self.logger.error("Pipeline execution failed: %s", exc)
            raise

    def schedule_daily(self, hour: str = "09:00") -> None:
        """
        Schedule the pipeline to run every day at a specific hour.
        """
        self.logger.info("Scheduling daily Stock & Forecast report at %s", hour)
        schedule.clear()
        schedule.every().day.at(hour).do(self.run_pipeline)
        self._start()

    def schedule_every_n_days(self, days: int) -> None:
        """
        Schedule the pipeline to run every N days.
        """
        if days <= 0:
            raise ValueError("Days must be a positive integer.")

        self.logger.info("Scheduling Stock & Forecast report every %d days", days)
        schedule.clear()
        schedule.every(days).days.do(self.run_pipeline)
        self._start()

    def _start(self) -> None:
        """
        Start the infinite scheduler loop.
        """
        self.logger.info("Stock & Forecast Scheduler started...")
        while True:
            schedule.run_pending()
            time.sleep(60)
