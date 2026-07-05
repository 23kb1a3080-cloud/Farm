from pymongo import MongoClient
from config import Config

# Initialize connection client
client = MongoClient(Config.MONGO_URI)
db = client.get_default_database()

# Collections
users_col = db['users']
products_col = db['products']
orders_col = db['orders']
payments_col = db['payments']

def get_db():
    return db
