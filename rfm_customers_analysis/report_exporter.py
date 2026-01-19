"""PDF Exporter Class"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.platypus import PageBreak
from logger import get_logger


class PDFExportError(Exception):
    """Custom exception for PDF export errors."""


class ReportExporter:
    """
    Exports customers reports to PDF format including:
    - Executive summary with KPIs
    - Data tables
    - Charts
    """

    def __init__(self, output_dir: str | Path = "output/reports") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(__name__)

    def export_to_pdf(
        self,
        clean_df: pd.DataFrame,
        kpis: Dict[str, Any],
        charts: Dict[str, Path],
        file_name: str = "rfm_report.pdf",
    ) -> Path:
        """
        Export the customers report to a PDF file.

        Parameters
        ----------
        clean_df : pd.DataFrame
            Cleaned customers data
        kpis : Dict[str, Any]
            Calculated KPIs
        charts : Dict[str, Path]
            Chart image paths
        file_name : str
            Output PDF file name

        Returns
        -------
        Path
            Path to the generated PDF file.
        """
        self.logger.info("Starting PDF report export: %s", file_name)
        try:
            file_path = self.output_dir / file_name

            # Create PDF document
            doc = SimpleDocTemplate(
                str(file_path),
                pagesize=A4,
                rightMargin=inch,
                leftMargin=inch,
                topMargin=inch,
                bottomMargin=inch,
            )

            # Get styles
            styles = getSampleStyleSheet()

            # Create custom styles
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.darkblue,
                alignment=1,  # Center alignment
            )

            heading_style = ParagraphStyle(
                "CustomHeading",
                parent=styles["Heading2"],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.darkblue,
                spaceBefore=20,
            )

            # Build the PDF content (story)
            story = []

            # Title
            story.append(Paragraph("RFM Customers Analytics Report", title_style))
            story.append(
                Paragraph(
                    f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                    styles["Normal"],
                )
            )
            story.append(Spacer(1, 20))

            # Executive Summary
            story.extend(self._build_executive_summary(kpis, heading_style, styles))

            # KPI Summary Table
            story.extend(self._build_kpi_table(kpis, heading_style, styles))

            # Page break before data and charts
            story.append(PageBreak())

            # Data Overview (first 20 rows)
            story.extend(self._build_data_overview(clean_df, heading_style, styles))

            # Charts - start on new page
            story.append(PageBreak())
            story.extend(self._build_charts_section(charts, heading_style, styles))

            # Build PDF
            doc.build(story)

            self.logger.info("PDF report successfully exported: %s", file_path)
            return file_path

        except Exception as exc:
            error_msg = "Error exporting PDF report: %s"
            self.logger.error(error_msg, exc)
            raise PDFExportError(error_msg % exc) from exc

    def _build_executive_summary(self, kpis: Dict[str, Any], heading_style, styles):
        """Build executive summary section for RFM analysis."""
        elements = []

        elements.append(Paragraph("Executive Summary", heading_style))

        top_segment_text = ""
        if "top_segment" in kpis and not kpis["top_segment"].empty:
            segment_name = kpis["top_segment"].index[0]
            segment_size = kpis["top_segment"].iloc[0]
            top_segment_text = (
                f"The largest customer segment is <b>{segment_name}</b>, "
                f"representing {segment_size:,} customers. "
            )

        summary_text = f"""
        This report presents an automated RFM-based customer analysis derived from
        historical purchase behavior.

        A total of <b>{kpis['total_customers']:,}</b> customers were analyzed, of which
        <b>{kpis['active_customers']:,}</b> are currently considered active.
        The average purchase recency is <b>{kpis['avg_recency']:.1f} days</b>, with an
        average purchase frequency of <b>{kpis['avg_frequency']:.2f}</b> transactions per customer
        and an average monetary value of <b>${kpis['avg_monetary']:,.2f}</b>.

        Importantly, <b>{kpis['churn_risk_customers']:,}</b> customers have been identified
        as being at risk of churn and may require targeted retention actions.
        {top_segment_text}

        The following sections provide a detailed segmentation analysis and visual insights
        to support data-driven customer engagement and retention strategies.
        """

        elements.append(Paragraph(summary_text, styles["Normal"]))
        elements.append(Spacer(1, 20))

        return elements

    def _build_kpi_table(self, kpis: Dict[str, Any], heading_style, styles):
        """Build RFM KPI summary table section."""
        elements = []

        elements.append(Paragraph("Customer Key Metrics (RFM)", heading_style))

        kpi_data = [
            ["Metric", "Value"],
            ["Total Customers", f"{kpis['total_customers']:,}"],
            ["Active Customers", f"{kpis['active_customers']:,}"],
            ["Customers at Churn Risk", f"{kpis['churn_risk_customers']:,}"],
            ["Average Recency (days)", f"{kpis['avg_recency']:.1f}"],
            ["Average Frequency", f"{kpis['avg_frequency']:.2f}"],
            ["Average Monetary Value", f"${kpis['avg_monetary']:,.2f}"],
        ]

        # Top segment
        if "top_segment" in kpis and not kpis["top_segment"].empty:
            segment_name = kpis["top_segment"].index[0]
            segment_size = kpis["top_segment"].iloc[0]
            kpi_data.append(
                ["Largest Segment", f"{segment_name} ({segment_size:,} customers)"]
            )

        # Most valuable customer
        if (
            "most_valuable_customer" in kpis
            and not kpis["most_valuable_customer"].empty
        ):
            customer_id = kpis["most_valuable_customer"].index[0]
            customer_value = kpis["most_valuable_customer"].iloc[0]
            kpi_data.append(
                [
                    "Top Customer by Value",
                    f"Customer {customer_id} (${customer_value:,.2f})",
                ]
            )

        table = Table(kpi_data, colWidths=[3 * inch, 2 * inch])

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                ]
            )
        )

        elements.append(table)
        elements.append(Spacer(1, 20))

        return elements

    def _build_data_overview(self, clean_df: pd.DataFrame, heading_style, styles):
        """Build data overview section."""
        elements = []

        elements.append(Paragraph("Customers Data Overview", heading_style))
        elements.append(
            Paragraph(
                f"Showing first 20 rows of {len(clean_df)} total records:",
                styles["Normal"],
            )
        )

        # Take first 20 rows
        sample_df = clean_df.head(20)

        # Convert DataFrame to table data
        data_list = [sample_df.columns.values.tolist()] + sample_df.values.tolist()

        # Create table
        table = Table(data_list)

        # Style the table
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTSIZE", (0, 1), (-1, -1), 7),
                ]
            )
        )

        elements.append(table)
        elements.append(Spacer(1, 20))

        return elements

    def _build_charts_section(self, charts: Dict[str, Path], heading_style, styles):
        """Build charts section with each chart on its own page."""
        elements = []

        if not charts:
            elements.append(Paragraph("Visual Analytics", heading_style))
            elements.append(
                Paragraph("No charts available for this report.", styles["Normal"])
            )
            return elements

        # Updated chart titles mapping
        chart_titles = {}

        chart_list = list(charts.items())

        for i, (chart_name, chart_path) in enumerate(chart_list):
            if not chart_path.exists():
                self.logger.warning("Chart file not found: %s", chart_path)
                continue

            if i > 0:
                elements.append(PageBreak())

            title = chart_titles.get(
                chart_name,
                chart_name.replace("_", " ").title(),
            )

            elements.append(Paragraph(title, heading_style))
            elements.append(Spacer(1, 20))

            img = Image(str(chart_path), width=6 * inch, height=4 * inch)
            elements.append(img)

        return elements
