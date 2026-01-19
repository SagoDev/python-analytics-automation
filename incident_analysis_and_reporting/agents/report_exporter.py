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
        elements.append(
            Paragraph(
                f"Showing first 20 rows of {len(clean_df)} analyzed tickets:",
                styles["Normal"],
            )
        )

        sample_df = clean_df.head(20)
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

        for i, (chart_name, chart_path) in enumerate(charts.items()):
            if chart_path.exists():
                if i > 0:
                    elements.append(PageBreak())

                elements.append(
                    Paragraph(
                        chart_titles.get(
                            chart_name, chart_name.replace("_", " ").title()
                        ),
                        heading_style,
                    )
                )
                elements.append(Spacer(1, 20))
                elements.append(Image(str(chart_path), width=6 * inch, height=4 * inch))
            else:
                self.logger.warning("Chart file not found: %s", chart_path)

        return elements
