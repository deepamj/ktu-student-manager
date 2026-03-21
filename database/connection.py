import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = None
db = None

def get_db():
    global client, db
    if db is None:
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            client.server_info()  # triggers connection, catches errors early
            db = client[DB_NAME]
            print("✅ Connected to MongoDB successfully.")
        except Exception as e:
            print(f"❌ Could not connect to MongoDB: {e}")
            exit(1)
    return db

def close_db():
    global client
    if client:
        client.close()