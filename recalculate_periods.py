from global_vars import db
import numpy as np


records = db.records.find()
tasks = db.tasks.find()

task_to_records = {task["task_name"]: [] for task in tasks}

for record in records:
    if record["task_name"] in task_to_records:
        task_to_records[record["task_name"]].append(record["time_completed"])

for task_name, dates in task_to_records.items():
    dates = np.array(dates)
    
