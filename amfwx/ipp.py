"""Minimal IPP/1.1 and 2.0 Print-Job client."""

from __future__ import annotations

import struct
from pathlib import Path

from .net import HttpClient, NetworkError


class IppError(RuntimeError):
    pass


def _attribute(tag, name, value, value_tag=0x42):
    name_data = str(name).encode("utf-8")
    value_data = str(value).encode("utf-8")
    return (bytes([tag]) + name_data + b"\x00" + bytes([value_tag]) +
            struct.pack(">H", len(value_data)) + value_data)


def build_print_job(printer_uri, job_name, user, document_format,
                    document):
    payload = bytearray()
    payload.extend(b"\x02\x00")             # IPP 2.0
    payload.extend(b"\x00\x02")             # Print-Job
    payload.extend(struct.pack(">I", 1))    # request-id
    payload.append(0x01)                    # operation attributes
    payload.extend(_attribute(0x47, "attributes-charset", "utf-8", 0x47))
    payload.extend(_attribute(0x48, "attributes-natural-language", "en",
                              0x48))
    payload.extend(_attribute(0x45, "printer-uri", printer_uri, 0x45))
    payload.extend(_attribute(0x42, "requesting-user-name", user))
    payload.extend(_attribute(0x42, "job-name", job_name))
    payload.extend(_attribute(0x49, "document-format", document_format,
                              0x49))
    payload.append(0x03)                    # end of attributes
    payload.extend(bytes(document))
    return bytes(payload)


def _decode_value(value_tag, data):
    if value_tag in (0x21, 0x23) and len(data) == 4:
        return struct.unpack(">i", data)[0]
    if value_tag == 0x22 and len(data) == 1:
        return bool(data[0])
    if value_tag in (0x41, 0x42, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49):
        return data.decode("utf-8", "replace")
    if value_tag == 0x32 and len(data) == 8:
        x, y = struct.unpack(">ii", data)
        return (x, y)
    return data


def parse_attributes(data):
    if len(data) < 8:
        raise IppError("IPP-Antwort zu kurz")
    result = {}
    offset = 8
    current = ""
    while offset < len(data):
        tag = data[offset]
        offset += 1
        if tag in (0x01, 0x02, 0x03, 0x04, 0x05):
            current = ""
            if tag == 0x03:
                break
            continue
        end = data.find(b"\x00", offset)
        if end < 0 or end + 3 > len(data):
            break
        name = data[offset:end].decode("utf-8", "replace")
        value_tag = tag
        length = struct.unpack(">H", data[end + 1:end + 3])[0]
        value = data[end + 3:end + 3 + length]
        offset = end + 3 + length
        key = name or current
        current = key
        decoded = _decode_value(value_tag, value)
        if key in result:
            if not isinstance(result[key], list):
                result[key] = [result[key]]
            result[key].append(decoded)
        else:
            result[key] = decoded
    return result


def build_get_attributes(printer_uri, user, requested=None):
    payload = bytearray(b"\x02\x00\x00\x0b\x00\x00\x00\x01")
    payload.append(0x01)
    payload.extend(_attribute(0x47, "attributes-charset", "utf-8", 0x47))
    payload.extend(_attribute(0x48, "attributes-natural-language", "en", 0x48))
    payload.extend(_attribute(0x45, "printer-uri", printer_uri, 0x45))
    payload.extend(_attribute(0x42, "requesting-user-name", user))
    payload.extend(_attribute(0x44, "requested-attributes",
                              requested or "printer-name", 0x44))
    payload.append(0x03)
    return bytes(payload)


def build_job_request(operation, printer_uri, user, job_id=None,
                      which_jobs="not-completed"):
    payload = bytearray(b"\x02\x00")
    payload.extend(struct.pack(">H", int(operation)))
    payload.extend(struct.pack(">I", 1))
    payload.append(0x01)
    payload.extend(_attribute(0x47, "attributes-charset", "utf-8", 0x47))
    payload.extend(_attribute(0x48, "attributes-natural-language", "en", 0x48))
    payload.extend(_attribute(0x45, "printer-uri", printer_uri, 0x45))
    payload.extend(_attribute(0x42, "requesting-user-name", user))
    if job_id is not None:
        payload.extend(_attribute(0x21, "job-id", int(job_id), 0x21))
    if which_jobs:
        payload.extend(_attribute(0x44, "which-jobs", which_jobs, 0x44))
    payload.append(0x03)
    return bytes(payload)


def build_job_attributes_request(printer_uri, user, job_id):
    payload = bytearray(b"\x02\x00\x00\x09\x00\x00\x00\x01")
    payload.append(0x01)
    payload.extend(_attribute(0x47, "attributes-charset", "utf-8", 0x47))
    payload.extend(_attribute(0x48, "attributes-natural-language", "en", 0x48))
    payload.extend(_attribute(0x45, "printer-uri", printer_uri, 0x45))
    payload.extend(_attribute(0x21, "job-id", int(job_id), 0x21))
    payload.extend(_attribute(0x42, "requesting-user-name", user))
    payload.append(0x03)
    return bytes(payload)


def parse_response(data):
    if len(data) < 8:
        raise IppError("IPP-Antwort zu kurz")
    status = struct.unpack(">H", data[2:4])[0]
    job_id = None
    marker = b"job-id\x00"
    index = data.find(marker)
    if index >= 0:
        position = index + len(marker) + 2
        if position + 2 <= len(data):
            length = struct.unpack(">H", data[position:position + 2])[0]
            if length == 4 and position + 6 <= len(data):
                job_id = struct.unpack(">I", data[position + 2:position + 6])[0]
    return {"status": status, "job_id": job_id}


class IppPrinter:
    def __init__(self, host, port=631, path="/ipp/print", secure=False,
                 timeout=20.0, user="AMFWX"):
        self.host = str(host)
        self.port = int(port)
        self.path = str(path)
        self.user = str(user)
        scheme = "https" if secure else "http"
        self.uri = f"ipp://{self.host}:{self.port}{self.path}"
        self.client = HttpClient(f"{scheme}://{self.host}:{self.port}",
                                 timeout=timeout)

    def get_attributes(self, requested=None):
        payload = build_get_attributes(self.uri, self.user, requested)
        try:
            response = self.client.request(
                self.path, method="POST", data=payload,
                headers={"Content-Type": "application/ipp"})
        except NetworkError as error:
            raise IppError(str(error)) from error
        if response["status"] != 200:
            raise IppError(f"IPP HTTP {response['status']}")
        return parse_attributes(response["body"])

    def get_job_attributes(self, job_id):
        payload = build_job_attributes_request(self.uri, self.user, job_id)
        response = self._request(payload)
        return parse_attributes(response["body"])

    def wait_for_job(self, job_id, timeout=60.0, interval=1.0):
        import time
        deadline = time.monotonic() + float(timeout)
        while time.monotonic() < deadline:
            attributes = self.get_job_attributes(job_id)
            state = attributes.get("job-state")
            if state in (7, 8, 9):
                return state
            time.sleep(max(0.1, float(interval)))
        raise IppError("Timeout beim Warten auf den Druckjob")

    def get_jobs(self, which_jobs="not-completed"):
        payload = build_job_request(0x000A, self.uri, self.user,
                                    which_jobs=which_jobs)
        response = self._request(payload)
        return parse_attributes(response["body"])

    def cancel_job(self, job_id):
        payload = build_job_request(0x0008, self.uri, self.user,
                                    job_id=job_id, which_jobs="")
        response = self._request(payload)
        return parse_response(response["body"])

    def _request(self, payload):
        try:
            response = self.client.request(
                self.path, method="POST", data=payload,
                headers={"Content-Type": "application/ipp"})
        except NetworkError as error:
            raise IppError(str(error)) from error
        if response["status"] != 200:
            raise IppError(f"IPP HTTP {response['status']}")
        return response

    def print_job(self, document, document_format="application/pdf",
                  job_name="AMFWX"):
        payload = build_print_job(self.uri, job_name, self.user,
                                  document_format, document)
        try:
            response = self.client.request(
                self.path, method="POST", data=payload,
                headers={"Content-Type": "application/ipp"})
        except NetworkError as error:
            raise IppError(str(error)) from error
        if response["status"] != 200:
            raise IppError(f"IPP HTTP {response['status']}")
        result = parse_response(response["body"])
        if result["status"] != 0:
            raise IppError(f"IPP-Status {result['status']:#06x}")
        return result

    def print_file(self, path, document_format=None, job_name=None):
        path = Path(path)
        if document_format is None:
            document_format = {
                ".pdf": "application/pdf",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".txt": "text/plain",
            }.get(path.suffix.lower(), "application/octet-stream")
        return self.print_job(path.read_bytes(), document_format,
                              job_name or path.name)
