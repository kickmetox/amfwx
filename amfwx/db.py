"""Small SQLite helper for AMFWX applications."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class Database:
    def __init__(self, path=":memory:"):
        self.path = str(path)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row

    def execute(self, sql, parameters=()):
        with self.connection:
            cursor = self.connection.execute(str(sql), tuple(parameters))
        return cursor

    def query(self, sql, parameters=()):
        cursor = self.connection.execute(str(sql), tuple(parameters))
        return cursor.fetchall()

    def one(self, sql, parameters=()):
        rows = self.query(sql, parameters)
        return rows[0] if rows else None

    def executescript(self, script):
        with self.connection:
            self.connection.executescript(str(script))
        return self

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()
