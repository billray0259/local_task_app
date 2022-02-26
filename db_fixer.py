from global_vars import db
from datetime import datetime
import pymongo

atlas = pymongo.MongoClient("mongodb+srv://admin:buginnoodle@cluster0.v7g58.mongodb.net/task_app?retryWrites=true&w=majority")["task_app"]

collections = ["users", "records", "bugs", "tasks"]

for name in collections:
    collection = atlas[name].find()
    db[name].insert_many(collection)

print(list(map(lambda u: u["username"], db["users"].find())))

# prefs = db.users.find_one({"username": "bill"})["preferences"]
# for user in users:
#     # new_prefs = []
#     # prefs = user["preferences"]
#     # for pref in prefs:
#     #     task = db.tasks.find_one({"_id": pref["task"]})
#     #     if task is not None:
#     #         new_prefs.append(pref)
#     db.users.update_one({"_id": user["_id"]}, {"$set": {"last_activated": datetime.now()}})
