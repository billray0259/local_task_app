import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from global_vars import app, db
import util
import uuid

layout = html.Div([
    html.Div(id="todo_header"),
    html.Div(id="needed_input")
])

@app.callback(
    Output("todo_header", "children"),
    Input("needed_input", "value"),
    State("session", "data")
)
def load_todo(_, session_data):
    if session_data is None or "session_id" not in session_data:
        return dcc.Link("Login", href="/login")
    
    session_id = session_data["session_id"]
    user = db.users.find_one({"session_id": session_id})
    if user is None:
        return dcc.Link("Login", href="/login")

    return "Hello %s" % user["name"]
