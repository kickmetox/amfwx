"""Minimal eSCL/AirScan client for network scanners."""

from __future__ import annotations

import base64
import ssl
from pathlib import Path
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from .net import HttpClient, NetworkError


class EsclError(RuntimeError):
    pass


def _settings_xml(resolution=300, color="RGB24", document_format="image/jpeg",
                  duplex=False, region=None, source="Platen"):
    width, height = (2481, 3507)
    x_offset = y_offset = 0
    if region:
        x_offset, y_offset, width, height = [int(value) for value in region]
    feeder = str(source).lower() in ("adf", "feeder")
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<scan:ScanSettings xmlns:scan="http://schemas.hp.com/imaging/escl/2011/05/03"
 xmlns:pwg="http://www.pwg.org/schemas/2010/12/sm">
  <pwg:Version>2.6</pwg:Version>
  <pwg:ScanRegions><pwg:ScanRegion>
    <pwg:XOffset>{x_offset}</pwg:XOffset><pwg:YOffset>{y_offset}</pwg:YOffset>
    <pwg:Width>{width}</pwg:Width><pwg:Height>{height}</pwg:Height>
    <pwg:ContentRegionUnits>escl:ThreeHundredthsOfInches</pwg:ContentRegionUnits>
  </pwg:ScanRegion></pwg:ScanRegions>
  <pwg:InputSource>{'Feeder' if feeder else 'Platen'}</pwg:InputSource>
  <scan:DocumentFormatExt>{document_format}</scan:DocumentFormatExt>
  <pwg:DocumentFormat>{document_format}</pwg:DocumentFormat>
  <scan:XResolution>{int(resolution)}</scan:XResolution>
  <scan:YResolution>{int(resolution)}</scan:YResolution>
  <scan:ColorMode>{color}</scan:ColorMode>
  <scan:Duplex>{'true' if duplex else 'false'}</scan:Duplex>
</scan:ScanSettings>'''.encode("utf-8")


@dataclass
class EsclCapabilities:
    make: str = ""
    model: str = ""
    adf: bool = False
    platen: bool = False
    duplex: bool = False
    resolutions: list = field(default_factory=list)
    color_modes: list = field(default_factory=list)


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def parse_capabilities(xml):
    root = ET.fromstring(xml)
    result = EsclCapabilities()
    for element in root.iter():
        name = _local(element.tag)
        text = (element.text or "").strip()
        if name == "MakeAndModel":
            result.model = text
        elif name == "Make":
            result.make = text
        elif name == "Adf":
            result.adf = True
        elif name == "Platen":
            result.platen = True
        elif name == "Duplex":
            result.duplex = text.lower() == "true"
        elif name in ("XResolution", "YResolution"):
            try:
                value = int(text)
            except ValueError:
                continue
            if value not in result.resolutions:
                result.resolutions.append(value)
        elif name in ("ColorMode", "ColorModes"):
            if text and text not in result.color_modes:
                result.color_modes.append(text)
    return result


class EsclScanner:
    def __init__(self, host, port=80, timeout=15.0, secure=False,
                 username=None, password=None, certfile=None,
                 keyfile=None, verify_tls=False):
        self.host = str(host)
        self.port = int(port)
        self.timeout = float(timeout)
        scheme = "https" if secure else "http"
        self.base_url = f"{scheme}://{self.host}:{self.port}"
        context = None
        if secure and not verify_tls:
            context = ssl._create_unverified_context()
        self.client = HttpClient(self.base_url, timeout=self.timeout,
                                 certfile=certfile, keyfile=keyfile,
                                 ssl_context=context)
        self.auth_headers = {}
        if username is not None:
            token = base64.b64encode(
                f"{username}:{password or ''}".encode("utf-8")).decode("ascii")
            self.auth_headers["Authorization"] = f"Basic {token}"

    def capabilities(self):
        try:
            response = self.client.request("/eSCL/ScannerCapabilities",
                                           headers=self.auth_headers)
            return response["body"].decode("utf-8", "replace")
        except NetworkError as error:
            raise EsclError(str(error)) from error

    def _create_job(self, payload, feeder=False):
        try:
            response = self.client.request(
                "/eSCL/ScanJobs", method="POST", data=payload,
                headers={"Content-Type": "text/xml",
                         **self.auth_headers})
        except NetworkError as error:
            raise EsclError(str(error)) from error
        if response["status"] not in (200, 201, 202):
            if feeder and response["status"] in (409, 500, 503):
                raise EsclError("Der automatische Einzug ist leer oder noch nicht bereit.")
            raise EsclError(f"ScanJobs HTTP {response['status']}")
        location = (response["headers"].get("Location") or
                    response["headers"].get("location"))
        if not location:
            raise EsclError("ScanJobs ohne Location")
        if location.startswith("http"):
            return location.rstrip("/")
        return self.base_url + "/" + location.lstrip("/")

    def _delete_job(self, job_base):
        try:
            self.client.request(job_base, method="DELETE")
        except NetworkError:
            pass

    def _adf_loaded(self):
        try:
            response = self.client.request("/eSCL/ScannerStatus",
                                           headers=self.auth_headers)
        except NetworkError:
            return None
        if response["status"] != 200:
            return None
        text = response["body"].decode("utf-8", "replace")
        if "ScannerAdfLoaded" in text:
            return True
        if "ScannerAdfEmpty" in text:
            return False
        return None

    def scan_pages(self, directory, prefix="page", resolution=300,
                   color="RGB24", document_format="image/jpeg",
                   max_pages=50, duplex=False, region=None,
                   source="Platen"):
        folder = Path(directory)
        folder.mkdir(parents=True, exist_ok=True)
        payload = _settings_xml(resolution, color, document_format,
                                duplex, region, source)
        feeder = str(source).lower() in ("adf", "feeder")
        job_base = None
        pages = []
        for index in range(1, int(max_pages) + 1):
            if job_base is None:
                job_base = self._create_job(payload, feeder=feeder)
            suffix = Path(prefix).suffix or ".jpg"
            target = folder / f"{Path(prefix).stem}_{index:03d}{suffix}"
            try:
                document = self.client.request(job_base + "/NextDocument")
            except NetworkError as error:
                raise EsclError(str(error)) from error
            if document["status"] in (204, 404):
                if feeder and pages and self._adf_loaded() is True:
                    self._delete_job(job_base)
                    job_base = None
                    continue
                self._delete_job(job_base)
                break
            if document["status"] == 503:
                continue
            if document["status"] != 200:
                raise EsclError(f"NextDocument HTTP {document['status']}")
            target.write_bytes(document["body"])
            pages.append(str(target))
        return pages

    def capabilities_info(self):
        return parse_capabilities(self.capabilities())

    def scan(self, path, resolution=300, color="RGB24",
             document_format="image/jpeg", duplex=False, region=None,
             source="Platen"):
        payload = _settings_xml(resolution, color, document_format,
                                duplex, region, source)
        try:
            response = self.client.request(
                "/eSCL/ScanJobs", method="POST", data=payload,
                headers={"Content-Type": "text/xml",
                         **self.auth_headers})
        except NetworkError as error:
            raise EsclError(str(error)) from error
        if response["status"] not in (200, 201, 202):
            if feeder and response["status"] in (409, 500, 503):
                raise EsclError("Der automatische Einzug ist leer oder noch nicht bereit.")
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
