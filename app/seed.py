import os
from datetime import datetime, timezone

from pymongo.errors import DuplicateKeyError

from app.core.mongo import (
    check_mongodb_connection,
    ensure_indexes,
    mongo_collection,
    next_sequence,
)
from app.core.security import get_password_hash
from app.seed_data import SEED_DATA


def seed_database() -> None:
    print("[+] Initializing MongoDB College ERP data...")
    check_mongodb_connection()
    ensure_indexes()

    users = mongo_collection("users")
    admin_email = os.getenv("SEED_ADMIN_EMAIL", "admin@college.edu")
    if not users.find_one({"email": admin_email}):
        admin_password = os.getenv("SEED_ADMIN_PASSWORD")
        if not admin_password:
            raise RuntimeError(
                "SEED_ADMIN_PASSWORD must be set to create the initial admin user."
            )
        admin = {
            "id": next_sequence(users.database, "users"),
            "name": "Administrator",
            "email": admin_email,
            "hashed_password": get_password_hash(admin_password),
            "role": "admin",
            "is_active": True,
            "otp_code": None,
            "otp_expires_at": None,
            "otp_attempts": 0,
            "otp_last_sent_at": None,
            "failed_attempts": 0,
            "locked_until": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        admin["_id"] = str(admin["id"])
        try:
            users.insert_one(admin)
            print(f"  * Created initial admin: {admin_email}")
        except DuplicateKeyError:
            print("  * Default admin already exists.")

    for collection_name, records in SEED_DATA.items():
        collection = mongo_collection(collection_name)
        inserted = 0
        for record in records:
            document = dict(record)
            if document.get("id") is None:
                if document.get("title") and document.get("content"):
                    if collection.find_one(
                        {"title": document["title"], "content": document["content"]}
                    ):
                        continue
                document["id"] = next_sequence(users.database, collection_name)
            document["_id"] = str(document["id"])
            if collection.find_one({"id": document["id"]}) or collection.find_one(
                {"_id": document["_id"]}
            ):
                continue
            now = datetime.now(timezone.utc)
            document.setdefault("created_at", now)
            document.setdefault("updated_at", now)
            try:
                collection.insert_one(document)
            except DuplicateKeyError:
                continue
            inserted += 1
        if inserted:
            print(f"  * Seeded {inserted} records in {collection_name}")

    print("[+] MongoDB initialization complete.")
