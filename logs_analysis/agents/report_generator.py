"""Report Generator"""

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
    Exports automated log analysis reports to PDF format including:
    - Executive summary with operational KPIs
    - Log data overview
    - Anomaly detection insights
    - Visual analytics (charts)
    """

    def __init__(self, output_dir: str | Path = "outputs/reports") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(__name__)

    def export_to_pdf(
        self,
        clean_df: pd.DataFrame,
        kpis: Dict[str, Any],
        charts: Dict[str, Path],
        file_name: str = "log_analysis_report.pdf",
    ) -> Path:
        """
        Export the log analysis report to a PDF file.
        """
        self.logger.info("Starting log analysis PDF export: %s", file_name)

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
                "Title",
                parent=styles["Heading1"],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.darkblue,
                alignment=1,
            )

            heading_style = ParagraphStyle(
                "Heading",
                parent=styles["Heading2"],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.darkblue,
                spaceBefore=20,
            )

            story = []

            # Title
            story.append(Paragraph("Log Analysis Report", title_style))
            story.append(
                Paragraph(
                    f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}",
                    styles["Normal"],
                )
            )
            story.append(Spacer(1, 20))

            # Executive Summary
            story.extend(self._build_executive_summary(kpis, heading_style, styles))

            # KPI Table
            story.extend(self._build_kpi_table(kpis, heading_style))

            story.append(PageBreak())

            # Log Data Overview
            story.extend(self._build_data_overview(clean_df, heading_style, styles))

            story.append(PageBreak())

            # Charts
            story.extend(self._build_charts_section(charts, heading_style))

            doc.build(story)

            self.logger.info("Log analysis PDF successfully exported: %s", file_path)
            return file_path

        except Exception as exc:
            self.logger.exception("Error exporting log analysis PDF")
            raise PDFExportError(str(exc)) from exc

    # ---------- Sections ----------

    def _build_executive_summary(self, kpis: Dict[str, Any], heading_style, styles):
        elements = [Paragraph("Executive Summary", heading_style)]

        summary_text = f"""
        This report provides an automated analysis of system and application logs.
        A total of <b>{kpis['total_logs']}</b> log entries were processed.
        <b>{kpis['error_logs']}</b> entries correspond to ERROR or CRITICAL levels,
        resulting in an error rate of <b>{kpis['error_rate']:.2%}</b>.
        The analysis highlights temporal patterns, error concentration by service,
        and anomalous activity spikes for operational monitoring.
        """

        elements.append(Paragraph(summary_text, styles["Normal"]))
        elements.append(Spacer(1, 20))
        return elements

    def _build_kpi_table(self, kpis: Dict[str, Any], heading_style):
        elements = [Paragraph("Key Log KPIs", heading_style)]

        data = [
            ["Metric", "Value"],
            ["Total Logs", f"{kpis['total_logs']}"],
            ["Error Logs", f"{kpis['error_logs']}"],
            ["Error Rate", f"{kpis['error_rate']:.2%}"],
        ]

        table = Table(data, colWidths=[3.5 * inch, 2 * inch])
        table.setStyle(self._default_table_style())

        elements.append(table)
        elements.append(Spacer(1, 20))
        return elements

    def _build_data_overview(self, df: pd.DataFrame, heading_style, styles):
        elements = [Paragraph("Log Data Overview", heading_style)]

        elements.append(
            Paragraph(
                f"Showing first 20 log entries from a total of {len(df)} records:",
                styles["Normal"],
            )
        )

        sample_df = df[["timestamp", "level", "service", "message"]].head(20)

        table_data = [sample_df.columns.tolist()] + sample_df.values.tolist()
        table = Table(table_data, repeatRows=1)
        table.setStyle(self._compact_table_style())

        elements.append(table)
        elements.append(Spacer(1, 20))
        return elements

    def _build_charts_section(self, charts: Dict[str, Path], heading_style):
        elements = [Paragraph("Visual Analytics", heading_style)]

        if not charts:
            elements.append(
                Paragraph(
                    "No charts available for this report.",
                    getSampleStyleSheet()["Normal"],
                )
            )
            return elements

        for chart_name, chart_path in charts.items():
            if not chart_path.exists():
                continue

            elements.append(
                Paragraph(chart_name.replace("_", " ").title(), heading_style)
            )
            elements.append(Image(str(chart_path), width=6 * inch, height=3.5 * inch))
            elements.append(Spacer(1, 20))

        return elements

    # ---------- Styles ----------

    @staticmethod
    def _default_table_style():
        return TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )

    @staticmethod
    def _compact_table_style():
        return TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTSIZE", (0, 1), (-1, -1), 7),
            ]
        )
