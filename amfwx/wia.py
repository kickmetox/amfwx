"""Optional WIA scanner enumeration via COM automation."""

from __future__ import annotations


WIA_FORMATS = {
    "bmp": "{B96B3CAB-0728-11D3-9D7B-0000F81EF32E}",
    "png": "{B96B3CAF-0728-11D3-9D7B-0000F81EF32E}",
    "jpg": "{B96B3CAE-0728-11D3-9D7B-0000F81EF32E}",
    "jpeg": "{B96B3CAE-0728-11D3-9D7B-0000F81EF32E}",
    "tif": "{B96B3CB1-0728-11D3-9D7B-0000F81EF32E}",
    "tiff": "{B96B3CB1-0728-11D3-9D7B-0000F81EF32E}",
}


class WiaError(RuntimeError):
    pass


class WiaDevice:
    def __init__(self, device_id, name, kind):
        self.device_id = device_id
        self.name = name
        self.kind = kind

    def __repr__(self):
        return f"WiaDevice({self.name!r}, {self.kind!r})"


def list_wia_devices():
    try:
        import comtypes.client
    except ImportError:
        return []
    try:
        manager = comtypes.client.CreateObject("WIA.DeviceManager")
    except Exception:
        return []
    devices = []
    try:
        infos = manager.DeviceInfos
        for index in range(1, infos.Count + 1):
            info = infos.Item(index)
            try:
                name = str(info.Properties("Name").Value)
            except Exception:
                name = ""
            try:
                kind = str(info.Properties("Type").Value)
            except Exception:
                kind = ""
            devices.append(WiaDevice(str(info.DeviceID), name, kind))
    except Exception:
        return []
    return devices


class WiaScanner:
    def __init__(self, device_id=None, index=1):
        self.device_id = device_id
        self.index = int(index)

    def _connect(self):
        try:
            import comtypes.client
        except ImportError as error:
            raise WiaError("comtypes ist nicht installiert: pip install comtypes") from error
        try:
            manager = comtypes.client.CreateObject("WIA.DeviceManager")
            infos = manager.DeviceInfos
            if self.device_id:
                for position in range(1, infos.Count + 1):
                    info = infos.Item(position)
                    if str(info.DeviceID) == str(self.device_id):
                        return info.Connect()
                raise WiaError(f"WIA-Geraet nicht gefunden: {self.device_id}")
            if not 1 <= self.index <= infos.Count:
                raise WiaError(f"WIA-Index ausserhalb: {self.index}")
            return infos.Item(self.index).Connect()
        except WiaError:
            raise
        except Exception as error:
            raise WiaError(f"WIA-Verbindung fehlgeschlagen: {error}") from error

    def acquire(self, path, image_format="png", dpi=None, color=None,
                duplex=False, adf=False):
        device = self._connect()
        try:
            items = device.Items
            count = max(1, int(items.Count))
            if not adf:
                count = 1
            pages = []
            for index in range(1, count + 1):
                item = items.Item(index)
                for property_id, value in self._settings(dpi, color, duplex):
                    try:
                        item.Properties(property_id).Value = value
                    except Exception:
                        pass
                image = item.Transfer(WIA_FORMATS.get(
                    str(image_format).lower(), WIA_FORMATS["png"]))
                target = path if count == 1 else self._page_path(path, index)
                image.SaveFile(str(target))
                pages.append(str(target))
            return pages[0] if len(pages) == 1 else pages
        except Exception as error:
            raise WiaError(f"WIA-Transfer fehlgeschlagen: {error}") from error

    @staticmethod
    def _settings(dpi, color, duplex):
        values = []
        if dpi:
            values.extend((("6146", int(dpi)), ("6147", int(dpi))))
        if color is not None:
            values.append(("6148", int(color)))
        if duplex:
            values.append(("3088", 1))
        return values

    @staticmethod
    def _page_path(path, index):
        from pathlib import Path
        path = Path(path)
        return str(path.with_name(f"{path.stem}_{index:03d}{path.suffix}"))

    def acquire_pages(self, directory, prefix="scan", **kwargs):
        from pathlib import Path
        folder = Path(directory)
        folder.mkdir(parents=True, exist_ok=True)
        return self.acquire(str(folder / f"{prefix}.png"), adf=True, **kwargs)
