import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from global_vars import app, db

layout = html.Div([
    html.H1("Report a bug"),
    dbc.FormGroup([
        dbc.Textarea(id="bug_text", placeholder="Describe how to reproduce bug OR submit a suggestion"),
        dbc.Button("Submit", id="bug_submit", type="submit")
    ])
])


@app.callback(
    Output("bug_text", "value"),
    Input("bug_submit", "n_clicks"),
    State("bug_text", "value")
)
def load_todo(clicks, bug_text):
    if bug_text is None or len(bug_text) == 0:
        return dash.no_update
    doc = {"bug": bug_text}
    db.bugs.insert_one(doc)
    return ""
