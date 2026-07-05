import os
from dotenv import load_dotenv

# Load environmental variables from root .env or fallback config
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('JWT_SECRET', 'supersecretfarmconnectkey123!')
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://127.0.0.1:27017/farmconnect')
