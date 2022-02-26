import dash
from dash_bootstrap_components._components.ButtonGroup import ButtonGroup
from dash_bootstrap_components._components.CardBody import CardBody
from dash_bootstrap_components._components.CardHeader import CardHeader
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL, MATCH
from flask.globals import session
from global_vars import app, db
import json
from bson.objectid import ObjectId
from datetime import datetime, timedelta

def get_todo_cards():
    tasks = db.tasks.find()
    users = list(db.users.find())
    cards = []
    for task in tasks:
        time_since_last_completion = datetime.now() - task["last_completed"]
        period = timedelta(days=task["period"])
        time_percentage = time_since_last_completion.total_seconds()/period.total_seconds()
        color = "success"
        if time_percentage > 0.75:
            color = "warning"
        if time_percentage > 1:
            color = "danger"
        label = ""
        if time_percentage > 0.02:
            label = html.Div("%d%%" % round(100*time_percentage), style={"font-size": "1.7em"})
        points = 0
        for user in users:
            prefs = user["preferences"]
            for pref in prefs:
                if pref["task"] == task["_id"]:
                    points += pref["preference"]
                    break
        points *= time_percentage
        points /= len(users)
        card = dbc.Card([
            dbc.CardHeader(html.H5("%s (%d points)" % (task["task_name"], round(points*100)))),
            dbc.CardBody([
                html.P(task["desc"]),
                dbc.Progress(label, value=100*time_percentage, color=color, className="mb-3", style={
                    "height": "2em"
                }),
                html.Div(id={
                    "type": "helper_list",
                    "task": str(task["_id"])
                }),
                dbc.Button("Add Helper", id={
                    "type": "helper_button",
                    "task": str(task["_id"])
                }, color="primary", className="mr-2"),
                dbc.Button("Complete", id={
                    "type": "todo_task",
                    "task": str(task["_id"]),
                    "points": points
                }, color="primary")
            ])
        ], className="mb-4")
        cards.append((card, time_percentage))
    # cards = [todo_card(task, users) for task in tasks]
    cards.sort(key=lambda t: t[1], reverse=True)
    cards = [card[0] for card in cards]
    return html.Div(cards)

def layout():
    return html.Div([
        html.H1("To Do"),
        html.Div(
            get_todo_cards(),
        id="todo_cards")
    ])

@app.callback(
    Output({"type": "helper_list", "task": MATCH}, "children"),
    Input({"type": "helper_button", "task": MATCH}, "n_clicks"),
    State({"type": "helper_button", "task": MATCH}, "id"),
    State({"type": "helper_list", "task": MATCH}, "children"),
    State("session", "data")
)
def add_helper_input(clicks, button_id, children, session_data):
    event = dash.callback_context.triggered[0]
    if event["value"] is None:
        return dash.no_update
    user = db.users.find_one(session_data)
    if children is None:
        children = [
            html.H6("Contributors:"),
            dbc.Row(dbc.Col(user["name"]))
        ]
    # else:
    #     children = children[:-1]
    children.append(
        dbc.Row([
            dbc.Col(dbc.Input(placeholder="Enter Username", id={
                "type": "helper_input",
                "id": button_id["task"] + str(len(children)),
            })),
            dbc.Col(dbc.Button("Add", id={
                "type": "helper_add",
                "id": button_id["task"] + str(len(children)),
            }))
        ], className="mb-3", id={
            "type": "helper_group",
            "id": button_id["task"] + str(len(children)),
        })
    )
    return children

@app.callback(
    Output({"type": "helper_group", "id": MATCH}, "children"),
    Input({"type": "helper_add", "id": MATCH}, "n_clicks"),
    State({"type": "helper_input", "id": MATCH}, "value")
)
def add_helper(clicks, username):
    user = db.users.find_one({"username": username})
    if user is None:
        return dash.no_update
    else:
        return dbc.Col(user["name"])
    

@app.callback(
    Output("todo_cards", "children"),
    Input({"type": "todo_task", "task": ALL, "points": ALL}, "n_clicks"),
    State("session", "data")
)
def complete_task(clicks, session_data):
    event = dash.callback_context.triggered[0]
    if event["value"] is None:
        return dash.no_update
    try:
        task_info = json.loads(event["prop_id"].rpartition(".")[0])
    except json.decoder.JSONDecodeError:
        return dash.no_update

    task_id = ObjectId(task_info["task"])
    task = db.tasks.find_one({"_id": task_id})
    user = db.users.find_one(session_data)

    completed_time = datetime.now()

    record = {
        "user": user["_id"],
        "task_name": task["task_name"],
        "time_completed": completed_time,
        "points": task_info["points"],
        "hidden": False
    }
    db.records.insert_one(record)
    db.tasks.update_one({"task": task_id}, {"$set": {"last_completed": completed_time}})
    return get_todo_cards()
