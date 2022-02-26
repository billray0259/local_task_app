import dash
from dash_bootstrap_components._components.ButtonGroup import ButtonGroup
from dash_bootstrap_components._components.CardBody import CardBody
from dash_bootstrap_components._components.CardHeader import CardHeader
from dash_bootstrap_components._components.Label import Label
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH
from global_vars import app, db
import json
from bson.objectid import ObjectId
from datetime import date, datetime, timedelta

# layout = html.Div([
#     dcc.Store(id="selected_task"),
#     html.H1("Create Task"),
#     html.Div(id="tasks_response"),
#     dcc.Input(id="task_name", type="text", placeholder="Task Name"),
#     dcc.Textarea(id="desc", placeholder="Task Description"),
#     dcc.Input(id="period", type="number", placeholder="Period in Days"),
#     dbc.Button("Add", id="add_task"),
#     dbc.Button("Clear", id="clear_task"),
#     dbc.Button("Delete", id="delete_task"),
#     html.Div(id="task_list")
# ])

def get_task_card(task):
    repeat_phrase = "Repeats once a day"
    if task["period"] != 1:
        repeat_phrase = "Repeats every %.2g days" % task["period"]
    card = dbc.Card([
            dbc.CardHeader(task["task_name"]),
            dbc.CardBody([
                dbc.Row(dbc.Col(html.P(task["desc"], "card-text"))),
                dbc.Row([
                    dbc.Col(repeat_phrase),
                    dbc.Col("Completed: %s" % task["last_completed"].strftime("%-m/%d %I:%M %p")),
                ])
            ])
        ], className="mb-3"),
        
    return card

# def get_task_divs():
#     tasks = db.tasks.find().sort("period")
#     task_divs = []
#     for task in tasks:
#         print(task["task_name"])
#         task_divs.append(
#             html.Div([
#                 dbc.Collapse(get_task_card(task), id={
#                     "type": "content_task",
#                     "id": str(task["_id"])
#                 }, is_open=True),
#                 dbc.Collapse(get_form_task(task), id={
#                     "type": "form_task",
#                     "id": str(task["_id"])
#                 }, is_open=True),
#             ])
#         )
#     return task_divs

def get_form_task(task):
    if task is None:
        task_name = ""
        desc = ""
        period = ""
        group = ""
        str_id = "new_task"
        percent_period_input = dbc.FormGroup([
            dbc.Label("Percent of period"),
            dbc.Input(value=round(0), type="number", min=0, id={"type": "input_completed", "id": str_id})
        ])
        true_button = dbc.Button("Save", id="update_new_task", size="sm", color="primary", className="mr-2")
        false_button = dbc.Button("Close", id="close_new_task", size="sm")
    else:
        task_name = task["task_name"]
        desc = task["desc"]
        period = task["period"]
        str_id = str(task["_id"])

        group = ""
        if "group" in task:
            group = task["group"]

        time_since_last_completion = datetime.now() - task["last_completed"]
        period_delta = timedelta(days=period)
        percent_of_period = time_since_last_completion.total_seconds()/period_delta.total_seconds()
        percent_period_input = dbc.FormGroup([
            dbc.Label("Percent of period"),
            dbc.Input(value=round(percent_of_period*100), type="number", min=0, id={"type": "input_completed", "id": str_id})
        ])

        true_button = dbc.Button("Update", id={"type": "update", "id": str_id}, color="primary", className="mr-2", size="sm")
        false_button = dbc.Button("Delete", id={"type": "delete", "id": str_id}, color="danger", size="sm")

    form_task = dbc.Form(
        dbc.Card([
            dbc.CardHeader(
                dbc.Row([
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.Label("Task Name"),
                            dbc.Input(value=task_name, type="text", id={"type": "input_task_name", "id": str_id})
                        ]),
                    ]),
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.Label("Task Group"),
                            dbc.Input(value=group, type="text", id={"type": "input_group", "id": str_id})
                        ])
                    ]),
                ]),
            ),
            dbc.CardBody([
                dbc.Row(
                    dbc.Col(
                        dbc.FormGroup([
                            dbc.Label("Task Description"),
                            dbc.Input(value=desc, type="text", id={"type": "input_desc", "id": str_id})
                        ])
                    )
                ),
                dbc.Row([
                    dbc.Col(
                        dbc.FormGroup([
                            dbc.Label("Period in days"),
                            dbc.Input(value=period, type="number", id={"type": "input_period", "id": str_id})
                        ])
                    ),
                    dbc.Col(
                        percent_period_input
                    )
                ]),
                dbc.Row([
                    dbc.Col([
                        true_button,
                        false_button,
                    ])
                ])
            ])
        ], className="mb-3"),
        id={
            "type": "task",
            "id": str_id
        })
    return form_task


def get_task_divs():
    tasks = db.tasks.find().sort("period")
    task_divs = []
    for task in tasks:
        str_id = str(task["_id"])
        task_divs.append(
            html.Div([
                html.Div(
                    dbc.Collapse(get_task_card(task), id={
                        "type": "content_task",
                        "id": str_id
                    }, is_open=True),
                    id={"type": "content_task_div", "id": str_id},
                ),
                dbc.Collapse(get_form_task(task), id={
                    "type": "form_task",
                    "id": str_id
                }, is_open=False),
                html.Div(id={
                    "type": "task_alert",
                    "id": str_id
                }),
            ])
        )
    return task_divs

layout = html.Div([
    dcc.Store(id="selected_task"),
    html.H1("Modify Tasks"),
    dbc.Button("New Task", id="new_task", color="success", className="mb-4"),
    dbc.Collapse(get_form_task(None), id="new_task_collapse"),
    html.Div(get_task_divs(), id="task_list")
])


@app.callback(
    Output("new_task_collapse", "is_open"),
    Output("new_task_collapse", "children"),
    Output("task_list", "children"),
    Input("new_task", "n_clicks"),
    Input("update_new_task", "n_clicks"),
    Input("close_new_task", "n_clicks"),
    State({"type": "input_task_name", "id":"new_task"}, "value"),
    State({"type": "input_group", "id":"new_task"}, "value"),
    State({"type": "input_desc", "id": "new_task"}, "value"),
    State({"type": "input_period", "id": "new_task"}, "value"),
    State({"type": "input_completed", "id": "new_task"}, "value"),
    State("session", "data"),
    prevent_initial_call=True
)
def new_task(new_task_clicks, update_clicks, close_clicks, task_name, group, desc, period, completed, session_data):
    event = dash.callback_context.triggered[0]["prop_id"]
    if event == ".":
        return dash.no_update, dash.no_update, dash.no_update
    elif event == "new_task.n_clicks":
        return True, dash.no_update, dash.no_update
    elif event == "close_new_task.n_clicks":
        return False, get_form_task(None), dash.no_update

    user = db.users.find_one(session_data)

    period_delta = timedelta(days=period * completed/100)

    document = {
        "task_name": task_name,
        "group": group,
        "desc": desc,
        "period": period,
        "modified_by": user["_id"],
        "last_completed": datetime.now() - period_delta
    }
    result = db.tasks.insert_one(document)

    users = db.users.find()
    for user in users:
        preferences = []
        if "preferences" in user:
            preferences = user["preferences"]
        preferences.append({"task": result.inserted_id, "preference": 1})
        db.users.update_one({"_id": user["_id"]}, {"$set": {"preferences": preferences}})

    return False, get_form_task(None), get_task_divs()
    

@app.callback(
    Output({"type": "form_task", "id": MATCH}, "is_open"),
    Output({"type": "task_alert", "id": MATCH}, "children"),
    Output({"type": "content_task_div", "id": MATCH}, "children"),
    Input({"type": "content_task_div", "id": MATCH}, "n_clicks"),
    Input({"type": "update", "id": MATCH}, "n_clicks"),
    Input({"type": "delete", "id": MATCH}, "n_clicks"),
    State({"type": "form_task", "id":MATCH}, "id"),
    State({"type": "input_task_name", "id": MATCH}, "value"),
    State({"type": "input_group", "id": MATCH}, "value"),
    State({"type": "input_desc", "id": MATCH}, "value"),
    State({"type": "input_period", "id": MATCH}, "value"),
    State({"type": "input_completed", "id": MATCH}, "value"),
    State("session", "data"),
    prevent_initial_call=True
)
def update_task(c1, c2, c3, clicked_id, task_name, group, desc, period, completed, session_data):
    event = dash.callback_context.triggered[0]["prop_id"]
    if event == ".":
        return dash.no_update, dash.no_update, dash.no_update
    elif "content_task_div" in event:
        return True, dash.no_update, dash.no_update
    
    alert = dash.no_update
    content_children = dash.no_update
    task_id = ObjectId(clicked_id["id"])
    if "update" in event:
        # task = db.tasks.find_one({"_id": task_id})
        user = db.users.find_one(session_data)
        period_delta = timedelta(days=period * completed/100)

        document = {
            "task_name": task_name,
            "desc": desc,
            "group": group,
            "period": period,
            "modified_by": user["_id"],
            "last_completed": datetime.now() - period_delta
        }
        db.tasks.replace_one({"_id": task_id}, document)
        alert = dbc.Alert("Updated '%s'" % task_name, color="success", duration=2000)
        task = db.tasks.find_one({"_id": task_id})
        content_children = dbc.Collapse(get_task_card(task), id={
            "type": "content_task",
            "id": clicked_id["id"]
        }, is_open=True),

    elif "delete" in event:
        db.tasks.delete_one({"_id": task_id})
        for every_user in db.users.find():
            preferences = every_user["preferences"]
            for i in range(len(preferences)-1, -1, -1):
                if preferences[i]["task"] == task_id:
                    del preferences[i]
                    break
            db.users.update_one({"_id": every_user["_id"]}, {"$set": {"preferences": preferences}})
        alert = dbc.Alert("Deleted '%s'" % task_name, color="success", duration=2000)
        content_children = html.Div()

    return False, alert, content_children
    

@app.callback(
    Output({"type": "content_task", "id": MATCH}, "is_open"),
    Input({"type": "form_task", "id": MATCH}, "is_open"),
    prevent_initial_call=True
)
def update_content_task(form_is_open):
    return not form_is_open

