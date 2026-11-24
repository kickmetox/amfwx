"""IP/RTSP camera capture through OpenCV."""

from __future__ import annotations

import time
from pathlib import Path

try:
    import cv2
except ImportError:  # optional
    cv2 = None


class IpCameraError(RuntimeError):
    pass


class IpCamera:
    def __init__(self, url, width=1280, height=720):
        if cv2 is None:
            raise IpCameraError("OpenCV fehlt")
        self.url = str(url)
        self.capture = cv2.VideoCapture(self.url)
        if not self.capture.isOpened():
            raise IpCameraError(f"IP-Kamera nicht erreichbar: {url}")
        if width:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
        if height:
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))

    @property
    def width(self):
        return int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self):
        return int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def read(self):
        ok, frame = self.capture.read()
        if not ok or frame is None:
            raise IpCameraError("kein Bild von der IP-Kamera")
        from PIL import Image
        return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    def settings(self):
        return {
            "width": self.width, "height": self.height,
            "fps": float(self.capture.get(cv2.CAP_PROP_FPS)),
            "brightness": float(self.capture.get(cv2.CAP_PROP_BRIGHTNESS)),
            "contrast": float(self.capture.get(cv2.CAP_PROP_CONTRAST)),
            "saturation": float(self.capture.get(cv2.CAP_PROP_SATURATION)),
            "gain": float(self.capture.get(cv2.CAP_PROP_GAIN)),
            "exposure": float(self.capture.get(cv2.CAP_PROP_EXPOSURE)),
            "focus": float(self.capture.get(cv2.CAP_PROP_FOCUS)),
        }

    def set_control(self, name, value):
        properties = {
            "brightness": cv2.CAP_PROP_BRIGHTNESS,
            "contrast": cv2.CAP_PROP_CONTRAST,
            "saturation": cv2.CAP_PROP_SATURATION,
            "gain": cv2.CAP_PROP_GAIN,
            "exposure": cv2.CAP_PROP_EXPOSURE,
            "focus": cv2.CAP_PROP_FOCUS,
        }
        if name not in properties:
            raise IpCameraError(f"unbekannte Einstellung: {name}")
        return bool(self.capture.set(properties[name], float(value)))

    def tether(self, directory, count=10, interval=1.0, prefix="ipcam",
               chroma_key=None):
        folder = Path(directory)
        folder.mkdir(parents=True, exist_ok=True)
        saved = []
        for index in range(1, int(count) + 1):
            image = self.read()
            if chroma_key is not None:
                from .chroma import chroma_key as apply_key
                image = apply_key(image, chroma_key)
            suffix = ".png" if image.mode == "RGBA" else ".jpg"
            path = folder / (f"{prefix}_{time.strftime('%Y%m%d_%H%M%S')}"
                             f"_{index:03d}{suffix}")
            image.save(path)
            saved.append(str(path))
            if index < count:
                time.sleep(max(0.0, float(interval)))
        return saved

    def record(self, path, seconds=5.0, fps=25.0):
        if self.width <= 0 or self.height <= 0:
            raise IpCameraError("ungueltige Bildgroesse")
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"),
                                 float(fps), (self.width, self.height))
        if not writer.isOpened():
            raise IpCameraError("VideoWriter konnte nicht geoeffnet werden")
        deadline = time.monotonic() + float(seconds)
        try:
            while time.monotonic() < deadline:
                ok, frame = self.capture.read()
                if not ok or frame is None:
                    break
                writer.write(frame)
        finally:
            writer.release()
        return str(path)

    def close(self):
        self.capture.release()
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()
