# Medical data

AMFWX includes basic parsers for medical interoperability data. This is
**not** a medical device certification and not a full DICOM/HL7 stack.

## HL7 v2

```python
from amfwx import parse_hl7

segments = parse_hl7(message)
for segment in segments:
    print(segment["name"], segment["fields"])
```

## FHIR

```python
from amfwx import parse_fhir

resource = parse_fhir('{"resourceType":"Patient","id":"p1"}')
```

## DICOM

```python
from amfwx import parse_dicom

dicom = parse_dicom(open("image.dcm", "rb").read())
print(dicom.patient_name(), dicom.modality())
```

## Implemented

- HL7 v2 segment/field splitting
- FHIR JSON resource type/id
- DICOM Part 10 header
- explicit VR little endian elements
- patient name / modality helpers

## Not implemented

- HL7 ACK generation
- FHIR validation/profiles
- DICOM network services (C-STORE/C-FIND/C-MOVE)
- DICOM sequences/pixel data decoding
- DICOM implicit VR
- IEEE 11073
- medical device certification

## Device transports

Medical devices still connect through:

- serial/UART
- USB HID / WinUSB
- Bluetooth SPP/BLE
- TCP/UDP

Those transports are covered by the hardware modules.
