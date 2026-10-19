"""SQLite source-of-truth storage for the synthetic registered-email dataset."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from dataset_generator import generate_emails
from bloom_filter import normalize_email

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "bloomcheck.sqlite3"


def connect(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


class _ClosingConnection:
    """Context manager which commits/rolls back and always closes SQLite."""
    def __init__(self, path: str | Path):
        self.path = path
        self.connection: sqlite3.Connection | None = None

    def __enter__(self) -> sqlite3.Connection:
        self.connection = connect(self.path)
        return self.connection

    def __exit__(self, exc_type, exc, traceback) -> None:
        assert self.connection is not None
        try:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
        finally:
            self.connection.close()


def closing_connect(db_path: str | Path = DEFAULT_DB_PATH) -> _ClosingConnection:
    return _ClosingConnection(db_path)


def initialize_database(db_path: str | Path = DEFAULT_DB_PATH, emails: Iterable[str] | None = None, reset: bool = False) -> int:
    dataset = list(dict.fromkeys(normalize_email(email) for email in (generate_emails() if emails is None else emails)))
    with closing_connect(db_path) as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS registered_emails (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE)")
        if reset:
            connection.execute("DELETE FROM registered_emails")
        connection.executemany("INSERT OR IGNORE INTO registered_emails(email) VALUES (?)", [(email,) for email in dataset])
        connection.execute("CREATE INDEX IF NOT EXISTS idx_registered_emails_email ON registered_emails(email)")
        row = connection.execute("SELECT COUNT(*) AS count FROM registered_emails").fetchone()
        return int(row["count"])


def is_registered(email: str, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    connection = connect(db_path)
    try:
        row = connection.execute("SELECT 1 FROM registered_emails WHERE email = ? LIMIT 1", (normalize_email(email),)).fetchone()
        return row is not None
    finally:
        connection.close()


def get_all_emails(db_path: str | Path = DEFAULT_DB_PATH) -> list[str]:
    connection = connect(db_path)
    try:
        rows = connection.execute("SELECT email FROM registered_emails ORDER BY id").fetchall()
        return [str(row["email"]) for row in rows]
    finally:
        connection.close()


def count_emails(db_path: str | Path = DEFAULT_DB_PATH) -> int:
    connection = connect(db_path)
    try:
        return int(connection.execute("SELECT COUNT(*) FROM registered_emails").fetchone()[0])
    finally:
        connection.close()
