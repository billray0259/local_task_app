# from logging import PlaceHolder
# from typing import Match
import dash
# from dash_bootstrap_components._components.ButtonGroup import ButtonGroup
# from dash_bootstrap_components._components.CardBody import CardBody
# from dash_bootstrap_components._components.CardHeader import CardHeader
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL, MATCH
from global_vars import app, db
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import random
from collections import defaultdict
import numpy as np

layout = html.Div([
    dcc.Interval(id="todo_interval", interval=60*1000),
    html.Div(id="audio_div"),
    dbc.FormGroup([
        dbc.Label("Display by Group"),
        html.Div(
            dbc.Checklist(
                options=[
                    {"label": "", "value": 1}
                ],
                value=[],
                id="group-display-input",
                switch=True,
            )
        )
    ]),
    html.Div(id="todo_contents"),
    # html.H1("Your Tasks", id="todo_title"),
    # html.Div(id="your_tasks"),
    # html.H1("All Tasks"),
    # html.Div(id="all_tasks"),
])


def calculate_points(task, users, current_user=None):
    points = 0
    n_users = 0
    # if len(users) < 5:
    #     print(users)
    # print(len(users))
    for every_user in users:
        # if every_user["_id"] == user["_id"]:
        #     continue
        if current_user is not None and every_user["_id"] == current_user["_id"]:
            continue

        n_users += 1
        prefs = every_user["preferences"]
        avg_pref = 0
        for pref in prefs:
            avg_pref += pref["preference"] / len(prefs)
        for pref in prefs:
            if pref["task"] == task["_id"]:
                points += pref["preference"] / avg_pref
                break

    points /= max(n_users, 1)
    return points


def calculate_time_percentage(task):
    time_since_last_completion = datetime.now() - task["last_completed"]
    period = timedelta(days=task["period"])
    time_percentage = time_since_last_completion.total_seconds()/period.total_seconds()
    return time_percentage


def make_card(user, task, users, default_helper_value=None):
    task_id = str(task["_id"])
    time_since_last_completion = datetime.now() - task["last_completed"]
    period = timedelta(days=task["period"])
    time_percentage = time_since_last_completion.total_seconds()/period.total_seconds()
    seconds_remaining = period.total_seconds() - time_since_last_completion.total_seconds()
    color = "success"
    if time_percentage > 0.75:
        color = "warning"
    if time_percentage > 1:
        color = "danger"
    label = ""
    if time_percentage > 0.02:
        # label = html.Div("%d%%" % round(100*time_percentage), style={"font-size": "1.7em"})
        abs_seconds = abs(seconds_remaining)
        label = ""
        days = abs_seconds // (60*60*24)
        hours = abs_seconds % (60*60*24) // (60*60)
        minutes = round(abs_seconds % (60*60*24) % (60*60) / 60)

        if days > 0:
            label = "%dd %dh %dm" % (days, hours, minutes)
        elif hours > 0:
            label = "%dh %dm" % (hours, minutes)
        else:
            label = "%dm" % minutes
        if seconds_remaining < 0:
            label += " overdue"
        label = html.Div(label, style={"font-size": "1.7em"})
    # points = 0
    usernames = [user["username"]]
    names = [user["name"]]
    if user["username"] == "tablet":
        usernames = []
        names = []

    for every_user in users:
        if user["_id"] != every_user["_id"] and every_user["active"]:
            usernames.append(every_user["username"])
            names.append(every_user["name"])

    points = calculate_points(task, users, current_user=user)

    helper_checklist_options = []
    for i in range(len(usernames)):
        helper_checklist_options.append({
            "label": names[i],
            "value": usernames[i]
        })

    # default_option = [default_helper_username] if default_helper_username is not None else None
    # print(default_option)
    # complete_disabled =

    card = dbc.Collapse(
        dbc.Card([
            dbc.CardHeader(
                dbc.Row([
                    dbc.Col(
                        html.H5(task["task_name"])
                    ),
                    dbc.Col(
                        html.H5("%d points" % round(points*100))
                    )
                ])
            ),
            dbc.CardBody([
                html.P(task["desc"]),
                html.Div([
                    dbc.Collapse([
                        dbc.Progress(label, value=100*time_percentage, color=color, className="mb-3", style={
                            "height": "2em"
                        })
                    ], id={"type": "todo_progress_collapse", "task": task_id}, is_open=True),
                    dbc.Collapse([
                        dbc.Row([
                            dbc.Col([
                                dcc.Slider(id={"type": "todo_progress_slider", "task": task_id}, min=0, max=100, step=1, value=50)
                            ], width=10),
                            dbc.Col([
                                dbc.Button("Update", id={
                                    "type": "todo_period_change",
                                    "task": task_id
                                }, color="primary"),
                            ])
                        ]),
                    ], id={"type": "todo_progress_transformed", "task": task_id}),
                ], id={"type": "todo_progress", "task": task_id}),
                dbc.Collapse([
                    html.H6("Contributors"),
                    dbc.Checklist(options=helper_checklist_options, value=[default_helper_value], id={
                        "type": "helper_list",
                        "task": task_id
                    })
                ], id={
                    "type": "helper_collapse",
                    "task": task_id
                }, className="mb-3"),
                dbc.Button("Add Helper", id={
                    "type": "helper_button",
                    "task": task_id
                }, color="primary", className="mr-2"),
                dbc.Button("Complete", id={
                    "type": "todo_task",
                    "task": task_id,
                    "points": points
                }, color="primary", disabled=default_helper_value is None, className="audio_trigger"),

                html.Div(id={
                    "type": "audio_div",
                    "task": task_id
                })
            ])
        ], className="mb-4"),
        is_open=True, id={
            "type": "todo_collapse",
            "task": task_id
        })
    return card, seconds_remaining, time_percentage


@app.callback(
    Output("todo_contents", "children"),
    Input("todo_interval", "n_intervals"),
    Input("group-display-input", "value"),
    State("session", "data")
)
def update_todo_cards(intervals, group_display, session_data):

    tasks = list(db.tasks.find())
    users = list(db.users.find({"active": True}))
    current_user = db.users.find_one(session_data)
    if current_user is None:
        print(session_data)

    if len(group_display) == 1:
        card_groups = defaultdict(lambda: [])
        groupless_cards = []
        for task in tasks:
            card = make_card(current_user, task, users)
            if "group" in task: 
                card_groups[task["group"]].append(card)
            else:
                groupless_cards.append(card)

        contents = []
        for group in card_groups:
            contents.append(html.H1(group))
            cards = card_groups[group]
            cards.sort(key=lambda t: t[2], reverse=True)
            cards = list(map(lambda t: t[0], cards))
            for card in cards:
                contents.append(card)

        if len(groupless_cards) > 0:
            contents.append(html.H1("Ungrouped Tasks"))
            groupless_cards.sort(key=lambda t: t[2], reverse=True)
            groupless_cards = list(map(lambda t: t[0], groupless_cards))
            contents.extend(groupless_cards)
        
        return contents

    
    records = list(db.records.find())

    user_ids = set()
    for user in users:
        user_ids.add(user["_id"])

    records = [record for record in records if record["user"] in user_ids]

    # records = db.records.find({"time_completed": {"$gt": datetime.now() - timedelta(days=14)}})

    users_by_id = {user["_id"]: user for user in users}
    tasks_by_id = {task["_id"]: task for task in tasks}

    avg_task_prefs = defaultdict(lambda: 0)
    # total_active_seconds = 0  # total active seconds across all users
    users_active_seconds = {}  # maps user_id to seconds
    users_preferences = {}  # maps user_id to dicts that map task_id to normalized preference values
    for user in users:
        avg_user_pref = 0  # this users average un-normalized preference value
        for pref in user["preferences"]:
            avg_user_pref += pref["preference"] / len(user["preferences"])

        user_id = user["_id"]
        preferences = {}
        for pref in user["preferences"]:
            preferences[pref["task"]] = pref["preference"] / avg_user_pref

        users_preferences[user_id] = preferences
        for t, task in enumerate(tasks):
            task_id = task["_id"]
            avg_task_prefs[task_id] += preferences[task_id] / len(users)

        active_seconds = user["active_seconds"]
        active_seconds += (datetime.now() - user["last_activated"]).total_seconds()
        users_active_seconds[user_id] = active_seconds
        # total_active_seconds += active_seconds

    total_points = 0
    users_points = defaultdict(lambda: 0)  # maps user_id to total points from all records
    for record in records:
        total_points += record["points"]
        users_points[record["user"]] += record["points"]

    assignments = defaultdict(lambda: [])
    tasks_to_assign = [task for task in tasks]
    last_tasks_to_assign_len = -1
    while len(tasks_to_assign) != last_tasks_to_assign_len:
        last_tasks_to_assign_len = len(tasks_to_assign)
        # Find the user with the fewest points per second
        min_pps = 1e9
        min_user_id = None
        for user_id, points in users_points.items():
            pps = points / users_active_seconds[user_id]
            if pps < min_pps:
                min_pps = pps
                min_user_id = user_id

        # Find the best task for this user based only on preference scores (not based on points)
        max_avoided_pain = -1e9
        max_task_id = None
        for task in tasks_to_assign:
            # If the task doesn't need to be done don't assign it to anyone
            if calculate_time_percentage(task) < 0.75:
                continue
            task_id = task["_id"]
            avoided_pain = 0  # sum of all other user preference scores minus this users preference score
            # pain = 0
            n_others = len(users) - 1
            for user_id, preferences in users_preferences.items():
                if user_id != min_user_id:
                    avoided_pain += preferences[task_id]/n_others
                else:
                    avoided_pain -= preferences[task_id]
            
            # avoided_pain = avoided_pain/n_others - pain

            if avoided_pain > max_avoided_pain:
                max_avoided_pain = avoided_pain
                max_task_id = task_id

        if max_task_id == None:
            print("max_task_id is None")
            continue
        
        

        task_points = calculate_points(tasks_by_id[max_task_id], users, {"_id": min_user_id})
        assignments[min_user_id].append(max_task_id)
        users_points[min_user_id] += task_points
        for i in range(len(tasks_to_assign)):
            if tasks_to_assign[i]["_id"] == max_task_id:
                del tasks_to_assign[i]
                break
        
    # If task assignment ever seems weird comment these out.
    #     print(db.users.find_one({"_id": min_user_id})["name"], db.tasks.find_one({"_id": max_task_id})["task_name"], users_points[min_user_id]/users_active_seconds[min_user_id], max_avoided_pain)

    # for i, p in users_points.items():
    #     print(db.users.find_one({"_id": i})["name"], p/users_active_seconds[i])

    if current_user["username"] == "tablet":
        contents = []
        for user_id, task_ids in assignments.items():
            user = users_by_id[user_id]
            contents.append(html.H1(user["name"]))
            cards = []
            for task_id in task_ids:
                card = make_card(user, tasks_by_id[task_id], users, default_helper_value=user["username"])
                cards.append(card)
            cards.sort(key=lambda t: t[2], reverse=True)
            cards = list(map(lambda t: t[0], cards))
            contents.extend(cards)

        contents.append(html.H1("Other Tasks"))
        cards = []
        for task in tasks_to_assign:
            card = make_card(current_user, tasks_by_id[task["_id"]], users)
            cards.append(card)
        cards.sort(key=lambda t: t[2], reverse=True)
        cards = list(map(lambda t: t[0], cards))
        contents.extend(cards)
        return contents

    # assignments["other_tasks"].extend(list(map(lambda t: t["_id"], tasks_to_assign)))

    your_tasks = []
    other_tasks = []

    for task in tasks_to_assign:
        card = make_card(current_user, task, users)
        other_tasks.append(card)

    contents = []
    for user_id, task_ids in assignments.items():
        user = users_by_id[user_id]
        contents.append(html.H1(user["name"]))
        cards = []
        for task_id in task_ids:
            if user_id == current_user["_id"]:
                card = make_card(user, tasks_by_id[task_id], users, default_helper_value=user["username"])
                your_tasks.append(card)
            else:
                card = make_card(user, tasks_by_id[task_id], users)
                other_tasks.append(card)
            cards.append(card)
        cards.sort(key=lambda t: t[2], reverse=True)
        cards = list(map(lambda t: t[0], cards))
        contents.extend(cards)

    your_tasks.sort(key=lambda t: t[2], reverse=True)
    your_tasks = [card[0] for card in your_tasks]

    other_tasks.sort(key=lambda t: t[2], reverse=True)
    other_tasks = [card[0] for card in other_tasks]

    if len(your_tasks) == 0:
        your_tasks = [dbc.Alert("You're ahead! As more tasks near their period they may be assigned to you.", color="success")]
    else:
        your_tasks = [html.Div(your_tasks)]

    if len(other_tasks) == 0:
        other_tasks = [dbc.Alert("You got this!", color="success")]
    else:
        other_tasks = [html.Div(other_tasks)]

    return [html.H1("Your Tasks")] + your_tasks + [html.H1("All Tasks")] + other_tasks


@app.callback(
    Output({"type": "todo_progress_collapse", "task": MATCH}, "is_open"),
    Output({"type": "todo_progress_transformed", "task": MATCH}, "is_open"),
    Input({"type": "todo_progress", "task": MATCH}, "n_clicks"),
    prevent_initial_call=True,
)
def open_percent_period_bar(clicks):
    return False, True

@app.callback(
    Output({"type": "todo_progress_transformed", "task": MATCH}, "children"),
    Input({"type": "todo_period_change", "task": MATCH}, "n_clicks"),
    State({"type": "todo_progress_slider", "task": MATCH}, "value"),
    State({"type": "todo_progress_slider", "task": MATCH}, "id"),
    prevent_initial_call=True
)
def update_percent_period(clicks, percent_period, id):
    task_id = ObjectId(id["task"])
    task = db.tasks.find_one({"_id": task_id})
    period_delta = timedelta(days=task["period"] * percent_period/100)
    db.tasks.update_one({"_id": task_id}, {"$set": {"last_completed": datetime.now() - period_delta}})
    return dbc.Alert("Updated", color="success")

@app.callback(
    Output({"type": "helper_collapse", "task": MATCH}, "is_open"),
    Output({"type": "helper_button", "task": MATCH}, "children"),
    Output({"type": "todo_task", "task": MATCH, "points": ALL}, "disabled"),
    Input({"type": "helper_button", "task": MATCH}, "n_clicks"),
    State({"type": "helper_collapse", "task": MATCH}, "is_open"),
    prevent_initial_call=True
)
def toggle_helper(clicks, is_open):
    helper_open=not is_open
    helper_button_text="Close" if not is_open else "Add Helper"
    return helper_open, helper_button_text, (False,)


@app.callback(
    Output({"type": "todo_collapse", "task": MATCH}, "is_open"),
    Output({"type": "audio_div", "task": MATCH}, "children"),
    Input({"type": "todo_task", "task": MATCH, "points": ALL}, "n_clicks"),
    Input({"type": "todo_task", "task": MATCH, "points": ALL}, "id"),
    State({"type": "helper_list", "task": MATCH}, "value"),
    prevent_initial_call=True
)
def complete_task(clicks, task_info, usernames):
    global db
    event=dash.callback_context.triggered[0]
    if event["value"] is None:
        return True, dash.no_update

    if len(usernames) == 0 or (len(usernames) == 1 and usernames[0] is None):
        return dash.no_update, dash.no_update

    task_id=ObjectId(task_info[0]["task"])
    task=db.tasks.find_one({"_id": task_id})
    # points=task_info[0]["points"]
    # usernames = map(lambda div: div["props"]["id"]["username"], helper_list)
    completed_time=datetime.now()
    if len(usernames) > 0:
        queries=list(map(lambda un: {"username": un}, usernames))
        all_users = list(db.users.find({"active": True}))
        users=list(db.users.find({"$or": queries}))
        records=[]
        for user in users:
            points = calculate_points(task, all_users, user)
            records.append({
                "user": user["_id"],
                "task_name": task["task_name"],
                "time_completed": completed_time,
                "points": points / len(users),
                "hidden": False
            })
        db.records.insert(records)
    
    # alpha = 0.1
    # time_taken = (completed_time - task["last_completed"]).total_seconds() / (60 * 60 * 24)
    # new_period =  (1-alpha) * task["period"] + alpha * time_taken
    # print(time_taken)
    # print(task["period"])
    # print(new_period)
    # db.tasks.update_one({"_id": task["_id"]}, {"$set": {"last_completed": completed_time, "period": new_period}})
    db.tasks.update_one({"_id": task["_id"]}, {"$set": {"last_completed": completed_time}})
    # db.command({
    #     "planCacheClear": "tasks",
    #     "query": {"_id": task["_id"]}
    # })
    
    # import pymongo
    # with open("db_connection.txt", "r") as db_info:
    #     connection_info = db_info.readline()
    #     db = pymongo.MongoClient(connection_info)["task_app_test"]

    # db.get_collec

    audio = np.random.choice(success_audio_links)
    # audio=np.random.choice(all_audio_links)

    audio_component=html.Audio(id="complete_audio", src=audio, controls=False,  autoPlay=True)
    return False, audio_component


all_audio_links=np.loadtxt("assets/mp3_links.txt", str)
success_audio_links=np.loadtxt("assets/success_list.txt", str)
