''' this is the database for the Prodbot - temporary '''
from pymongo import MongoClient
MONGODB_URI = "mongodb://heroku_gh025bzj:obo29fmtaec5i8nonfrla7a064@ds133261.mlab.com:33261/heroku_gh025bzj"
client = MongoClient(MONGODB_URI)
db = client.heroku_gh025bzj
# cursor = db.prodBot  # for skipping the collection naming step

if __name__ == '__main__':
    db_package = {
        'col1': 1,
        'col2': 2,
        'col3': 3
    }
    db.draftlog.insert(db_package)
    print('logged to db')