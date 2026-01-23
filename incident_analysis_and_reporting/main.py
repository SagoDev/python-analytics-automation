"""
Incident analysis report
A tool that transforms raw sales data into a ready-to-use executive report
"""

from agents.scheduler import Scheduler

scheduler = Scheduler(input_file="input/ticket_sample.csv")

# Single run
scheduler.run_pipeline()

# Run every day at 09:00
# scheduler.schedule_daily("09:00")

# Or run every 3 days
# scheduler.schedule_every_n_days(3)
