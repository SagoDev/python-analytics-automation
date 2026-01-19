"""
RFM Clients Analysis
A tool that transforms raw clients data into a ready-to-use executive RFM report
"""

from scheduler import Scheduler

scheduler = Scheduler(input_file="input/orders_sample.csv")

# Single run
scheduler.run_pipeline()

# Run every day at 09:00
# scheduler.schedule_daily("09:00")

# Or run every 3 days
# scheduler.schedule_every_n_days(3)
