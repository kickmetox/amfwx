"""Webcam capture and tethering via optional OpenCV."""

from __future__ import annotations

import time
from pathlib import Path

try:
    import cv2
except ImportError:  # optional
    cv2 = None


class WebcamError(RuntimeError):
    pass


class CameraInfo:
    def __init__(self, index, name=""):
        self.index = None if index is None else int(index)
        self.name = name or f"Camera {index}"

    def __repr__(self):
        return f"CameraInfo({self.index}, {self.name!r})"


def available():
    return cv2 is not None


def list_pnp_cameras():
    import json
    import subprocess
    command = ("Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue "
               "| Select-Object FriendlyName,InstanceId | ConvertTo-Json -Compress")
    try:
        process = subprocess.run(["powershell", "-NoProfile", "-Command", command],
                                 capture_output=True, text=True, timeout=20)
        data = json.loads(process.stdout or "[]")
    except Exception:
        return []
    if isinstance(data, dict):
        data = [data]
    result = []
    for item in data:
        name = str(item.get("FriendlyName") or "")
        path = str(item.get("InstanceId") or "")
        if name:
            result.append(CameraInfo(None, name))
            result[-1].path = path
            result[-1].kind = "pnp"
    return result


def list_cameras(max_index=8):
    if cv2 is None:
        return []
    try:
        cv2.setLogLevel(0)
    except Exception:
        pass
    found = []
    for index in range(int(max_index)):
        capture = cv2.VideoCapture(index)
        try:
            if capture.isOpened():
                found.append(CameraInfo(index))
        finally:
            capture.release()
    return found


class Webcam:
    def __init__(self, index=0, width=1280, height=720, fps=30):
        if cv2 is None:
            raise WebcamError("OpenCV fehlt: pip install opencv-python-headless")
        self.index = None if index is None else int(index)
        self.capture = cv2.VideoCapture(self.index)
        if not self.capture.isOpened():
            raise WebcamError(f"Kamera {index} nicht erreichbar")
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))
        self.capture.set(cv2.CAP_PROP_FPS, int(fps))

    @property
    def width(self):
        return int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self):
        return int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def read(self):
        ok, frame = self.capture.read()
        if not ok or frame is None:
            raise WebcamError("kein Kamerabild")
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
            "width": cv2.CAP_PROP_FRAME_WIDTH,
            "height": cv2.CAP_PROP_FRAME_HEIGHT,
            "fps": cv2.CAP_PROP_FPS,
        }
        if name not in properties:
            raise WebcamError(f"unbekannte Einstellung: {name}")
        return bool(self.capture.set(properties[name], float(value)))

    def tether(self, directory, count=10, interval=1.0, prefix="cam",
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
            path = folder / f"{prefix}_{time.strftime('%Y%m%d_%H%M%S')}_{index:03d}{suffix}"
            image.save(path)
            saved.append(str(path))
            if index < count:
                time.sleep(max(0.0, float(interval)))
        return saved


    def record(self, path, seconds=5.0, fps=25.0):
        if self.width <= 0 or self.height <= 0:
            raise WebcamError("ungueltige Bildgroesse")
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"),
                                 float(fps), (self.width, self.height))
        if not writer.isOpened():
            raise WebcamError("VideoWriter konnte nicht geoeffnet werden")
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
