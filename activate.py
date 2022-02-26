import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from global_vars import app, db
from datetime import datetime

layout = html.Div([
    dcc.Location(id="activate_location"),
    html.H1("You must activate to use the app", id="activate_message"),
    dbc.Button("Activate", id="activate_button")
])


@app.callback(
    Output("activate_location", "pathname"),
    Input("activate_button", "n_clicks"),
    State("session", "data")
)
def load_todo(clicks, session_data):
    event = dash.callback_context.triggered[0]["prop_id"]
    if event != "activate_button.n_clicks":
        return dash.no_update
    user = db.users.find_one(session_data)
    if user["active"]:
        return "/home"
    db.users.update_one(session_data, {"$set": {"active": True}})
    db.users.update_one(session_data, {"$set": {"last_activated": datetime.now()}})
    return "/home"
