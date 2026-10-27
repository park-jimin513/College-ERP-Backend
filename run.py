import os
<<<<<<< HEAD
import sys
=======

>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
import uvicorn
from app.seed import seed_database

if __name__ == "__main__":
<<<<<<< HEAD
    print("[*] Checking database initialization...")
    try:
        seed_database()
    except Exception as e:
        print(f"[!] Database setup notice: {e}")

    print("\n[+] Starting College ERP Backend Server...")
    print("   -> API URL: http://127.0.0.1:8000")
    print("   -> Interactive Swagger Docs: http://127.0.0.1:8000/docs")
    print("   -> Alternative Redoc: http://127.0.0.1:8000/redoc\n")
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
=======
    if os.getenv("SEED_DATABASE", "").lower() in {"1", "true", "yes"}:
        seed_database()

    port = int(os.getenv("PORT", "8000"))
    print("\n[+] Starting College ERP Backend Server...")
    print(f"   -> API URL: http://localhost:{port}")
    print(f"   -> Interactive Swagger Docs: http://localhost:{port}/docs")
    print(f"   -> Alternative Redoc: http://localhost:{port}/redoc\n")

    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
