import dash_html_components as html
import dash_bootstrap_components as dbc
from global_vars import app, db

def layout():
    cards = []
    records = db.records.find().sort("time_completed", -1)
    id_to_user = {}
    for record in records:
        if record["hidden"]:
            continue
        if record["user"] in id_to_user:
            user = id_to_user[record["user"]]
        else:
            user = db.users.find_one({"_id": record["user"]})
            id_to_user[record["user"]] = user
        cards.append(
            dbc.Card([
                dbc.CardHeader(html.H5("%s completed '%s'" % (user["name"], record["task_name"]))),
                dbc.CardBody([
                    html.Div("Time Completed: %s" % record["time_completed"].strftime("%-m/%d/%y %-I:%M %p")),
                    html.Div("Points Recieved: %d" % round(record["points"] * 100))
                ])
            ], className="mb-4")
        )
    return html.Div([
        html.H1("Records"),
        html.Div(cards, id="record_cards"),
        # dbc.Button("Load More", id="load_more_records")
    ])
