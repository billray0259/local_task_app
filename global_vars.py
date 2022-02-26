from os import confstr
import dash
import pymongo

debug = False

# https://www.bootstrapcdn.com/bootswatch/

theme = "https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/materia/bootstrap.min.css"
# theme = "https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/cyborg/bootstrap.min.css"

db = None
with open("db_connection.txt", "r") as db_info:
    connection_info = db_info.readline()
    db = pymongo.MongoClient(connection_info)["task_app_test" if debug else "task_app"]
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[theme])
