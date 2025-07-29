from dotenv import load_dotenv
load_dotenv()
import os
from cryptography.fernet import Fernet



# Hardcoded keys (only for development use — NOT for production!)
FERNET_KEY = "dZ5pT1cY7MVVGszAoq4j1YqrmZxobxy4pC4iWrFiIkI="  # must be 32-byte base64 string

# ✅ FIXED MongoDB connection URI for Docker
MONGO_URI = "mongodb://mongodb:27017/whatsapp_clone"

# Initialize Fernet with key
fernet = Fernet(FERNET_KEY.encode())

class Config:
    MONGO_URI = MONGO_URI
    SECRET_KEY = "DPGceexWKbTBNPoJrYZaFZjIPJ-ndBWwMYhVupBRlX0="
