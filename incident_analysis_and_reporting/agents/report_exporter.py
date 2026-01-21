"""Report exporter"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from utils.logger import get_logger


class PDFExportError(Exception):
    """Custom exception for PDF export errors."""


class ReportExporter:
    """
    Exports incident and support reports to PDF format including:
    - Executive summary with operational KPIs
    - Ticket data overview
    - Visual analytics (charts)
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
        file_name: str = "incident_support_report.pdf",
    ) -> Path:
        """
        Export the incident and support analysis report to a PDF file.
        """
        self.logger.info("Starting incident PDF report export: %s", file_name)

        try:
            file_path = self.output_dir / file_name

            doc = SimpleDocTemplate(
                str(file_path),
                pagesize=A4,
                rightMargin=inch,
                leftMargin=inch,
                topMargin=inch,
                bottomMargin=inch,
            )

            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.darkblue,
                alignment=1,
            )

            heading_style = ParagraphStyle(
                "CustomHeading",
                parent=styles["Heading2"],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.darkblue,
                spaceBefore=20,
            )

            story = []

            # Title
            story.append(Paragraph("Incident & Support Analytics Report", title_style))
            story.append(
                Paragraph(
                    f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                    styles["Normal"],
                )
            )
            story.append(Spacer(1, 20))

            # Executive Summary
            story.extend(self._build_executive_summary(kpis, heading_style, styles))

            # KPI Table
            story.extend(self._build_kpi_table(kpis, heading_style))

            story.append(PageBreak())

            # Data Overview
            story.extend(self._build_data_overview(clean_df, heading_style, styles))

            story.append(PageBreak())

            # Charts
            story.extend(self._build_charts_section(charts, heading_style))

            doc.build(story)

            self.logger.info("Incident PDF report successfully exported: %s", file_path)
            return file_path

        except Exception as exc:
            error_msg = "Error exporting incident PDF report: %s"
            self.logger.error(error_msg, exc)
            raise PDFExportError(error_msg % exc) from exc

    def _build_executive_summary(self, kpis: Dict[str, Any], heading_style, styles):
        elements = []

        elements.append(Paragraph("Executive Summary", heading_style))

        summary_text = f"""
        This report provides an operational overview of incident and support activity.
        A total of <b>{kpis['total_tickets']}</b> tickets were analyzed, with an average
        resolution time of <b>{kpis['avg_resolution_time']:.2f} hours</b>.
        {kpis['sla_compliance_rate']:.1f}% of tickets were resolved within SLA.
        The analysis highlights workload distribution, resolution efficiency, and
        potential bottlenecks affecting support performance.
        """

        elements.append(Paragraph(summary_text, styles["Normal"]))
        elements.append(Spacer(1, 20))

        return elements

    def _build_kpi_table(self, kpis: Dict[str, Any], heading_style):
        elements = []

        elements.append(Paragraph("Key Support KPIs", heading_style))

        kpi_data = [
            ["Metric", "Value"],
            ["Total Tickets", f"{kpis['total_tickets']}"],
            ["Average Resolution Time (hrs)", f"{kpis['avg_resolution_time']:.2f}"],
            ["Median Resolution Time (hrs)", f"{kpis['median_resolution_time']:.2f}"],
            ["SLA Compliance (%)", f"{kpis['sla_compliance_rate']:.1f}%"],
            ["Open Tickets", f"{kpis['open_tickets']}"],
        ]

        if "top_category" in kpis:
            kpi_data.append(["Most Frequent Category", kpis["top_category"]])

        if "slowest_category" in kpis:
            kpi_data.append(
                [
                    "Slowest Resolution Category",
                    f"{kpis['slowest_category']} ({kpis['slowest_category_avg']:.2f} hrs)",
                ]
            )

        table = Table(kpi_data, colWidths=[3.5 * inch, 2 * inch])

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
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
        elements = []

        elements.append(Paragraph("Ticket Data Overview", heading_style))

        # Show only closed tickets in the PDF table for better overview
        closed_tickets_df = clean_df[clean_df["closed_at"].notna()]

        elements.append(
            Paragraph(
                f"Showing first 20 closed tickets of {len(closed_tickets_df)} resolved tickets (from {len(clean_df)} total):",
                styles["Normal"],
            )
        )

        # Select only key columns for better readability
        key_columns = [
            "ticket_id",
            "created_at",
            "category",
            "priority",
            "status",
            "agent",
            "resolution_time_hours",
        ]

        # Filter to only available columns
        available_columns = [
            col for col in key_columns if col in closed_tickets_df.columns
        ]
        sample_df = closed_tickets_df[available_columns].head(20)
        data_list = [sample_df.columns.tolist()] + sample_df.values.tolist()

        table = Table(data_list, repeatRows=1)

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTSIZE", (0, 1), (-1, -1), 7),
                ]
            )
        )

        elements.append(table)
        elements.append(Spacer(1, 20))

        return elements

    def _build_charts_section(self, charts: Dict[str, Path], heading_style):
        elements = []

        if not charts:
            elements.append(Paragraph("Visual Analytics", heading_style))
            elements.append(
                Paragraph(
                    "No charts available for this report.",
                    getSampleStyleSheet()["Normal"],
                )
            )
            return elements

        chart_titles = {
            "tickets_by_category": "Tickets by Category",
            "tickets_by_priority": "Tickets by Priority",
            "avg_resolution_time_by_category": "Average Resolution Time by Category",
            "ticket_status_distribution": "Ticket Status Distribution",
            "tickets_created_vs_resolved": "Tickets Created vs Resolved Over Time",
        }

        # Convert to list to allow indexing
        chart_items = list(charts.items())

        # Process charts in pairs (2 per page)
        for i in range(0, len(chart_items), 2):
            if i > 0:
                elements.append(PageBreak())

            current_chart = chart_items[i]
            next_chart = chart_items[i + 1] if i + 1 < len(chart_items) else None

            # Create layout for 1 or 2 charts
            chart_layout = self._create_chart_layout(
                current_chart, next_chart, chart_titles, heading_style
            )
            elements.append(chart_layout)

        return elements

    def _create_chart_layout(
        self, chart1_info, chart2_info, chart_titles, heading_style
    ):
        """Create layout for 1 or 2 charts vertically stacked"""
        styles = getSampleStyleSheet()

        # Build chart data for vertical table layout
        chart_data = []

        # First chart
        chart1_name, chart1_path = chart1_info
        if chart1_path.exists():
            chart1_title = Paragraph(
                chart_titles.get(chart1_name, chart1_name.replace("_", " ").title()),
                heading_style,
            )
            chart1_image = Image(str(chart1_path), width=6 * inch, height=3.5 * inch)
            chart_data.extend([[chart1_title], [Spacer(1, 10)], [chart1_image]])

        # Second chart (if exists)
        if chart2_info:
            chart2_name, chart2_path = chart2_info
            if chart2_path.exists():
                chart2_title = Paragraph(
                    chart_titles.get(
                        chart2_name, chart2_name.replace("_", " ").title()
                    ),
                    heading_style,
                )
                chart2_image = Image(
                    str(chart2_path), width=6 * inch, height=3.5 * inch
                )
                chart_data.extend(
                    [[Spacer(1, 20)], [chart2_title], [Spacer(1, 10)], [chart2_image]]
                )

        # Create table with proper styling for vertical layout
        table = Table(chart_data, colWidths=[6 * inch])

        # Apply styling to center content
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        return table
