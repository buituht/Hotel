#!/usr/bin/env python3
# db_test.py
# Chạy: python db_test.py "mysql+pymysql://user:pass@host:port/dbname"
# Ví dụ:
# python db_test.py "mysql+pymysql://hotel_user:StrongPassword!123@127.0.0.1:3307/khachsan"

import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

def main():
    if len(sys.argv) < 2:
        print("Usage: python db_test.py \"mysql+pymysql://user:pass@host:port/dbname\"")
        sys.exit(1)
    url = sys.argv[1]
    engine = create_engine(url, pool_pre_ping=True)
    print("Testing connection to:", url)
    try:
        with engine.connect() as conn:
            r = conn.execute("SELECT VERSION()")
            ver = r.scalar()
            print("Connected successfully. MySQL version:", ver)
    except OperationalError as e:
        print("OperationalError:", e)
    except Exception as e:
        print("Error:", type(e).__name__, e)

if __name__ == "__main__":
    main()