
def get_database():
    CONNECTION_STRING = "mongodb://root:rootpassword@localhost:27017"

    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING)

    return client['magneto']