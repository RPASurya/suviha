import os, sqlite3
from pathlib import Path

DB_PATH = os.getenv("UCL_DATABASE_PATH", "./data/ucl.sqlite3")


def connect():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY, value TEXT NOT NULL DEFAULT ''
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS conversions (
            id TEXT PRIMARY KEY, created_at TEXT NOT NULL, source_type TEXT NOT NULL,
            target_version TEXT NOT NULL, input_name TEXT NOT NULL, status TEXT NOT NULL,
            output_path TEXT, report TEXT
        )""")


def get_setting(key, default=""):
    with connect() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default


def set_setting(key, value):
    with connect() as conn:
        conn.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))


def add_conversion(row):
    with connect() as conn:
        conn.execute("INSERT INTO conversions(id,created_at,source_type,target_version,input_name,status,output_path,report) VALUES(?,?,?,?,?,?,?,?)", row)


def list_conversions(limit=30):
    with connect() as conn:
        rows = conn.execute("SELECT id,created_at,source_type,target_version,input_name,status,report FROM conversions ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]
