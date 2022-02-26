from dash_bootstrap_components._components.NavItem import NavItem
from dash_bootstrap_components._components.NavLink import NavLink
from dash_bootstrap_components._components.NavbarSimple import NavbarSimple
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from global_vars import app, db, debug

import login
import register
import home
import tasks
import preferences
import todo
import records
import issues
import activate
import points
import readme

layouts = {
    "login": login.layout,
    "register": register.layout,
    "home": home.layout,
    "tasks": tasks.layout,
    "preferences": preferences.layout,
    "todo": todo.layout,
    "records": records.layout,
    "issues": issues.layout,
    "activate": activate.layout,
    "points": points.layout,
    "readme": readme.layout
}

app.layout = html.Div([
    dcc.Store(id="session", storage_type='local'),
    dcc.Location(id='url', refresh=False),
    # dbc.NavbarSimple(
    #     dbc.Collapse(id="navbar", is_open=True),
    # brand="Test Task App" if debug else "Task App", brand_href="/todo", color="primary", className="mb-3", dark=True),
    dbc.NavbarSimple(id="navbar", brand="Test Task App" if debug else "Task App", brand_href="/todo", color="primary", className="mb-3", dark=True),
    html.Meta(name="viewport", content="width=device-width, initial-scale=1"),
    dbc.Container(id='page-content')
])

app.title = "Task App"

@app.callback(
    Output('page-content', 'children'),
    Output("navbar", "children"),
    Input('url', 'pathname'),
    State("session", "data")
)
def display_page(path, session_data):
    if path == "/logout":
        path = "/login"
    user = None
    if session_data is not None:
        user = db.users.find_one(session_data)
    if user is None or path == "/logout":
        if path not in ["/login", "/register", "/issues"]:
            path = "/login"
        navbar_children = [
            dbc.NavItem(dbc.NavLink("Login", href="/login")),
            dbc.NavItem(dbc.NavLink("Register", href="/register")),
            dbc.NavItem(dbc.NavLink("Report Bug", href="/issues")),
        ]
    else:
        if not user["active"] and not user["username"] == "tablet":
            path = "/activate"
        navbar_children = [
            dbc.NavItem(dbc.NavLink("To Do", href="/todo", id={"type": "navitem", "id":"todo"})),
            dbc.NavItem(dbc.NavLink("Points", href="/points", id={"type": "navitem", "id": "points"})),
            dbc.NavItem(dbc.NavLink("Records", href="/records", id={"type": "navitem", "id": "records"})),
            dbc.NavItem(dbc.NavLink("Tasks", href="/tasks", id={"type": "navitem", "id": "tasks"})),
            dbc.NavItem(dbc.NavLink("Preferences", href="/preferences", id={"type": "navitem", "id": "preferences"})),
            dbc.NavItem(dbc.NavLink("Logout", href="/login", id={"type": "navitem", "id": "login"})),
            dbc.NavItem(dbc.NavLink("Report Issue", href="/issues", id={"type": "navitem", "id": "issues"})),
            dbc.NavItem(dbc.NavLink("Read Me", href="/readme", id={"type": "navitem", "id": "readme"})),
        ]
    
    path = path.replace("/", "")
    if path == "":
        path = "todo"
    if path in layouts:
        page = layouts[path]
        if callable(page):
            return page(), navbar_children
        return page, navbar_children
    return "Page not found", navbar_children

# @app.callback(
#     Output("navbar", "is_open"),
#     Input({"type": "navitem", "id": "tasks"}, "n_clicks")
# )
# def collapse_navbar(clicks):
#     return False

if __name__ == '__main__':
    app.run_server(debug=debug, dev_tools_ui=True, dev_tools_props_check=False, host="0.0.0.0", port=8000)
