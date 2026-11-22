# AMFWX 3.40.0

AMFWX 3.40 adds basic medical data interoperability and documents
USB/Thunderbolt/scanner boundaries.

## New

- `parse_hl7`
- `parse_fhir`
- `parse_dicom`
- `DicomFile`
- 255 tests

## Notes

- HL7 is segment/field parsing only
- FHIR is JSON resource parsing only
- DICOM is Part 10 header parsing only
- no WIA/TWAIN scanner API
- no Thunderbolt PCIe API
- Windows-only
- unsigned installer
