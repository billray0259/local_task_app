import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pymongo
from global_vars import app, db

layout = html.Div([
    html.H1("Submit an issue", id="issues_title"),
    dbc.FormGroup([
        dbc.Textarea(id="bug_text", placeholder="Submit a suggestion or describe how to reproduce bug", className="mb-3"),
        dbc.Button("Submit", id="bug_submit", type="submit")
    ]),
    html.H1("Active Issues"),
    html.Div(id="issues")
])

def get_issues_cards():
    issues = db.bugs.find().sort("_id", pymongo.DESCENDING)
    issue_cards = []
    for issue in issues:
        issue_cards.append(
            dbc.Card(
                dbc.CardBody(issue["bug"]),
                className="mb-3")
        )
    return issue_cards

@app.callback(
    Output("bug_text", "value"),
    Output("issues", "children"),
    Input("bug_submit", "n_clicks"),
    State("bug_text", "value")
)
def submit_issue(clicks, bug_text):
    
    if bug_text is None or len(bug_text) == 0:
        return dash.no_update, get_issues_cards()
    doc = {"bug": bug_text}
    db.bugs.insert_one(doc)
    return "", get_issues_cards()


# @app.callback(
#     Output("issues", "children"),
#     Input("issues_title", "n_clicks"),
#     Input("bug_text", "value")
# )
# def show_issues(clicks):
    
#     return issue_cards
