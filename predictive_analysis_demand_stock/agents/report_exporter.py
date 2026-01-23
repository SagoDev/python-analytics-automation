"""
PDF Report Exporter Module

Generates PDF reports for demand forecasting and stock risk using ReportLab.
"""

from pathlib import Path
from datetime import datetime

import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
)


class ReportExporter:
    """
    Exports analysis and forecast into a PDF report.
    """

    def __init__(self, output_dir: str | Path = "output/reports_pdf") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()

    def export_pdf(
        self,
        clean_sales_df: pd.DataFrame,
        forecast_df: pd.DataFrame,
        stock_risk_df: pd.DataFrame,
        charts_dict: dict[str, Path],
        file_name: str | None = None,
    ) -> Path:
        """
        Export all data and charts to a PDF.

        Args:
            clean_sales_df: Cleaned sales data
            forecast_df: Forecasted demand
            stock_risk_df: Stock risk
            charts_dict: Dictionary of product -> chart path
            file_name: Optional PDF file name

        Returns:
            Path to the saved PDF
        """
        if file_name is None:

            file_name = (
                f"sales_forecast_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            )

        file_path = self.output_dir / file_name

        doc = SimpleDocTemplate(str(file_path), pagesize=A4)
        elements = []

        # Title
        elements.append(
            Paragraph("Sales Forecast & Stock Risk Report", self.styles["Title"])
        )
        elements.append(Spacer(1, 12))

        # Section: Historical Sales (sample)
        elements.append(
            Paragraph("Historical Sales (Top 10 Rows)", self.styles["Heading2"])
        )
        sample_sales = clean_sales_df.head(10)
        table_data = [list(sample_sales.columns)] + sample_sales.values.tolist()
        table = Table(table_data)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d3d3d3")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ]
            )
        )
        elements.append(table)
        elements.append(Spacer(1, 12))

        # Section: Forecast (sample)
        elements.append(
            Paragraph("Forecasted Demand (Top 10 Rows)", self.styles["Heading2"])
        )
        sample_forecast = forecast_df.head(10)
        table_data = [list(sample_forecast.columns)] + sample_forecast.values.tolist()
        table = Table(table_data)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d3d3d3")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ]
            )
        )
        elements.append(table)
        elements.append(Spacer(1, 12))

        # Section: Stock Risk (Top 10)
        elements.append(
            Paragraph("Stock Risk Analysis (Top 10 Rows)", self.styles["Heading2"])
        )
        sample_risk = stock_risk_df.head(10)
        table_data = [list(sample_risk.columns)] + sample_risk.values.tolist()
        table = Table(table_data)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d3d3d3")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ]
            )
        )
        elements.append(table)
        elements.append(Spacer(1, 12))

        # Section: Charts
        elements.append(Paragraph("Charts", self.styles["Heading2"]))
        elements.append(Spacer(1, 12))

        for product, chart_path in charts_dict.items():
            elements.append(Paragraph(product, self.styles["Heading3"]))
            elements.append(Spacer(1, 6))
            try:
                img = Image(str(chart_path))
                img.drawHeight = 150
                img.drawWidth = 300
                elements.append(img)
                elements.append(Spacer(1, 12))
            except Exception as exc:
                elements.append(
                    Paragraph(f"Could not load chart: {exc}", self.styles["Normal"])
                )

        # Build PDF
        doc.build(elements)
        return file_path
