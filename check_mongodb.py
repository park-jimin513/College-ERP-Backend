import sys

from pydantic import ValidationError
from pymongo.errors import ConfigurationError


def main() -> int:
    client = None
    try:
        from app.core.mongo import check_mongodb_connection, client as mongo_client

        client = mongo_client
        check_mongodb_connection()
    except ValidationError:
        print(
            "[MongoDB] Backend settings are invalid. Check that required values, "
            "including MONGODB_URI and SECRET_KEY, are configured in backend\\.env.",
            file=sys.stderr,
        )
        return 1
    except ConfigurationError:
        print(
            "[MongoDB] The URI or Atlas SRV configuration is invalid. Verify the "
            "MONGODB_URI hostname and Atlas DNS records; the URI was not printed.",
            file=sys.stderr,
        )
        return 1
    except RuntimeError as exc:
        print(f"[MongoDB] {exc}", file=sys.stderr)
        return 1
    finally:
        if client is not None:
            client.close()

    print("[MongoDB] Ping succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
