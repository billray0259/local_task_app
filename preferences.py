import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from global_vars import app, db
from bson.objectid import ObjectId
from datetime import datetime

layout = html.Div([
    html.H1("Preferences", id="preference_heading"),
    html.P("Your preferences represent how much you don't want to do a task. This is a linear scale. If task A has a score of 1 and task B has a score of 10 that means you consider doing task A 10 times to be an equivalent amount of effort as doing task B once"),
    html.Div(id="preference_list"),
    html.Div(id="preference_response"),
    dbc.Button("Update Preferences", id="update_preferences", color="primary", className="mb-4"),
    html.Hr(),
    html.H1("User Settings"),
    dbc.Form([
        dbc.FormGroup([
            dbc.Label("Display Name"),
            dbc.Input(id="display_name", type="text", placeholder="Enter Display Name"),
        ]),
        dbc.FormGroup([
            dbc.Label("Active"),
            html.Div(
                dbc.Checklist(
                    options=[
                        {"label": "", "value": 1}
                    ],
                    value=[],
                    id="switches-input",
                    switch=True,
                ),
            id="active_switch")
        ]),
        html.Div(id="user_settings_response"),
        dbc.Button("Save Settings", id="save_user_settings", color="primary")
    ])
])

@app.callback(
    Output("display_name", "value"),
    Output("switches-input", "value"),
    Output("user_settings_response", "children"),
    Input("save_user_settings", "n_clicks"),
    State("session", "data"),
    State("display_name", "value"),
    State("switches-input", "value"),
)
def save_user_settings(clicks, session_data, display_name, active_switch):
    if session_data is None:
        return [dash.no_update] * 3
    
    user = db.users.find_one(session_data)
    if user is None:
        return [dash.no_update] * 3
    
    event = dash.callback_context.triggered[0]["prop_id"]
    response = dash.no_update
    if event == "save_user_settings.n_clicks":
        if display_name is not None and display_name != user["name"]:
            db.users.update_one(session_data, {"$set": {"name": display_name}})
        active = len(active_switch) == 1
        if active != user["active"]:
            db.users.update_one(session_data, {"$set": {"active": active}})
            if active:
                db.users.update_one(session_data, {"$set": {"last_activated": datetime.now()}})
            else:
                new_active_seconds = user["active_seconds"] + (datetime.now() - user["last_activated"]).total_seconds()
                db.users.update_one(session_data, {"$set": {"active_seconds": new_active_seconds}})
        response = dbc.Alert("Settings saved", color="success", duration=2000)

        return display_name, active_switch, response
    
    display_name = display_name or user["name"]
    active_switch = [1] if user["active"] else []
    return display_name, active_switch, response


    

    


@app.callback(
    Output("preference_response", "children"),
    Output("preference_list", "children"),
    Output("preference_heading", "children"),
    Input("update_preferences", "n_clicks"),
    State({"type": "preference", "task_name": ALL, "preference": ALL, "task_id": ALL}, "children"),
    State("session", "data")
)
def udpate_preferences(update_clicks, preference_divs, session_data):
    login_message = dbc.Alert(["You must be ", html.A("logged in", href="/login"), " to view preferences"], color="danger")
    if session_data is None:
        return login_message, "", ""
    
    session_id = session_data["session_id"]
    user = db.users.find_one({"session_id": session_id})
    if user is None:
        return login_message, "", ""
    
    response_message = ""
    if len(preference_divs) == len(user["preferences"]):
        updated_preferences = []
        # for id_div, task_name, input_elm in preference_divs:
        for id_div, body in preference_divs:
            _id = id_div["props"]["children"]
            pref_value = body["props"]["children"][1]["props"]["children"]["props"]["value"]
            updated_preferences.append({
                "task": ObjectId(_id),
                "preference": pref_value
            })
        db.users.update_one({"_id": user["_id"]}, {"$set": {"preferences": updated_preferences}})
        response_message = dbc.Alert("Preferences Updated", color="success", duration=2000),
        user = db.users.find_one({"_id": user["_id"]})

    preference_divs = []
    preferences = user["preferences"]
    preferences.sort(key=lambda p: p["preference"])
    for preference in preferences:
        task = db.tasks.find_one({"_id": preference["task"]})
        if task is None:
            print(preference["task"])
        preference_divs.append(html.Div([
            html.Div(str(task["_id"]), style={"display": "none"}),
            dbc.Row([
                dbc.Col(html.H5(task["task_name"])),
                dbc.Col(dbc.Input(type="number", value=preference["preference"], min=0, max=100, step=0.001))
            ])
        ], id={
            "type": "preference",
            "task_name": task["task_name"],
            "preference": preference["preference"],
            "task_id": str(task["_id"])
        }))
    return response_message, preference_divs, "%s's preferences" % user["name"]
