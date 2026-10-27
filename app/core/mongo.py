from __future__ import annotations

from typing import Any

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.core.config import settings


client: MongoClient | None = None
mongo_db = None

if settings.MONGODB_URI:
    try:
        client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        mongo_db = client[settings.DATABASE_NAME]
        print("[MongoDB] Connected successfully.")
    except Exception as exc:  # pragma: no cover - runtime env guard
        print(f"[MongoDB] Connection failed: {exc}")
        client = None
        mongo_db = None


def mongo_collection(collection_name: str):
    if mongo_db is None:
        return None
    return mongo_db[collection_name]


def mongo_key_for(payload: dict[str, Any]) -> str:
    for key in ("email", "id", "room", "vehicle", "title", "name"):
        value = payload.get(key)
        if value not in (None, ""):
            return str(value)
    return str(payload.get("_id") or payload.get("code") or payload.get("studentId") or len(str(payload)))


def sync_to_mongodb(collection_name: str, payload: dict[str, Any] | None, *, delete: bool = False) -> None:
    if not payload or mongo_db is None:
        return

    collection = mongo_db[collection_name]
    doc = dict(payload)
    doc_id = mongo_key_for(doc)
    doc["_id"] = doc_id

    if delete:
        collection.delete_one({"_id": doc_id})
        return

    try:
        collection.update_one({"_id": doc_id}, {"$set": doc}, upsert=True)
    except PyMongoError as exc:  # pragma: no cover - best effort sync only
        print(f"[MongoDB] Write failed for {collection_name}: {exc}")
