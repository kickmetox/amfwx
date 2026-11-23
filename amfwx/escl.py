"""Minimal eSCL/AirScan client for network scanners."""

from __future__ import annotations

from pathlib import Path

from .net import HttpClient, NetworkError


class EsclError(RuntimeError):
    pass


def _settings_xml(resolution=300, color="RGB24", document_format="image/jpeg",
                  duplex=False, region=None):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<scan:ScanSettings xmlns:scan="http://schemas.hp.com/imaging/escl/2011/05/03"
 xmlns:pwg="http://www.pwg.org/schemas/2010/12/sm">
  <pwg:Version>2.63</pwg:Version>
  <scan:DocumentFormatExt>{document_format}</scan:DocumentFormatExt>
  <scan:XResolution>{int(resolution)}</scan:XResolution>
  <scan:YResolution>{int(resolution)}</scan:YResolution>
  <scan:ColorMode>{color}</scan:ColorMode>
  <scan:Duplex>{'true' if duplex else 'false'}</scan:Duplex>
{_region_xml(region)}
</scan:ScanSettings>'''.encode("utf-8")


def _region_xml(region):
    if not region:
        return ""
    x, y, width, height = [int(value) for value in region]
    return (
        "  <pwg:ScanRegions><pwg:ScanRegion>"
        f"<pwg:XOffset>{x}</pwg:XOffset>"
        f"<pwg:YOffset>{y}</pwg:YOffset>"
        f"<pwg:Width>{width}</pwg:Width>"
        f"<pwg:Height>{height}</pwg:Height>"
        "<pwg:ContentRegionUnits>escl:ThreeHundredthsOfInches"
        "</pwg:ContentRegionUnits>"
        "</pwg:ScanRegion></pwg:ScanRegions>")


class EsclScanner:
    def __init__(self, host, port=80, timeout=15.0, secure=False):
        self.host = str(host)
        self.port = int(port)
        self.timeout = float(timeout)
        scheme = "https" if secure else "http"
        self.base_url = f"{scheme}://{self.host}:{self.port}"
        self.client = HttpClient(self.base_url, timeout=self.timeout)

    def capabilities(self):
        try:
            return self.client.text("/eSCL/ScannerCapabilities")
        except NetworkError as error:
            raise EsclError(str(error)) from error

    def scan_pages(self, directory, prefix="page", resolution=300,
                   color="RGB24", document_format="image/jpeg",
                   max_pages=50, duplex=False, region=None):
        folder = Path(directory)
        folder.mkdir(parents=True, exist_ok=True)
        payload = _settings_xml(resolution, color, document_format,
                                duplex, region)
        try:
            response = self.client.request(
                "/eSCL/ScanJobs", method="POST", data=payload,
                headers={"Content-Type": "text/xml"})
        except NetworkError as error:
            raise EsclError(str(error)) from error
        if response["status"] not in (200, 201, 202):
            raise EsclError(f"ScanJobs HTTP {response['status']}")
        location = (response["headers"].get("Location") or
                    response["headers"].get("location"))
        if not location:
            raise EsclError("ScanJobs ohne Location")
        if location.startswith("http"):
            base = location.rstrip("/")
        else:
            base = self.base_url + "/" + location.lstrip("/")
        pages = []
        for index in range(1, int(max_pages) + 1):
            suffix = Path(prefix).suffix or ".jpg"
            target = folder / f"{Path(prefix).stem}_{index:03d}{suffix}"
            try:
                document = self.client.request(base + "/NextDocument")
            except NetworkError as error:
                raise EsclError(str(error)) from error
            if document["status"] in (204, 404):
                break
            if document["status"] != 200:
                raise EsclError(f"NextDocument HTTP {document['status']}")
            target.write_bytes(document["body"])
            pages.append(str(target))
        return pages

    def scan(self, path, resolution=300, color="RGB24",
             document_format="image/jpeg", duplex=False, region=None):
        payload = _settings_xml(resolution, color, document_format,
                                duplex, region)
        try:
            response = self.client.request(
                "/eSCL/ScanJobs", method="POST", data=payload,
                headers={"Content-Type": "text/xml"})
        except NetworkError as error:
            raise EsclError(str(error)) from error
        if response["status"] not in (200, 201, 202):
            raise EsclError(f"ScanJobs HTTP {response['status']}")
        location = response["headers"].get("Location") or response["headers"].get("location")
        if not location:
            raise EsclError("ScanJobs ohne Location")
        if location.startswith("http"):
            document_url = location.rstrip("/") + "/NextDocument"
        else:
            document_url = self.base_url + "/" + location.lstrip("/") + "/NextDocument"
        try:
            document = self.client.request(document_url)
        except NetworkError as error:
            raise EsclError(str(error)) from error
        if document["status"] != 200:
            raise EsclError(f"NextDocument HTTP {document['status']}")
        target = Path(path)
        target.write_bytes(document["body"])
        return str(target)
