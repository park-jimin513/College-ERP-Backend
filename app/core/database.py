from collections.abc import Iterator

from pymongo.database import Database

from app.core import mongo


def get_db() -> Iterator[Database]:
    database = mongo.mongo_db
    if database is None:
        raise RuntimeError("MongoDB is not configured.")
    yield database
