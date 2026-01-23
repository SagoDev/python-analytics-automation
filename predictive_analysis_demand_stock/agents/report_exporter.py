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
    PageBreak,
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
        Export all data and charts to a PDF with one page per product.

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

        # Title page
        elements.append(
            Paragraph("Sales Forecast & Stock Risk Report", self.styles["Title"])
        )
        elements.append(Spacer(1, 12))
        elements.append(
            Paragraph(
                f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                self.styles["Normal"],
            )
        )
        elements.append(Spacer(1, 20))

        # Summary tables on title page
        elements.append(Paragraph("Forecasted Demand Summary", self.styles["Heading2"]))
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

        # Section: Stock Risk Summary
        elements.append(
            Paragraph("Stock Risk Analysis Summary", self.styles["Heading2"])
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

        # Add page break before individual product pages
        elements.append(PageBreak())

        # Create one page per product
        products = sorted(charts_dict.keys())
        for i, product in enumerate(products):
            # Product title
            elements.append(
                Paragraph(f"Product Analysis: {product}", self.styles["Heading1"])
            )
            elements.append(Spacer(1, 12))

            # Product-specific data
            product_forecast = forecast_df[forecast_df["product"] == product]
            product_risk = stock_risk_df[stock_risk_df["product"] == product]

            # Add forecast data for this product
            elements.append(Paragraph("Forecast Details", self.styles["Heading2"]))
            if not product_forecast.empty:
                table_data = [
                    list(product_forecast.columns)
                ] + product_forecast.values.tolist()
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
            else:
                elements.append(
                    Paragraph("No forecast data available", self.styles["Normal"])
                )

            elements.append(Spacer(1, 12))

            # Add stock risk data for this product
            elements.append(Paragraph("Stock Risk Details", self.styles["Heading2"]))
            if not product_risk.empty:
                table_data = [list(product_risk.columns)] + product_risk.values.tolist()
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
            else:
                elements.append(
                    Paragraph("No stock risk data available", self.styles["Normal"])
                )

            elements.append(Spacer(1, 12))

            # Add chart for this product
            elements.append(Paragraph("Visual Analysis", self.styles["Heading2"]))
            elements.append(Spacer(1, 6))

            if product in charts_dict:
                try:
                    img = Image(str(charts_dict[product]))
                    # Adjust image size to fit well on A4 page
                    img.drawHeight = 400
                    img.drawWidth = 500
                    elements.append(img)
                    elements.append(Spacer(1, 12))
                except Exception as exc:
                    elements.append(
                        Paragraph(f"Could not load chart: {exc}", self.styles["Normal"])
                    )

            # Add page break except for the last product
            if i < len(products) - 1:
                elements.append(PageBreak())

        # Build PDF
        doc.build(elements)
        return file_path
