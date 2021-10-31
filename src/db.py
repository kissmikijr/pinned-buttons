import os

def get_database():
    from pymongo import MongoClient
    client = MongoClient(os.environ.get("MONGO_DB_CONNECTION_STRING")))

    return client['magneto']