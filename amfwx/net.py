"""Small HTTP client without third-party dependencies."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from urllib.parse import urlparse


class NetworkError(RuntimeError):
    pass


class HttpClient:
    def __init__(self, base_url="", headers=None, timeout=30.0,
                 max_bytes=8 * 1024 * 1024):
        self.base_url = str(base_url).rstrip("/")
        self.headers = dict(headers or {})
        self.timeout = float(timeout)
        self.max_bytes = int(max_bytes)
        if self.base_url:
            parsed = urlparse(self.base_url)
            if parsed.scheme not in ("http", "https"):
                raise NetworkError("nur http/https erlaubt")

    def _url(self, path):
        if path.startswith("http://") or path.startswith("https://"):
            url = path
        else:
            url = self.base_url + "/" + str(path).lstrip("/")
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise NetworkError("nur http/https erlaubt")
        return url

    def request(self, path, method="GET", data=None, json_data=None,
                headers=None):
        request_headers = dict(self.headers)
        if headers:
            request_headers.update(headers)
        body = None
        if json_data is not None:
            body = json.dumps(json_data).encode("utf-8")
            request_headers.setdefault("Content-Type", "application/json")
        elif data is not None:
            body = data.encode("utf-8") if isinstance(data, str) else data
        request = urllib.request.Request(self._url(path), data=body,
                                         method=method.upper(),
                                         headers=request_headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read(self.max_bytes)
                return {"status": response.status, "headers": dict(response.headers),
                        "body": raw}
        except urllib.error.HTTPError as error:
            raw = error.read(self.max_bytes)
            return {"status": error.code, "headers": dict(error.headers),
                    "body": raw}
        except urllib.error.URLError as error:
            raise NetworkError(f"nicht erreichbar: {error.reason}") from error

    def text(self, path, **kwargs):
        return self.request(path, **kwargs)["body"].decode("utf-8", "replace")

    def json(self, path, **kwargs):
        return json.loads(self.text(path, **kwargs))
