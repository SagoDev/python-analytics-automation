"""Chart Generator Class"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


class ChartsGenerator:
    """
    Generates charts for incident and support analysis.
    """

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _save_chart(self, filename: str) -> Path:
        path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        return path

    def tickets_by_category(self, df: pd.DataFrame) -> Path:
        """
        Bar chart: number of tickets per category.
        """
        counts = df["category"].value_counts()

        counts.plot(kind="bar", title="Tickets by Category")
        plt.xlabel("Category")
        plt.ylabel("Number of Tickets")

        return self._save_chart("tickets_by_category.png")

    def tickets_by_priority(self, df: pd.DataFrame) -> Path:
        """
        Bar chart: number of tickets per priority.
        """
        counts = df["priority"].value_counts()

        counts.plot(kind="bar", title="Tickets by Priority")
        plt.xlabel("Priority")
        plt.ylabel("Number of Tickets")

        return self._save_chart("tickets_by_priority.png")

    def avg_resolution_time_by_category(self, df: pd.DataFrame) -> Path:
        """
        Bar chart: average resolution time by category.
        """
        avg_time = (
            df.groupby("category")["resolution_time_hours"]
            .mean()
        ).sort_values(ascending=False)

        avg_time.plot(kind="bar", title="Average Resolution Time by Category")
        plt.xlabel("Category")
        plt.ylabel("Hours")

        return self._save_chart("avg_resolution_time_by_category.png")

    def ticket_status_distribution(self, df: pd.DataFrame) -> Path:
        """
        Pie chart: ticket status distribution.
        """
        counts = df["status"].value_counts()

        counts.plot(kind="pie", autopct="%1.1f%%", title="Ticket Status Distribution")
        plt.ylabel("")

        return self._save_chart("ticket_status_distribution.png")

    def tickets_created_vs_resolved(self, df: pd.DataFrame) -> Path:
        """
        Line chart: tickets created vs resolved over time.
        """
        # Group by date for created tickets
        df_copy = df.copy()
        created_dates = pd.to_datetime(df_copy['created_at']).dt.date
        created_tickets = df_copy.groupby(created_dates).size().to_frame("created")
        
        # Group by date for resolved tickets
        resolved_df = df[df["status"] == "closed"].copy()
        resolved_dates = pd.to_datetime(resolved_df['closed_at']).dt.date
        resolved_tickets = resolved_df.groupby(resolved_dates).size().to_frame("resolved")
        
        # Combine the data
        timeline = created_tickets.join(resolved_tickets, how="outer").fillna(0)
        timeline.index = pd.to_datetime(timeline.index)

        timeline.plot(title="Tickets Created vs Resolved Over Time")
        plt.xlabel("Date")
        plt.ylabel("Tickets")

        return self._save_chart("tickets_created_vs_resolved.png")

    def tickets_by_team(self, df: pd.DataFrame) -> Path:
        """
        Bar chart: number of tickets per team.
        """
        counts = df["team"].value_counts()

        counts.plot(kind="bar", title="Tickets by Team")
        plt.xlabel("Team")
        plt.ylabel("Number of Tickets")
        plt.xticks(rotation=45)

        return self._save_chart("tickets_by_team.png")

    def tickets_by_agent(self, df: pd.DataFrame) -> Path:
        """
        Bar chart: number of tickets per agent.
        """
        counts = df["agent"].value_counts()

        counts.plot(kind="bar", title="Tickets by Agent")
        plt.xlabel("Agent")
        plt.ylabel("Number of Tickets")
        plt.xticks(rotation=45)

        return self._save_chart("tickets_by_agent.png")

    def avg_resolution_time_by_priority(self, df: pd.DataFrame) -> Path:
        """
        Bar chart: average resolution time by priority.
        """
        avg_time = (
            df.groupby("priority")["resolution_time_hours"]
            .mean()
        ).sort_values(ascending=False)

        avg_time.plot(kind="bar", title="Average Resolution Time by Priority")
        plt.xlabel("Priority")
        plt.ylabel("Hours")

        return self._save_chart("avg_resolution_time_by_priority.png")