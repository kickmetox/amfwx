"""GoPro HTTP control (camera Wi-Fi)."""

from __future__ import annotations

from .net import HttpClient, NetworkError


class GoProError(RuntimeError):
    pass


class GoProCamera:
    def __init__(self, host="10.5.5.9", port=8080, timeout=8.0):
        self.client = HttpClient(f"http://{host}:{port}", timeout=timeout)
        self.host = host
        self.port = int(port)

    def _get(self, path):
        try:
            return self.client.json(path)
        except NetworkError as error:
            raise GoProError(str(error)) from error

    def status(self):
        return self._get("/gp/gpControl/status")

    def shutter(self, enabled=True):
        return self._get(f"/gp/gpControl/command/shutter?p={1 if enabled else 0}")

    def take_photo(self):
        return self.shutter(True)

    def mode(self, value):
        return self._get(f"/gp/gpControl/command/mode?p={int(value)}")

    def media_list(self):
        return self._get("/gpMediaList")

    def tether(self, directory, count=1, interval=2.0):
        import time
        from pathlib import Path
        folder = Path(directory)
        folder.mkdir(parents=True, exist_ok=True)
        shots = []
        for index in range(1, int(count) + 1):
            self.take_photo()
            shots.append({"index": index,
                          "time": time.strftime("%Y-%m-%dT%H:%M:%S")})
            if index < count:
                time.sleep(max(0.0, float(interval)))
        return shots
