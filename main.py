from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "aise"
COLLECTION_NAME = "students"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Models
class QueryPhone(BaseModel):
    phone_number: str

class DocumentModel(BaseModel):
    documents: List[Dict[str, Any]]

class QueryModel(BaseModel):
    query: Dict[str, Any]

class UpdateModel(BaseModel):
    filter: Dict[str, Any]
    update: Dict[str, Any]

# Endpoints
@app.post("/lookup")
async def find_user_by_phone(query: QueryPhone):
    document = await collection.find_one({"phone": query.phone_number})
    if not document:
        raise HTTPException(status_code=404, detail="User not found")
    document["_id"] = str(document["_id"])
    return document

@app.post("/drop-collection")
async def drop_collection():
    await collection.drop()
    return {"status": "Collection dropped"}

@app.post("/insert-many")
async def insert_many(data: DocumentModel):
    result = await collection.insert_many(data.documents)
    return {"inserted_ids": [str(_id) for _id in result.inserted_ids]}

@app.post("/find")
async def find_by_query(query_model: QueryModel):
    cursor = collection.find(query_model.query)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results

@app.post("/update-many")
async def update_many(update_model: UpdateModel):
    result = await collection.update_many(update_model.filter, {"$set": update_model.update})
    return {"matched_count": result.matched_count, "modified_count": result.modified_count}
