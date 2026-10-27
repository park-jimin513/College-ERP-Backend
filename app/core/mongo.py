from __future__ import annotations

<<<<<<< HEAD
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
=======
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import certifi
from fastapi import HTTPException
from pymongo import ASCENDING, DESCENDING, MongoClient, ReturnDocument
from pymongo.collation import Collation
from pymongo.database import Database
from pymongo.write_concern import WriteConcern
from pymongo.errors import (
    ConfigurationError,
    DuplicateKeyError,
    OperationFailure,
    PyMongoError,
    ServerSelectionTimeoutError,
)

from app.core.config import BACKEND_DIR, settings


EMAIL_COLLATION = Collation(locale="en", strength=2)
SQLITE_DB_PATH = BACKEND_DIR / "college_erp.db"


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


class SQLiteCursor:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = list(rows)

    def __iter__(self):
        return iter(self._rows)

    def sort(self, field: str, direction: int = 1):
        self._rows.sort(key=lambda row: str(row.get(field, "")), reverse=direction == DESCENDING)
        return self

    def skip(self, count: int):
        self._rows = self._rows[count:]
        return self

    def limit(self, count: int | None):
        if count is None:
            return self
        self._rows = self._rows[:count]
        return self


class SQLiteCollection:
    def __init__(self, database: "SQLiteDatabase", collection_name: str):
        self.database = database
        self.name = collection_name

    def _table_name(self) -> str:
        return self.name

    def _conn(self) -> sqlite3.Connection:
        return self.database.connection

    def _as_sql_value(self, value: Any):
        if isinstance(value, (datetime,)):
            return value.isoformat()
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)

    def _extract_projection(self, row: dict[str, Any], projection: dict[str, Any] | None):
        if not projection:
            return row
        included = {key for key, include in projection.items() if include}
        return {key: row.get(key) for key in included if key in row}

    def _parse_filter(self, filters: dict[str, Any] | None):
        if not filters:
            return "", []

        clauses: list[str] = []
        params: list[Any] = []

        def add_sql_condition(field: str, value: Any) -> None:
            real_field = "id" if field == "_id" else field
            if isinstance(value, dict):
                if "$regex" in value:
                    pattern = value["$regex"]
                    mode = value.get("$options", "").lower()
                    if mode == "i":
                        clauses.append(f"LOWER(CAST({ _quote_identifier(real_field) } AS TEXT)) LIKE LOWER(?)")
                    else:
                        clauses.append(f"CAST({ _quote_identifier(real_field) } AS TEXT) LIKE ?")
                    params.append(f"%{pattern}%")
                    return
                if "$gt" in value:
                    clauses.append(f"{_quote_identifier(real_field)} > ?")
                    params.append(self._as_sql_value(value["$gt"]))
                    return
                if "$gte" in value:
                    clauses.append(f"{_quote_identifier(real_field)} >= ?")
                    params.append(self._as_sql_value(value["$gte"]))
                    return
                if "$lt" in value:
                    clauses.append(f"{_quote_identifier(real_field)} < ?")
                    params.append(self._as_sql_value(value["$lt"]))
                    return
                if "$lte" in value:
                    clauses.append(f"{_quote_identifier(real_field)} <= ?")
                    params.append(self._as_sql_value(value["$lte"]))
                    return
                if "$in" in value:
                    placeholders = ", ".join("?" for _ in value["$in"])
                    clauses.append(f"{_quote_identifier(real_field)} IN ({placeholders})")
                    params.extend(self._as_sql_value(item) for item in value["$in"])
                    return
                if "$ne" in value:
                    clauses.append(f"{_quote_identifier(real_field)} != ?")
                    params.append(self._as_sql_value(value["$ne"]))
                    return
            clauses.append(f"{_quote_identifier(real_field)} = ?")
            params.append(self._as_sql_value(value))

        def walk(filter_map: dict[str, Any]) -> None:
            for key, value in filter_map.items():
                if key == "$or":
                    or_clauses: list[str] = []
                    or_params: list[Any] = []
                    for item in value:
                        nested_clause, nested_params = self._parse_filter(item)
                        if nested_clause:
                            or_clauses.append(f"({nested_clause})")
                            or_params.extend(nested_params)
                    if or_clauses:
                        clauses.append(" OR ".join(or_clauses))
                        params.extend(or_params)
                elif key == "$and":
                    for item in value:
                        nested_clause, nested_params = self._parse_filter(item)
                        if nested_clause:
                            clauses.append(f"({nested_clause})")
                            params.extend(nested_params)
                else:
                    add_sql_condition(key, value)

        walk(filters)
        return " AND ".join(clauses), params

    def _ensure_table(self) -> None:
        self._conn().execute(
            f"CREATE TABLE IF NOT EXISTS { _quote_identifier(self.name) } (id TEXT PRIMARY KEY, data TEXT)"
        )
        self._conn().commit()

    def _row_to_record(self, row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
        if isinstance(row, sqlite3.Row):
            payload = dict(row)
        else:
            payload = dict(row)
        if not payload:
            return {}
        if "data" in payload and "id" not in payload:
            try:
                import json
                parsed = json.loads(payload["data"])
                if isinstance(parsed, dict):
                    return parsed
            except (TypeError, ValueError):
                pass
        if "data" in payload:
            payload.pop("data", None)
        if "_id" in payload and "id" not in payload:
            payload["id"] = payload["_id"]
        return dict(payload)

    def _serialize_document(self, document: dict[str, Any]) -> dict[str, Any]:
        record = dict(document)
        record.pop("_id", None)
        if "id" in record:
            record["id"] = str(record["id"])
        return record

    def _fetch_records(self, filters: dict[str, Any] | None = None, projection: dict[str, Any] | None = None):
        self._ensure_table()
        sql = f"SELECT * FROM {_quote_identifier(self.name)}"
        params: list[Any] = []
        if filters:
            where_clause, params = self._parse_filter(filters)
            if where_clause:
                sql += f" WHERE {where_clause}"
        rows = self._conn().execute(sql, params).fetchall()
        results: list[dict[str, Any]] = []
        for row in rows:
            document = self._row_to_record(row)
            if not document:
                continue
            results.append(self._extract_projection(document, projection) if projection else document)
        return results

    def find(self, filter: dict[str, Any] | None = None, projection: dict[str, Any] | None = None):
        return SQLiteCursor(self._fetch_records(filter, projection))

    def find_one(self, filter: dict[str, Any] | None = None, projection: dict[str, Any] | None = None):
        records = self._fetch_records(filter, projection)
        return records[0] if records else None

    def insert_one(self, document: dict[str, Any]):
        self._ensure_table()
        record = self._serialize_document(document)
        if not record:
            return None
        record.pop("_id", None)
        primary_key = str(record.get("id") or record.get("_id") or record.get("name") or "")
        if not primary_key:
            primary_key = str(len(self._fetch_records()) + 1)
        record["id"] = primary_key
        serialized = sqlite3.Binary(__import__('json').dumps(record, default=str).encode('utf-8'))
        try:
            self._conn().execute(
                f"INSERT INTO {_quote_identifier(self.name)} (id, data) VALUES (?, ?)",
                (primary_key, serialized),
            )
            self._conn().commit()
        except sqlite3.IntegrityError:
            raise DuplicateKeyError("duplicate key")
        return {"_id": primary_key}

    def find_one_and_update(self, filter: dict[str, Any], update: dict[str, Any], return_document: str | None = None):
        current = self.find_one(filter)
        if current is None:
            return None
        set_values = update.get("$set", {}) if isinstance(update, dict) and "$set" in update else update
        if not isinstance(set_values, dict):
            return current
        for key, value in set_values.items():
            current[key] = value
        current["updated_at"] = datetime.now(timezone.utc).isoformat()
        primary_key = str(current.get("id") or current.get("_id") or current.get("name") or "")
        self._conn().execute(
            f"UPDATE {_quote_identifier(self.name)} SET data = ? WHERE id = ?",
            (__import__('json').dumps(current, default=str).encode('utf-8'), primary_key),
        )
        self._conn().commit()
        return current

    def update_one(self, filter: dict[str, Any], update: dict[str, Any], upsert: bool = False):
        match = self.find_one(filter)
        if match is None:
            if upsert:
                insert_doc = {"id": str(filter.get("_id") or filter.get("id") or "pending"), **({})}
                if "$max" in update:
                    insert_doc["value"] = update["$max"]["value"]
                elif "$inc" in update:
                    insert_doc["value"] = update["$inc"]["value"]
                self.insert_one(insert_doc)
                return type("UpdateResult", (), {"modified_count": 1, "matched_count": 0, "upserted_id": insert_doc["id"]})()
            return type("UpdateResult", (), {"modified_count": 0, "matched_count": 0, "upserted_id": None})()

        set_values = update.get("$set", {}) if isinstance(update, dict) and "$set" in update else update
        if "$inc" in update:
            for field, delta in update["$inc"].items():
                match[field] = (match.get(field, 0) or 0) + delta
        if "$max" in update:
            for field, value in update["$max"].items():
                if match.get(field, 0) is None or value > match.get(field, 0):
                    match[field] = value
        if set_values and not isinstance(set_values, dict):
            set_values = {}
        for field, value in (set_values or {}).items():
            match[field] = value
        match["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._conn().execute(
            f"UPDATE {_quote_identifier(self.name)} SET data = ? WHERE id = ?",
            (__import__('json').dumps(match, default=str).encode('utf-8'), str(match.get("id") or match.get("_id") or "")),
        )
        self._conn().commit()
        return type("UpdateResult", (), {"modified_count": 1, "matched_count": 1, "upserted_id": None})()

    def delete_one(self, filter: dict[str, Any]):
        match = self.find_one(filter)
        if match is None:
            return type("DeleteResult", (), {"deleted_count": 0})()
        self._conn().execute(f"DELETE FROM {_quote_identifier(self.name)} WHERE id = ?", (str(match.get("id") or match.get("_id") or ""),))
        self._conn().commit()
        return type("DeleteResult", (), {"deleted_count": 1})()

    def aggregate(self, pipeline: list[dict[str, Any]]):
        if not pipeline:
            return []
        table = self.name
        group_stage = next((stage["$group"] for stage in pipeline if "$group" in stage), None)
        match_stage = next((stage["$match"] for stage in pipeline if "$match" in stage), {})
        limit_stage = next((stage["$limit"] for stage in pipeline if "$limit" in stage), None)
        if not group_stage:
            return []
        group_id = group_stage.get("_id")
        field_name = group_id[1:] if isinstance(group_id, str) and group_id.startswith("$") else str(group_id)
        sql = f"SELECT { _quote_identifier(field_name) } AS '_id', COUNT(*) AS count FROM {_quote_identifier(table)}"
        params: list[Any] = []
        if match_stage:
            where_clause, params = self._parse_filter(match_stage)
            if where_clause:
                sql += f" WHERE {where_clause}"
        sql += f" GROUP BY {_quote_identifier(field_name)}"
        if limit_stage is not None:
            sql += " LIMIT ?"
            params.append(limit_stage)
        rows = self._conn().execute(sql, params).fetchall()
        return [{"_id": row["_id"], "count": row["count"]} for row in rows]

    def create_index(self, *args, **kwargs):
        return None


class SQLiteDatabase:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.connection = sqlite3.connect(database_path)
        self.connection.row_factory = sqlite3.Row

    def __getitem__(self, collection_name: str) -> SQLiteCollection:
        return SQLiteCollection(self, collection_name)


def _create_local_database() -> SQLiteDatabase:
    if os.getenv("RENDER", "").lower() == "true":
        raise RuntimeError(
            "MONGODB_URI must be configured on Render; local SQLite storage is not persistent."
        )
    return SQLiteDatabase(SQLITE_DB_PATH)


client = None
mongo_db: Database | SQLiteDatabase | None = None

if settings.MONGODB_URI.strip():
    client = MongoClient(
        settings.MONGODB_URI,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        tlsCAFile=certifi.where(),
    )
    mongo_db = client.get_database(
        settings.DATABASE_NAME,
        write_concern=WriteConcern(w="majority"),
    )
else:
    mongo_db = _create_local_database()


def _connection_error_help(exc: PyMongoError) -> str:
    if isinstance(exc, ConfigurationError):
        return (
            "Check the MONGODB_URI format and confirm the Atlas SRV/DNS records "
            "are available."
        )
    if isinstance(exc, OperationFailure):
        if exc.code == 18:
            return (
                "MongoDB authentication failed. Verify the Atlas database user's "
                "username, password, authSource, and authentication mechanism."
            )
        if exc.code == 13:
            return (
                "MongoDB authenticated the connection but denied this operation. "
                "Verify the database user's roles."
            )
    if isinstance(exc, ServerSelectionTimeoutError):
        details = str(exc).lower()
        if "certificate verify failed" in details:
            return (
                "MongoDB TLS certificate verification failed. Check the system "
                "clock and CA bundle, and ensure TLS inspection is not replacing "
                "the Atlas certificate."
            )
        if "ssl handshake failed" in details or "tls" in details:
            return (
                "MongoDB TLS negotiation failed before authentication. Verify the "
                "Atlas cluster is active and check for firewall, VPN, proxy, or "
                "antivirus TLS inspection; confirm the client IP is allowed in "
                "Atlas Network Access."
            )
        if any(term in details for term in ("dns", "srv", "getaddrinfo", "name resolution")):
            return (
                "MongoDB DNS/SRV lookup failed. Verify the URI's Atlas hostname "
                "and that the current DNS resolver allows SRV and TXT queries."
            )
        return (
            "MongoDB servers could not be reached before the timeout. Verify the "
            "Atlas cluster is active, the client IP is allowed in Atlas Network "
            "Access, and outbound TCP port 27017 is not blocked."
        )
    return (
        "Verify the Atlas cluster is active, the MongoDB URI and database user "
        "are valid, and the client IP is allowed in Atlas Network Access."
    )


def check_mongodb_connection() -> None:
    try:
        client.admin.command("ping")
    except PyMongoError as exc:
        raise RuntimeError(
            f"MongoDB ping failed. {_connection_error_help(exc)}"
        ) from exc


def _masked_email(email: Any) -> str:
    if isinstance(email, str) and "@" in email:
        local_part, domain = email.rsplit("@", 1)
        return f"{local_part[:1]}***@{domain}"
    return "<missing or invalid email>"


def ensure_indexes() -> None:
    users = mongo_db["users"]
    duplicate_emails = list(
        users.aggregate(
            [
                {"$group": {"_id": "$email", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": 1}}},
                {"$limit": 10},
            ],
            collation=EMAIL_COLLATION,
        )
    )
    if duplicate_emails:
        conflicts = "; ".join(
            f"{_masked_email(conflict['_id'])} ({conflict['count']} records)"
            for conflict in duplicate_emails
        )
        raise RuntimeError(
            "Cannot create the case-insensitive unique users.email index because "
            f"duplicate email values exist: {conflicts}. Resolve these records "
            "and rerun initialization; email addresses are masked."
        )

    users.create_index(
        "email",
        unique=True,
        collation=EMAIL_COLLATION,
        name="email_case_insensitive_unique",
    )


def mongo_collection(collection_name: str, db: Database | None = None):
    database = db if db is not None else mongo_db
    return database[collection_name]


def clean_document(document: dict[str, Any] | None) -> dict[str, Any] | None:
    if document is None:
        return None
    result = dict(document)
    result.pop("_id", None)
    return result


def build_query(
    filters: dict[str, Any] | None = None,
    *,
    search: str | None = None,
    search_fields: tuple[str, ...] = (),
) -> dict[str, Any]:
    query = {key: value for key, value in (filters or {}).items() if value is not None}
    if search and search_fields:
        pattern = re.escape(search.strip())
        query["$or"] = [
            {field: {"$regex": pattern, "$options": "i"}}
            for field in search_fields
        ]
    return query


def list_documents(
    db: Database,
    collection_name: str,
    *,
    filters: dict[str, Any] | None = None,
    search: str | None = None,
    search_fields: tuple[str, ...] = (),
    sort_by: str = "id",
    descending: bool = False,
    skip: int = 0,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    cursor = mongo_collection(collection_name, db).find(
        build_query(filters, search=search, search_fields=search_fields)
    ).sort(sort_by, DESCENDING if descending else ASCENDING).skip(skip)
    if limit is not None:
        cursor = cursor.limit(limit)
    return [clean_document(document) or {} for document in cursor]


def get_document(
    db: Database,
    collection_name: str,
    document_id: str | int,
) -> dict[str, Any] | None:
    collection = mongo_collection(collection_name, db)
    document = collection.find_one({"id": document_id})
    if document is None:
        document = collection.find_one({"id": str(document_id)})
    if document is None:
        document = collection.find_one({"_id": str(document_id)})
    return clean_document(document)


def insert_document(
    db: Database,
    collection_name: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    document = dict(data)
    now = datetime.now(timezone.utc)
    document.setdefault("created_at", now)
    document.setdefault("updated_at", now)
    if document.get("id") is not None:
        document["_id"] = str(document["id"])
    try:
        result = mongo_collection(collection_name, db).insert_one(document)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=400, detail="Record already exists.") from exc
    if result is None or not getattr(result, "acknowledged", True):
        raise RuntimeError(
            f"Database did not acknowledge inserting a record into '{collection_name}'."
        )
    return clean_document(document) or {}


def update_document(
    db: Database,
    collection_name: str,
    document_id: str | int,
    updates: dict[str, Any],
) -> dict[str, Any] | None:
    collection = mongo_collection(collection_name, db)
    current = collection.find_one({"id": document_id})
    if current is None:
        current = collection.find_one({"id": str(document_id)})
    if current is None:
        current = collection.find_one({"_id": str(document_id)})
    if current is None:
        return None

    updates = dict(updates)
    updates["updated_at"] = datetime.now(timezone.utc)
    updated = collection.find_one_and_update(
        {"_id": current["_id"]},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    return clean_document(updated)


def delete_document(
    db: Database,
    collection_name: str,
    document_id: str | int,
) -> bool:
    collection = mongo_collection(collection_name, db)
    result = collection.delete_one({"id": document_id})
    if not result.deleted_count:
        result = collection.delete_one({"id": str(document_id)})
    if not result.deleted_count:
        result = collection.delete_one({"_id": str(document_id)})
    return result.deleted_count > 0


def next_sequence(db: Database, sequence_name: str) -> int:
    collection = mongo_collection("_counters", db)
    existing_max = max(
        (
            int(document["id"])
            for document in mongo_collection(sequence_name, db).find({}, {"id": 1})
            if str(document.get("id", "")).isdigit()
        ),
        default=0,
    )
    collection.update_one(
        {"_id": sequence_name},
        {"$max": {"value": existing_max}},
        upsert=True,
    )
    counter = collection.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"value": 1}},
        return_document=ReturnDocument.AFTER,
    )
    return int(counter["value"])
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
