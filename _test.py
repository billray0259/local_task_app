from global_vars import db
from todo import calculate_points
import numpy as np

tasks = list(db.tasks.find())
users = list(db.users.find({"active": True}))

points = np.zeros(len(tasks))
periods = np.zeros(len(tasks))

for i, task in enumerate(tasks):
    points[i] = calculate_points(task, users)
    periods[i] = task["period"]

ppd = points / periods

print(100*ppd.sum()/len(users))
