from typing import Container
import dash
from dash_bootstrap_components._components.FormFeedback import FormFeedback
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from global_vars import app, db
import util
import uuid


layout = html.Div([
    dcc.Location(id="login_location"),
    html.H1("Login"),
    dbc.Form([
        dbc.FormGroup([
            dbc.Label("Username", className="mr-2"),
            dbc.Input(id="login_username", type="text", placeholder="Enter Username")
        ], className="mr-3"),
        dbc.FormGroup([
            dbc.Label("Password", className="mr-2"),
            dbc.Input(id="login_password", type="password", placeholder="Enter Password")
        ], className="mr-3"),
        html.Div(id="login_response"),
        dbc.Button("Submit", id="login_submit", color="primary")
    ]),
    
    # dbc.Row(dbc.Col(html.H1("Login page"))),
    # dbc.Row([
    #     dbc.Col("Username", width=2),
    #     dbc.Col(dbc.Input(id="username", type="text"))
    # ]),
    # dbc.Row([
    #     dbc.Col("Password"),
    #     dbc.Col(dbc.Input(id="password", type="password"))
    # ]),
    # html.Div(id="login_response"),
    # html.Div(dcc.Input(id="username", type="text", placeholder="Username")),
    # html.Div(dcc.Input(id="password", type="password", placeholder="Password")),
    # dbc.Row(dbc.Button("Submit", id="submit")),
    # dcc.Link("Create Account", href="/register")
])


@app.callback(
    Output("session", "data"),
    Output("login_response", "children"),
    Output("login_location", "pathname"),
    Input("login_submit", "n_clicks"),
    State("login_username", "value"),
    State("login_password", "value"),
    State("session", "data")
)
def on_sumbit(submit_clicks, username, password, session_data):
    if username is None or password is None:
        if session_data is not None:
            return None, dash.no_update, "/logout"
        return [dash.no_update] * 3
    user = db.users.find_one({"username": username})
    if user is None:
        error = dbc.Alert("Username not found", color="danger")
        return dash.no_update, error, dash.no_update
    salt = user["salt"]
    key = user["password"]
    new_key = util.pass2key(password, salt)
    if key != new_key:
        error = dbc.Alert("Incorrect password", color="danger")
        return dash.no_update, error, dash.no_update
    
    session_id = str(uuid.uuid4())
    db.users.update_one({"username": username}, {"$set": {"session_id": session_id}})
    
    return {"session_id": session_id}, dash.no_update, "/todo"

# @app.callback(
#     Output("login_location", "pathname"),
#     Input("session", "data")
# )
# def go_home(session_data):
#     return "/home"