import pymongo

copy_from = pymongo.MongoClient("mongodb://192.168.1.40:27017/task_app?retryWrites=true&w=majority")["task_app"]

# WARNING copy_to MUST BE EMPTY
copy_to = pymongo.MongoClient("mongodb://192.168.1.40:27017/task_app?retryWrites=true&w=majority")["task_app_backup_oct_18_2021"]


collections = ["users", "records", "bugs", "tasks"]

for name in collections:
    collection = copy_from[name].find()
    copy_to[name].insert_many(collection)

print(list(map(lambda u: u["username"], copy_to["users"].find())))

# prefs = db.users.find_one({"username": "bill"})["preferences"]
# for user in users:
#     # new_prefs = []
#     # prefs = user["preferences"]
#     # for pref in prefs:
#     #     task = db.tasks.find_one({"_id": pref["task"]})
#     #     if task is not None:
#     #         new_prefs.append(pref)
#     db.users.update_one({"_id": user["_id"]}, {"$set": {"last_activated": datetime.now()}})
