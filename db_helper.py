"""
This is a helper to manage the database connection for our background process
"""

import os
import pymongo


# USERNAME = os.environ['MONGO_USER']
# PASSWORD = os.environ['MONGO_PASSWORD']
HOSTNAME = 'random_temp_string'
# HOSTNAME = os.environ['MONGO_HOST']
# PORT = os.environ['MONGO_PORT']
PORT = 'random_temp_string'
DB_NAME = 'drafter'


CONNECTION_STRING = 'mongodb://{host}:{port}/{database}'.format(host=HOSTNAME, port=PORT, database=DB_NAME)
CLIENT = pymongo.MongoClient(CONNECTION_STRING, connect=False)

DB = CLIENT.get_default_database()

db = DB


def db_setup():
    """Setup DB"""
    DB.queued_messages.create_index([('userEmailAddress', pymongo.DESCENDING), ('threadId', pymongo.DESCENDING)], unique=True)

# This should be run immediately
db_setup()



def update_history_delta(user, history_id):
    """
    Put new history delta for user into db

    See https://developers.google.com/gmail/api/v1/reference/users/history/list

    Arguments:
        user {[type]} -- [description]
        history_id {[type]} -- [description]
    """
    db.accounts.update_one({'userEmailAddress': user['userEmailAddress']}, {'$set': {'historyId': history_id}})


def set_watch_expiration(user, expiration):
    """Set expiration of current watch https://developers.google.com/gmail/api/v1/reference/users/watch"""
    db.accounts.update_one({'userEmailAddress': user['userEmailAddress']}, {'$set': {'expiration': expiration}})
