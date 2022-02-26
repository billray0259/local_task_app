import os

import hashlib
import pymongo

debug = False

with open("db_connection.txt", "r") as db_info:
    connection_info = db_info.readline()
    db = pymongo.MongoClient(connection_info)["task_app_test" if debug else "task_app"]

username = ""
password = ""

print("Changing password of '%s' to '%s'. Press enter to confirm or ctrl+C to cancel." % (username, password))
input()

salt = os.urandom(32)
password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

db.users.update_one({"username": username}, {"$set": {"password": password, "salt": salt}})

print("Password Changed.")
