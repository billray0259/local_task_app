from logging import PlaceHolder
from typing import Match
import dash
from dash_bootstrap_components._components.ButtonGroup import ButtonGroup
from dash_bootstrap_components._components.CardBody import CardBody
from dash_bootstrap_components._components.CardHeader import CardHeader
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL, MATCH
from global_vars import app, db
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import random
from collections import defaultdict



layout = html.Div([
    dcc.Interval(id="grouping_interval", interval=60*1000),
    html.H1("Task Groups"),
    dbc.Button("Add Group", id="add_group"),
    html.Div(id="grouping_contents"),
])


def calculate_points(task, users):
    points = 0

    for every_user in users:
        prefs = every_user["preferences"]
        avg_pref = 0
        for pref in prefs:
            avg_pref += pref["preference"] / len(prefs)
        for pref in prefs:
            if pref["task"] == task["_id"]:
                points += pref["preference"] / avg_pref
                break

    points /= len(users)
    return points


def make_card(task, users):
    task_id = str(task["_id"])
    time_since_last_completion = datetime.now() - task["last_completed"]
    period = timedelta(days=task["period"])
    time_percentage = time_since_last_completion.total_seconds()/period.total_seconds()
    seconds_remaining = period.total_seconds() - time_since_last_completion.total_seconds()
    color = "success"
    if time_percentage > 0.75:
        color = "warning"
    if time_percentage > 1:
        color = "danger"
    label = ""
    if time_percentage > 0.02:
        # label = html.Div("%d%%" % round(100*time_percentage), style={"font-size": "1.7em"})
        abs_seconds = abs(seconds_remaining)
        label = ""
        days = abs_seconds // (60*60*24)
        hours = abs_seconds % (60*60*24) // (60*60)
        minutes = round(abs_seconds % (60*60*24) % (60*60) / 60)

        if days > 0:
            label = "%dd %dh %dm" % (days, hours, minutes)
        elif hours > 0:
            label = "%dh %dm" % (hours, minutes)
        else:
            label = "%dm" % minutes
        if seconds_remaining < 0:
            label += " overdue"
        label = html.Div(label, style={"font-size": "1.7em"})
    
    usernames = []
    names = []

    for every_user in users:
        usernames.append(every_user["username"])
        names.append(every_user["name"])

    points = calculate_points(task, users)

    helper_checklist_options = []
    for i in range(len(usernames)):
        helper_checklist_options.append({
            "label": names[i],
            "value": usernames[i]
        })
    
    return dbc.Collapse(
        dbc.Card([
            dbc.CardHeader(
                dbc.Row([
                    dbc.Col(
                        html.H5(task["task_name"])
                    ),
                    dbc.Col(
                        html.H5("%d points" % round(points*100))
                    )
                ])
            ),
            dbc.CardBody([
                html.P(task["desc"]),
                dbc.Progress(label, value=100*time_percentage, color=color, className="mb-3", style={
                    "height": "2em"
                }),
                dbc.Collapse([
                    html.H6("Contributors"),
                    dbc.Checklist(options=helper_checklist_options, id={
                        "type": "helper_list",
                        "task": task_id
                    })
                ], id={
                    "type": "helper_collapse",
                    "task": task_id
                }, className="mb-3"),
                dbc.Button("Add Helper", id={
                    "type": "helper_button",
                    "task": task_id
                }, color="primary", className="mr-2"),
                dbc.Button("Complete", id={
                    "type": "grouping_task",
                    "task": task_id,
                    "points": points
                }, color="primary", disabled=True)
            ])
        ], className="mb-4"), is_open=True, id={
            "type": "grouping_collapse",
            "task": task_id
        }), seconds_remaining, time_percentage


@app.callback(
    Output("grouping_contents", "children"),
    Input("add_group", "n_clicks"),
    Input("grouping_interval", "n_intervals")
)
def update_grouping_cards(clicks, intervals):

    event = dash.callback_context.triggered[0]["prop_id"]
    if event == "add_group.n_clicks":
        
    tasks = list(db.tasks.find())
    users = list(db.users.find({"active": True}))
    groups = list(db.groups.find())


    return "groups"

@app.callback(
    Output({"type": "helper_collapse", "task": MATCH}, "is_open"),
    Output({"type": "helper_button", "task": MATCH}, "children"),
    Output({"type": "grouping_task", "task": MATCH, "points": ALL}, "disabled"),
    Input({"type": "helper_button", "task": MATCH}, "n_clicks"),
    State({"type": "helper_collapse", "task": MATCH}, "is_open"),
    prevent_initial_call=True
)
def toggle_helper(clicks, is_open):
    helper_open = not is_open
    helper_button_text = "Close" if not is_open else "Add Helper"
    return helper_open, helper_button_text, (False,)


@app.callback(
    Output({"type": "grouping_collapse", "task": MATCH}, "is_open"),
    Input({"type": "grouping_task", "task": MATCH, "points": ALL}, "n_clicks"),
    Input({"type": "grouping_task", "task": MATCH, "points": ALL}, "id"),
    State({"type": "helper_list", "task": MATCH}, "value"),
    prevent_initial_call=True
)
def complete_task(clicks, task_info, usernames):
    event = dash.callback_context.triggered[0]
    if event["value"] is None:
        return True
    task_id = ObjectId(task_info[0]["task"])
    task = db.tasks.find_one({"_id": task_id})
    points = task_info[0]["points"]
    # usernames = map(lambda div: div["props"]["id"]["username"], helper_list)
    completed_time = datetime.now()
    if len(usernames) > 0:
        queries = list(map(lambda un: {"username": un}, usernames))
        users = list(db.users.find({"$or": queries}))
        records = []
        for user in users:
            records.append({
                "user": user["_id"],
                "task_name": task["task_name"],
                "time_completed": completed_time,
                "points": points / len(users),
                "hidden": False
            })
        db.records.insert(records)
    db.tasks.update_one({"_id": task_id}, {"$set": {"last_completed": completed_time}})
    return False
