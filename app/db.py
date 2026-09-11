import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "data/vehicles.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_schema():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            body_type TEXT NOT NULL,
            fuel_type TEXT NOT NULL,
            transmission TEXT NOT NULL,
            city TEXT NOT NULL,
            color TEXT NOT NULL,
            price INTEGER NOT NULL,
            km INTEGER NOT NULL,
            year INTEGER NOT NULL,
            seats INTEGER NOT NULL,
            mileage REAL NOT NULL,
            safety_rating INTEGER NOT NULL,
            features TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
