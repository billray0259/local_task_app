from datetime import datetime, timedelta
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from global_vars import app, db
import hashlib
import os


# layout = html.Div([
#     dcc.Location(id="register_location"),
#     html.H1("Create Account"),
#     html.Div(id="register_response"),
#     html.Div(dcc.Input(id="name", type="text", placeholder="Name")),
#     html.Div(dcc.Input(id="username", type="text", placeholder="Username")),
#     html.Div(dcc.Input(id="password", type="password", placeholder="Password")),
#     html.Div(dcc.Input(id="confirm_password", type="password", placeholder="Confirm Password")),
#     html.Div(dbc.Button("Submit", id="submit"))
# ])

layout = html.Div([
    dcc.Location(id="register_location"),
    html.H1("Create Account"),
    dbc.Form([
        dbc.FormGroup([
            dbc.Label("Name", className="mr-2"),
            dbc.Input(id="name", type="text", placeholder="Enter Name")
        ], className="mr-3"),
        dbc.FormGroup([
            dbc.Label("Username", className="mr-2"),
            dbc.Input(id="register_username", type="text", placeholder="Enter Username")
        ], className="mr-3"),
        dbc.FormGroup([
            dbc.Label("Password", className="mr-2"),
            dbc.Input(id="register_password", type="password", placeholder="Enter Password")
        ], className="mr-3"),
        dbc.FormGroup([
            dbc.Input(id="confirm_password", type="password", placeholder="Confirm Password")
        ], className="mr-3"),
        html.Div(id="register_response"),
        dbc.Button("Submit", id="register_submit", color="primary")
    ]),
])


@app.callback(
    Output("register_response", "children"),
    Output("register_location", "pathname"),
    Input("register_submit", "n_clicks"),
    State("register_username", "value"),
    State("register_password", "value"),
    State("name", "value"),
    State("confirm_password", "value")
)
def on_sumbit(submit_clicks, username, password, name, confirm_password):
    if username is None or password is None or name is None or confirm_password is None:
        return [dash.no_update] * 2
    
    if password != confirm_password:
        error = dbc.Alert("Passwords do not match", color="danger")
        return error, dash.no_update
    
    user = db.users.find_one({"username": username})
    if user is not None:
        error = dbc.Alert("The username '%s' is already in use" % username, color="danger")
        return error, dash.no_update
    
    salt = os.urandom(32)
    password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    
    preferences = []

    users = list(db.users.find())

    for task in db.tasks.find():
        avg_pref = 0
        for every_user in users:
            for pref in every_user["preferences"]:
                if pref["task"] == task["_id"]:
                    avg_pref += pref["preference"]
        avg_pref /= len(users)
        preferences.append({
            "task": task["_id"],
            "preference": avg_pref
        })

    db.users.insert_one({
        "name": name,
        "username": username,
        "password": password,
        "salt": salt,
        "preferences": preferences,
        "active": True,
        "last_activated": datetime.now(),
        "active_seconds": 0
    })
    
    return "", "/login"
