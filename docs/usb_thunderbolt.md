# USB 3.x and Thunderbolt

## Reality

USB 3.2, USB4 and Thunderbolt are **transport layers**. An application does
not open "USB 3.2"; it opens a device class:

- HID
- WinUSB
- CDC/serial
- mass storage
- audio/video
- PCIe tunnel (Thunderbolt)

Backward compatibility is handled by the OS, hub, cable and device. The
application sees the device, not the generation.

## AMFWX support

| Device class | AMFWX API |
|---|---|
| USB serial/CDC | `amfwx.io.SerialPort` |
| USB HID | `amfwx.usb` |
| Raw WinUSB | `amfwx.usb_raw` |
| USB storage | not included (use OS file API) |
| USB audio/video | not included |
| Thunderbolt PCIe | not included |
| Thunderbolt USB devices | via the USB class above |

## Thunderbolt

Thunderbolt devices appear as PCIe or USB devices. There is no separate
"Thunderbolt API" for normal applications. PCIe tunnel devices need their
own driver/vendor SDK.

## Scanners

Scanners are usually WIA or TWAIN devices, not raw USB:

- WIA (Windows Image Acquisition)
- TWAIN data source
- vendor SDK

AMFWX does not implement WIA/TWAIN yet. A scanner may still appear as a
USB device, but its scan protocol is vendor-specific.

## Medical devices

Device transports are usually:

- USB HID
- USB serial/CDC
- Bluetooth SPP/BLE
- Ethernet/WLAN

Data standards are separate:

- HL7 v2
- FHIR
- DICOM
- IEEE 11073

See [Medical data](medical.md).

## Limits

- no USB audio/video class
- no Thunderbolt PCIe API
- no WIA/TWAIN
- no vendor scanner SDK
- no medical device certification
