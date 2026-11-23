"""Small HTTP client without third-party dependencies."""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from urllib.parse import urlparse, urlsplit


class NetworkError(RuntimeError):
    pass


class HttpClient:
    def __init__(self, base_url="", headers=None, timeout=30.0,
                 max_bytes=8 * 1024 * 1024, username=None, password=None):
        self.base_url = str(base_url).rstrip("/")
        self.headers = dict(headers or {})
        self.timeout = float(timeout)
        self.max_bytes = int(max_bytes)
        self.username = username
        self.password = password
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

    @staticmethod
    def _digest_header(challenge, method, uri, username, password):
        values = {}
        challenge = challenge.replace("Digest ", "", 1)
        for part in challenge.split(","):
            if "=" in part:
                key, value = part.split("=", 1)
                values[key.strip()] = value.strip().strip('"')
        realm = values.get("realm", "")
        nonce = values.get("nonce", "")
        qop = values.get("qop", "").split(",")[0].strip()
        opaque = values.get("opaque", "")
        algorithm = values.get("algorithm", "MD5")
        ha1 = hashlib.md5(f"{username}:{realm}:{password}".encode()).hexdigest()
        ha2 = hashlib.md5(f"{method}:{uri}".encode()).hexdigest()
        if qop in ("auth", "auth-int"):
            nc = "00000001"
            cnonce = "amfwx"
            response = hashlib.md5(
                f"{ha1}:{nonce}:{nc}:{cnonce}:{qop}:{ha2}".encode()).hexdigest()
            return (f'Digest username="{username}", realm="{realm}", '
                    f'nonce="{nonce}", uri="{uri}", response="{response}", '
                    f'qop={qop}, nc={nc}, cnonce="{cnonce}"' +
                    (f', opaque="{opaque}"' if opaque else ""))
        response = hashlib.md5(f"{ha1}:{nonce}:{ha2}".encode()).hexdigest()
        return (f'Digest username="{username}", realm="{realm}", '
                f'nonce="{nonce}", uri="{uri}", response="{response}"' +
                (f', opaque="{opaque}"' if opaque else ""))

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
            if (error.code == 401 and self.username is not None and
                    "Digest" in error.headers.get("WWW-Authenticate", "")):
                auth = self._digest_header(
                    error.headers.get("WWW-Authenticate", ""),
                    method.upper(), urlsplit(self._url(path)).path,
                    self.username, self.password or "")
                retry_headers = dict(request_headers)
                retry_headers["Authorization"] = auth
                request = urllib.request.Request(self._url(path), data=body,
                                                 method=method.upper(),
                                                 headers=retry_headers)
                try:
                    with urllib.request.urlopen(request, timeout=self.timeout) as response:
                        return {"status": response.status,
                                "headers": dict(response.headers),
                                "body": response.read(self.max_bytes)}
                except urllib.error.HTTPError as retry_error:
                    return {"status": retry_error.code,
                            "headers": dict(retry_error.headers),
                            "body": retry_error.read(self.max_bytes)}
            return {"status": error.code, "headers": dict(error.headers),
                    "body": raw}
        except urllib.error.URLError as error:
            raise NetworkError(f"nicht erreichbar: {error.reason}") from error

    def text(self, path, **kwargs):
        return self.request(path, **kwargs)["body"].decode("utf-8", "replace")

    def json(self, path, **kwargs):
        return json.loads(self.text(path, **kwargs))
