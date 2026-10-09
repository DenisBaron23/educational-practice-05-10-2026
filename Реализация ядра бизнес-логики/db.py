import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "Инфраструктура данных и ETL" / "partner_system.db"


def get_connection(db_path=None):
    conn = sqlite3.connect(str(db_path or DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
