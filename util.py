import hashlib
import os
from global_vars import db


def pass2key(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
