"""Camera driver plugin API."""

from __future__ import annotations

from pathlib import Path


class CameraPluginError(RuntimeError):
    pass


class CameraDriver:
    name = "camera"

    def available(self):
        return False

    def open(self):
        raise NotImplementedError

    def read(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def settings(self):
        return {}

    def set_control(self, name, value):
        raise CameraPluginError("Steuerung nicht unterstützt")


class WebcamDriver(CameraDriver):
    name = "uvc"

    def __init__(self, index=0, width=1280, height=720):
        from .camera import Webcam
        self._camera = Webcam(index, width=width, height=height)

    def available(self):
        return True

    def open(self):
        return self

    def read(self):
        return self._camera.read()

    def close(self):
        self._camera.close()

    def settings(self):
        return self._camera.settings()

    def set_control(self, name, value):
        return self._camera.set_control(name, value)


class IpCameraDriver(CameraDriver):
    name = "ip"

    def __init__(self, url, width=1280, height=720):
        from .ipcam import IpCamera
        self._camera = IpCamera(url, width=width, height=height)

    def available(self):
        return True

    def open(self):
        return self

    def read(self):
        return self._camera.read()

    def close(self):
        self._camera.close()

    def settings(self):
        return self._camera.settings()

    def set_control(self, name, value):
        return self._camera.set_control(name, value)


_DRIVERS = {"uvc": WebcamDriver, "ip": IpCameraDriver}


def register_camera_driver(name, factory, replace=False):
    key = str(name).lower()
    if not key:
        raise CameraPluginError("Treibername fehlt")
    if key in _DRIVERS and not replace:
        raise CameraPluginError(f"Treiber bereits registriert: {key}")
    _DRIVERS[key] = factory
    return factory


def unregister_camera_driver(name):
    return _DRIVERS.pop(str(name).lower(), None)


def list_camera_drivers():
    return sorted(_DRIVERS)


def load_camera_plugins():
    import importlib.metadata
    try:
        entries = importlib.metadata.entry_points(group="amfwx.cameras")
    except TypeError:
        entries = importlib.metadata.entry_points().get("amfwx.cameras", [])
    for entry in entries:
        if entry.name.lower() not in _DRIVERS:
            try:
                register_camera_driver(entry.name, entry.load())
            except Exception:
                continue
    return list_camera_drivers()


def create_camera_driver(name, **kwargs):
    key = str(name).lower()
    if key not in _DRIVERS:
        load_camera_plugins()
    if key not in _DRIVERS:
        raise CameraPluginError(f"unbekannter Kameratreiber: {name}")
    return _DRIVERS[key](**kwargs)
