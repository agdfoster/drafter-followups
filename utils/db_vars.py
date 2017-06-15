''' this is the database for the Prodbot - temporary '''
from pymongo import MongoClient
MONGODB_URI = os.environ['MONGODB_URI']
client = MongoClient(MONGODB_URI)
# db = client.heroku_gh025bzj
db = client.get_default_database() # this get's default db
# cursor = db.prodBot  # for skipping the collection naming step

if __name__ == '__main__':
    db_package = {
        'col1': 1,
        'col2': 2,
        'col3': 3
    }
    db.draftlog.insert(db_package)
    print('logged to db')