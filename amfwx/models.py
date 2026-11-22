"""Small model layer for AMFWX views (ListModel/TableModel)."""

from __future__ import annotations


class Model:
    def __init__(self):
        self._listeners = []

    def connect(self, callback):
        self._listeners.append(callback)
        return callback

    def disconnect(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def changed(self):
        for callback in list(self._listeners):
            callback(self)

    def row_count(self):
        return 0

    def column_count(self):
        return 0

    def data(self, row, column=0, role="display"):
        return ""


class ListModel(Model):
    def __init__(self, items=None):
        super().__init__()
        self.items = list(items or [])

    def row_count(self):
        return len(self.items)

    def column_count(self):
        return 1

    def data(self, row, column=0, role="display"):
        if 0 <= row < len(self.items):
            return self.items[row]
        return ""

    def set_data(self, row, value):
        if 0 <= row < len(self.items):
            self.items[row] = value
            self.changed()
            return True
        return False

    def append(self, value):
        self.items.append(value)
        self.changed()
        return len(self.items) - 1

    def remove(self, row):
        if 0 <= row < len(self.items):
            del self.items[row]
            self.changed()
            return True
        return False

    def sort(self, reverse=False):
        self.items.sort(key=lambda value: str(value).lower(), reverse=reverse)
        self.changed()

    def clear(self):
        self.items.clear()
        self.changed()


class TableModel(Model):
    def __init__(self, headers=None, rows=None):
        super().__init__()
        self.headers = list(headers or ["Spalte"])
        self.rows = [list(row) for row in (rows or [])]

    def row_count(self):
        return len(self.rows)

    def column_count(self):
        return len(self.headers)

    def data(self, row, column=0, role="display"):
        if 0 <= row < len(self.rows):
            values = self.rows[row]
            if 0 <= column < len(values):
                return values[column]
        return ""

    def set_data(self, row, column, value):
        if not 0 <= row < len(self.rows):
            return False
        values = self.rows[row]
        while len(values) <= column:
            values.append("")
        values[column] = value
        self.changed()
        return True

    def append_row(self, values):
        row = list(values)
        while len(row) < len(self.headers):
            row.append("")
        self.rows.append(row)
        self.changed()
        return len(self.rows) - 1

    def remove_row(self, row):
        if 0 <= row < len(self.rows):
            del self.rows[row]
            self.changed()
            return True
        return False

    def set_headers(self, headers):
        self.headers = list(headers)
        self.changed()

    def sort(self, column=0, reverse=False):
        def key(row):
            return str(row[column]) if column < len(row) else ""
        self.rows.sort(key=key, reverse=reverse)
        self.changed()

    def clear(self):
        self.rows.clear()
        self.changed()


class SortFilterModel(Model):
    def __init__(self, source, column=0, query=""):
        super().__init__()
        self.source = source
        self.column = int(column)
        self.query = str(query)
        self._view = []
        source.connect(self._source_changed)
        self._rebuild()

    def _source_changed(self, _source):
        self._rebuild()
        self.changed()

    def _rebuild(self):
        rows = [row for row in range(self.source.row_count())
                if self._matches(row)]
        rows.sort(key=lambda row: str(self.source.data(row,
                                                       self.column)).lower())
        self._view = rows

    def _matches(self, row):
        if not self.query:
            return True
        needle = self.query.lower()
        for column in range(self.source.column_count()):
            if needle in str(self.source.data(row, column)).lower():
                return True
        return False

    def set_query(self, query):
        self.query = str(query)
        self._rebuild()
        self.changed()

    def row_count(self):
        return len(self._view)

    def column_count(self):
        return self.source.column_count()

    def data(self, row, column=0, role="display"):
        if 0 <= row < len(self._view):
            return self.source.data(self._view[row], column, role)
        return ""
