from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load .env variables (Mongo URI, etc.)
load_dotenv()

app = FastAPI()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")  # e.g. mongodb+srv://user:pass@cluster.mongodb.net
DB_NAME = "aise"
COLLECTION_NAME = "students"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Request model
class QueryPhone(BaseModel):
    phone_number: str

@app.post("/lookup")
async def find_user_by_phone(query: QueryPhone):
    document = await collection.find_one({"phone": query.phone_number})
    if not document:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert ObjectId to string
    document["_id"] = str(document["_id"])
    return document

