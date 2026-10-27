import argparse
import sqlite3
from pathlib import Path
from typing import Any

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from app.core.config import BACKEND_DIR, settings


TABLE_COLLECTIONS = {
    "users": "users",
    "students": "students",
    "teaching_staff": "teaching_staff",
    "non_teaching_staff": "non_teaching_staff",
    "departments": "departments",
    "academic_programs": "academic_programs",
    "courses": "courses",
    "fee_records": "fee_records",
    "attendance_records": "attendance_records",
    "examinations": "examinations",
    "exam_results": "exam_results",
    "books": "library_books",
    "hostel_rooms": "hostel_rooms",
    "transport_vehicles": "transport_vehicles",
    "documents": "documents",
    "notices": "notices",
    "timetable_slots": "timetable_slots",
}


def import_table(
    source: sqlite3.Connection,
    database: Any,
    table_name: str,
    collection_name: str,
) -> tuple[int, int]:
    table_exists = source.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    if not table_exists:
        return 0, 0

    collection = database[collection_name]
    inserted = 0
    preserved = 0
    rows = source.execute(f'SELECT * FROM "{table_name}"')
    for row in rows:
        document = dict(row)
        identifier = document.get("id")
        if identifier is not None:
            existing = collection.find_one({"id": identifier}, {"_id": 1})
            if existing is None:
                existing = collection.find_one({"_id": str(identifier)}, {"_id": 1})
            if existing:
                preserved += 1
                continue
            document["_id"] = str(identifier)

        try:
            collection.insert_one(document)
        except DuplicateKeyError:
            if identifier is None:
                raise
            document["_id"] = f"legacy-{table_name}-{identifier}"
            collection.update_one(
                {"_id": document["_id"]},
                {"$setOnInsert": document},
                upsert=True,
            )
        inserted += 1
    return inserted, preserved


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import missing legacy SQLite records into MongoDB without overwriting MongoDB data."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=BACKEND_DIR / "college_erp.db",
        help="Path to the legacy SQLite file (read only).",
    )
    args = parser.parse_args()
    if not args.source.is_file():
        raise FileNotFoundError(f"Legacy database not found: {args.source}")

    sqlite_uri = f"{args.source.resolve().as_uri()}?mode=ro"
    source = sqlite3.connect(sqlite_uri, uri=True)
    source.row_factory = sqlite3.Row
    with MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=10000) as client:
        client.admin.command("ping")
        database = client[settings.DATABASE_NAME]
        summary = {}
        for table_name, collection_name in TABLE_COLLECTIONS.items():
            inserted, preserved = import_table(
                source,
                database,
                table_name,
                collection_name,
            )
            summary[table_name] = {"imported": inserted, "preserved": preserved}
    source.close()

    for table_name, counts in summary.items():
        print(
            f"{table_name}: imported {counts['imported']}, "
            f"preserved existing MongoDB records {counts['preserved']}"
        )
    print(f"SQLite import complete into MongoDB database '{settings.DATABASE_NAME}'.")


if __name__ == "__main__":
    main()
