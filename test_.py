# import pymongo

# db = pymongo.MongoClient("mongodb://192.168.1.40:27017/task_app?retryWrites=true&w=majority")["task_app"]
from global_vars import db
from bson.json_util import dumps

# backup = list(db.records.find())

# with open("record_backup.json", "w") as f:
#     json_string = dumps(backup, indent=1)
#     f.write(json_string)





