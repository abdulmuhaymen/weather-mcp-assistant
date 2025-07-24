from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

load_dotenv()

username = quote_plus(os.getenv("MONGO_USERNAME"))
password = quote_plus(os.getenv("MONGO_PASSWORD"))

uri = f"mongodb+srv://{username}:{password}@cluster0.frxzbp7.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri)
db = client["sample_weatherdata"]
collection = db["data"]
