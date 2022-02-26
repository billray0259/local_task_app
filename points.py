from dash_bootstrap_components._components.Collapse import Collapse
from dash_bootstrap_components._components.Select import Select
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from pandas._config.config import options
from global_vars import app, db
import plotly.express as px
import pandas as pd
from datetime import datetime, time, timedelta
import dash
from collections import defaultdict

layout = html.Div([
    html.H1("Points", id="points_heading"),
    dbc.Label("Graph Type"),
    dbc.Select(
        id="graph_type",
        value = "average",
        options = [
            {"label": "Average Points Per day", "value": "average"},
            {"label": "Total Points", "value": "total"},
            {"label": "Total Time", "value": "time"},
        ]
    ),
    dcc.Graph(id="ppd_graph"),
    
    dbc.Form([
        dbc.Row([
            dbc.Col([
                dbc.Label("Group by", className="mr-3"),
                dbc.Select(id="group_by",
                    value="time_period",
                    options=[
                        {"label": "Time Period", "value": "time_period"},
                        {"label": "Task", "value": "task"},
                    ],
                    className="mr-3"
                ),
            ], width=4),
            dbc.Col(
                dbc.Collapse([
                    dbc.Label("Period", className="mr-3"),
                    dbc.Input(id="group_days", value=7, type="number", className="mr-3")
                ], id="time_period_input", is_open=True),
            width=4)
        ], className="mb-4"), 
        dbc.Row(
            dbc.Col([
                dbc.Label("Total days", className="mr-3"),
                dbc.Input(id="total_days", value=28, type="number", className="mr-3")
            ], width=4)
        )
    ]),
    dcc.Graph(id="points_graph")
])

@app.callback(
    Output("ppd_graph", "figure"),
    Input("graph_type", "value")
)
def load_ppd_graph(graph_type):
    users = list(db.users.find({"active": True}))

    user_ids = set()
    users_active_seconds = {}
    id_to_display_name = {}
    for user in users:
        active_seconds = user["active_seconds"]
        active_seconds += (datetime.now() - user["last_activated"]).total_seconds()
        user_id = user["_id"]
        users_active_seconds[user_id] = active_seconds
        id_to_display_name[user_id] = user["name"]
        user_ids.add(user_id)

    records = db.records.find()
    records = [record for record in records if record["user"] in user_ids]

    total_points = 0
    users_points = defaultdict(lambda: 0)  # maps user_id to total points from all records
    for record in records:
        total_points += record["points"]
        users_points[record["user"]] += record["points"]

    # users_pps = {}
    display_names = []
    daily_points = []
    total_points = []
    total_time = []
    for user_id in user_ids:
        points = users_points[user_id]
        total_points.append(100 * points)
        active_seconds = users_active_seconds[user_id]
        total_time.append(round(active_seconds / (60 * 60 * 24)))
        display_names.append(id_to_display_name[user_id])
        daily_points.append(100 * points / active_seconds * 60 * 60 * 24)
    
    df = pd.DataFrame({
        "User": display_names,
        "Daily Points": daily_points,
        "Total Points": total_points,
        "Total Time": total_time
    })

    df.sort_values("User", inplace=True)

    value = "Daily Points"
    if graph_type == "total":
        value = "Total Points"
    elif graph_type == "time":
        value = "Total Time"


    return px.bar(
        df,
        x="User",
        y=value,
        color="User",
    )

@app.callback(
    Output("points_graph", "figure"),
    Output("time_period_input", "is_open"),
    Input("group_by", "value"),
    Input("group_days", "value"),
    Input("total_days", "value"),
)
def load_graph(group_by, group, total):
    if group is None or total is None or group <= 0:
        return dash.no_update, dash.no_update
    
    start = datetime.now() - timedelta(days=total)
    

    users = list(db.users.find({"active": True}))


    # user_ids = set()
    users_active_seconds = {}
    for user in users:
        active_seconds = user["active_seconds"]
        active_seconds += (datetime.now() - user["last_activated"]).total_seconds()
        user_id = user["_id"]
        users_active_seconds[user_id] = active_seconds
        # user_ids.add(user_id)

    # records = db.records.find()
    # records = [record for record in records if record["user"] in user_ids]

    # total_points = 0
    # users_points = defaultdict(lambda: 0)  # maps user_id to total points from all records
    # for record in records:
    #     total_points += record["points"]
    #     users_points[record["user"]] += record["points"]
    
    # users_pps = {}
    # for user_id in user_ids:
    #     points = users_points[user_id]
    #     active_seconds = users_active_seconds[user_id]
    #     users_pps[user_id] = points / active_seconds

    points = []
    weeks = []
    users = []
    tasks = []
    times = []
    
    max_seconds = max(users_active_seconds.values())
    
    records = db.records.find({"time_completed": {"$gt": start}})
    id_to_user = {}
    for record in records:
        if record["user"] in id_to_user:
            user = id_to_user[record["user"]]
        else:
            user = db.users.find_one({"_id": record["user"]})
            if not user["active"]:
                continue
            id_to_user[record["user"]] = user
        users.append(user["name"])
        time_modifier = max_seconds / users_active_seconds[record["user"]]
        points.append(round(record["points"] * 100 * time_modifier))
        days = (record["time_completed"] - start).total_seconds() / (60*60*24)
        weeks.append(int(days/group)+1)
        tasks.append(record["task_name"])
        times.append(record["time_completed"].strftime("%-m/%d %-I:%M %p"))

    period_label = "%d day periods" % group

    df = pd.DataFrame({
        "Points": points,
        period_label: weeks,
        "User": users,
        "Task": tasks,
        "Time": times
    })

    df.sort_values("User", inplace=True)

    x_label = period_label
    if group_by == "task":
        x_label = "Task"

    return px.bar(
        df,
        x=x_label,
        y="Points",
        color="User",
        barmode="group",
        hover_data=["Task", "Time"],
    ), group_by == "time_period"
