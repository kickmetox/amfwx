# Database and network

## SQLite

```python
from amfwx import Database

with Database("app.db") as db:
    db.execute("create table if not exists notes (text text)")
    db.execute("insert into notes values (?)", ("hello",))
    rows = db.query("select * from notes")
```

`Database` uses parameter binding; no string concatenation is required.

## HTTP

```python
from amfwx import HttpClient

client = HttpClient("https://api.example.com", timeout=15)
data = client.json("/status")
```

Only `http` and `https` are allowed. Responses are capped at 8 MB by default.
`NetworkError` is raised for connection failures.

## Limits

- SQLite only (no ORM)
- no migrations
- HTTP client has no retry/redirect policy beyond urllib defaults
- no OAuth helper
- no WebSocket support
