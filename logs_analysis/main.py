"""
Sales Report Automation
A tool that transforms raw sales data into a ready-to-use executive report
"""

from agents.scheduler import Scheduler

scheduler = Scheduler(file_path=["input/logs_sample.log"])

# Single run
scheduler.run_pipeline()

# Run every day at 09:00
# scheduler.schedule_daily("09:00")

# Or run every 3 days
# scheduler.schedule_every_n_days(3)
