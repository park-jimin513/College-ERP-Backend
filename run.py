import os

import uvicorn
from app.seed import seed_database

if __name__ == "__main__":
    if os.getenv("SEED_DATABASE", "").lower() in {"1", "true", "yes"}:
        seed_database()

    port = int(os.getenv("PORT", "8000"))
    print("\n[+] Starting College ERP Backend Server...")
    print(f"   -> API URL: http://localhost:{port}")
    print(f"   -> Interactive Swagger Docs: http://localhost:{port}/docs")
    print(f"   -> Alternative Redoc: http://localhost:{port}/redoc\n")

    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
