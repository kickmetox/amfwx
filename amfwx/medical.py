"""Basic medical/healthcare data interoperability helpers."""

from __future__ import annotations

import json
import struct


class MedicalError(ValueError):
    pass


def parse_hl7(message):
    text = str(message).replace("\r\n", "\r").replace("\n", "\r")
    segments = []
    for raw in text.split("\r"):
        if not raw:
            continue
        fields = raw.split("|")
        segments.append({"name": fields[0], "fields": fields[1:]})
    return segments


def parse_fhir(value):
    data = value if isinstance(value, dict) else json.loads(str(value))
    resource_type = data.get("resourceType", "")
    if not resource_type:
        raise MedicalError("FHIR resourceType fehlt")
    return {"resourceType": resource_type, "id": data.get("id", ""),
            "data": data}


class DicomFile:
    def __init__(self, elements=None):
        self.elements = dict(elements or {})

    def get(self, tag, default=None):
        return self.elements.get(tag, default)

    def patient_name(self):
        return self.get("0010,0010", "")

    def modality(self):
        return self.get("0008,0060", "")


def parse_dicom(data):
    data = bytes(data)
    if len(data) < 132 or data[128:132] != b"DICM":
        raise MedicalError("kein DICOM-Part-10-Header")
    offset = 132
    elements = {}
    explicit = True
    while offset + 8 <= len(data):
        group, element = struct.unpack("<HH", data[offset:offset + 4])
        offset += 4
        tag = f"{group:04X},{element:04X}"
        if explicit:
            vr = data[offset:offset + 2].decode("ascii", "replace")
            offset += 2
            if vr in ("OB", "OW", "OF", "SQ", "UT", "UN"):
                if offset + 6 > len(data):
                    break
                _reserved = data[offset:offset + 2]
                length = struct.unpack("<I", data[offset + 2:offset + 6])[0]
                offset += 6
            else:
                length = struct.unpack("<H", data[offset:offset + 2])[0]
                offset += 2
        else:
            length = struct.unpack("<I", data[offset:offset + 4])[0]
            offset += 4
            vr = ""
        if length == 0xFFFFFFFF:
            break
        value = data[offset:offset + length]
        offset += length
        if vr in ("PN", "LO", "SH", "CS", "DA", "TM", "UI", "ST", "LT"):
            text = value.decode("utf-8", "replace").rstrip("\x00 ")
            elements[tag] = text
        else:
            elements[tag] = value
    return DicomFile(elements)
