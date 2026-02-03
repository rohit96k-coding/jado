
import sqlite3
import os
import sys

print("Running Diagnostic...")

# 1. Check Database
db_path = r"c:\Users\sagar\my project\_legacy\jado\data\sami_memory.db"
print(f"Checking Database at: {db_path}")

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Database Integrity: OK. Tables: {tables}")
        conn.close()
    except sqlite3.DatabaseError as e:
        print(f"Database Integrity: ERROR - {e}")
        print("RECOMMENDATION: Delete sami_memory.db")
    except Exception as e:
        print(f"Database Check Failed: {e}")
else:
    print("Database file does not exist (will be created on start).")

# 2. Check Imports
print("\nChecking Imports...")
try:
    import flask
    import flask_socketio
    import mss
    import PIL
    import psutil
    import requests
    # import cv2 # older error
    print("Core Imports: OK")
except ImportError as e:
    print(f"Import Error: {e}")

print("\nDiagnostic Complete.")
