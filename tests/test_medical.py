"""Medical data parser tests."""

from __future__ import annotations

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import MedicalError, parse_dicom, parse_fhir, parse_hl7


def dicom_bytes():
    data = bytearray(b"\x00" * 128 + b"DICM")

    def element(group, element_id, vr, value):
        return (struct.pack("<HH", group, element_id) + vr.encode("ascii") +
                struct.pack("<H", len(value)) + value)

    data.extend(element(0x0010, 0x0010, "PN", b"Test^Patient"))
    data.extend(element(0x0008, 0x0060, "CS", b"CT"))
    return bytes(data)


class MedicalTests(unittest.TestCase):
    def test_hl7(self):
        segments = parse_hl7(
            "MSH|^~\\&|A|B|C|D|2020||ADT^A01|1|P|2.3\r"
            "PID|1||123")
        self.assertEqual(segments[0]["name"], "MSH")
        self.assertEqual(segments[1]["name"], "PID")
        self.assertEqual(segments[1]["fields"][2], "123")

    def test_fhir(self):
        resource = parse_fhir('{"resourceType":"Patient","id":"p1"}')
        self.assertEqual(resource["resourceType"], "Patient")
        self.assertEqual(resource["id"], "p1")
        with self.assertRaises(MedicalError):
            parse_fhir('{"id":"x"}')

    def test_dicom(self):
        dicom = parse_dicom(dicom_bytes())
        self.assertEqual(dicom.patient_name(), "Test^Patient")
        self.assertEqual(dicom.modality(), "CT")
        with self.assertRaises(MedicalError):
            parse_dicom(b"not dicom")


if __name__ == "__main__":
    unittest.main(verbosity=2)
