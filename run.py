import os
import sys
import uvicorn
from app.seed import seed_database

if __name__ == "__main__":
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
