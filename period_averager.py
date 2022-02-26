import pymongo
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

N_SECONDS_IN_DAY = 60 * 60 * 24

alpha = 0.
average = alpha == 0
days = 100

debug = False

with open("db_connection.txt", "r") as db_info:
    connection_info = db_info.readline()
    db = pymongo.MongoClient(connection_info)["task_app_test" if debug else "task_app"]

records = pd.DataFrame(db.records.find({"time_completed": {"$gt": datetime.now() - timedelta(days=days)}}))
by_task = records.groupby(["task_name"])

new_periods = {}

for task_name, df in by_task:
    if len(df) < 2:
        continue

    task = db.tasks.find_one({"task_name": task_name})
    period = task["period"] * N_SECONDS_IN_DAY
    old_period = period / N_SECONDS_IN_DAY
    
    times = list(df["time_completed"])
    time_deltas = map(lambda x: (x[0]-x[1]), zip(times[1:], times[:-1]))
    delta_seconds = np.array([ds for ds in map(lambda dt: dt.total_seconds(), time_deltas) if round(ds) > 10])
    n_nonzero = len(delta_seconds)
    if n_nonzero == 0:
        continue
    weights = np.linspace(0, 1, len(delta_seconds)) if n_nonzero > 1 else np.ones(1)
    weights = weights**2
    # delta_seconds.dot(weights)

    if average:
        # period = sum(delta_seconds)/(n_nonzero)
        period = delta_seconds.dot(weights) / weights.sum()
    else:
        for ds in delta_seconds:
            if round(ds) == 0:
                continue
            period = period * alpha + ds * (1-alpha)
    
    new_periods[task_name] = (period / N_SECONDS_IN_DAY, old_period)

pairs = list(new_periods.items())
pairs.sort(key=lambda x: -(x[1][0]-x[1][1])/x[1][1])

print("Over %d days, " % days, end="")
if average:
    print("AVERAGED")
else:
    print("EMA: alpha=%f" % alpha)

for task, periods in pairs:
    percent_change = 100*(periods[0]-periods[1])/periods[1]
    print("%40s: %2.1f\t%2.1f\t%3.1f%%" % (task, periods[0], periods[1], percent_change))

    db.tasks.update_one({"task_name": task}, {"$set": {"period": periods[0]}})
