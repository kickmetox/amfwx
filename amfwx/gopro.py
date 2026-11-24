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
        self.mode(1)
        return self.shutter(True)

    def start_video(self):
        self.mode(0)
        return self.shutter(True)

    def stop_video(self):
        return self.shutter(False)

    def mode(self, value):
        return self._get(f"/gp/gpControl/command/mode?p={int(value)}")

    def media_list(self):
        try:
            return self._get("/gp/gpMediaList")
        except GoProError:
            return self._get("/gpMediaList")

    def media_entries(self):
        data = self.media_list()
        entries = []
        for folder in data.get("media", []):
            directory = folder.get("d", "")
            for item in folder.get("fs", []):
                name = item.get("n", "")
                if name:
                    entries.append({"directory": directory,
                                    "name": name,
                                    "size": item.get("s", ""),
                                    "path": f"/videos/DCIM/{directory}/{name}"})
        return entries

    def download_media(self, directory, kind="all"):
        from pathlib import Path
        from urllib.parse import quote
        folder = Path(directory)
        folder.mkdir(parents=True, exist_ok=True)
        saved = []
        for entry in self.media_entries():
            name = entry["name"]
            suffix = Path(name).suffix.lower()
            if kind == "photo" and suffix not in (".jpg", ".jpeg", ".png"):
                continue
            if kind == "video" and suffix not in (".mp4", ".mov"):
                continue
            path = quote(entry["path"], safe="/")
            try:
                response = self.client.request(path)
            except NetworkError as error:
                raise GoProError(str(error)) from error
            target = folder / name
            target.write_bytes(response["body"])
            saved.append(str(target))
        return saved

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
