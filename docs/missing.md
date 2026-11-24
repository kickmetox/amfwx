# Was noch fehlt

Stand: AMFWX 5.3.0

## Scanner

| Punkt | Status |
|---|---|
| WIA | ✅ |
| TWAIN 64-bit Enumeration | ✅ |
| TWAIN 32-bit via eigener Python32-Brücke | ✅ real |
| Scanner-CLI fuer WIA/TWAIN32/NAPS2 | ✅ |
| TWAIN/WIA 32-bit via NAPS2 | ✅ Adapter, NAPS2 muss installiert sein |
| eSCL HTTP/HTTPS | ✅ |
| Kyocera ADF + Weck-Scan | ✅ real getestet |
| NAPS2 bündeln | ❌ GPL, nicht im MIT-Paket |
| echtes 32-bit-Treiberpaket bündeln | ❌ Treiber bleiben Herstellersache |

### NAPS2

```powershell
# NAPS2 installieren, dann:
python -c "from amfwx import naps2_available; print(naps2_available())"
```

Gesucht wird unter:

```text
PATH
Program Files\NAPS2
Program Files (x86)\NAPS2
%LOCALAPPDATA%\Programs\NAPS2
vendor\naps2
AMFWX_NAPS2
```

## Kameras

| Punkt | Status |
|---|---|
| PnP-Inventar | ✅ |
| UVC-Webcam | ✅ optional OpenCV |
| Kamera-Steuerung | ✅ soweit Treiber Eigenschaften anbietet |
| Tethering | ✅ UVC/GoPro/gPhoto2 |
| Chroma Key | ✅ |
| GoPro HTTP | ✅ |
| gPhoto2 DSLR | ✅ optional |
| MTP/PTP-Download | ✅ Shell-Adapter |
| Canon EDSDK | ❌ nicht gebündelt |
| Nikon SDK | ❌ |
| Sony Camera Remote SDK | ❌ |
| Fuji/Olympus/Leica native SDK | ❌ |
| DJI UVC | ⚠️ nur im Webcam-Modus |
| DJI MTP | ⚠️ nur wenn gemountet |

## Fernzugriff / IoT

| Punkt | Status |
|---|---|
| FRITZ!Box TR-064 | ✅ |
| Shelly | ✅ |
| Fibaro | ✅ |
| HomePilot | ✅ |
| Becker CC51 | ✅ |
| TaHoma | ✅ |
| Matter/Thread-Steuerung | ❌ nur Discovery |
| Tuya LAN 3.4/3.5 | ❌ nur 3.3 |
| Zigbee2MQTT | ✅ MQTT-Client |
| Jarolift-Discovery | ❌ |
| Becker Centronic USB | ❌ |

## Drucken

| Punkt | Status |
|---|---|
| Windows-Queue | ✅ |
| GDI-DIB | ✅ |
| Kyocera TCP/IP 9100 | ✅ real bestätigt |
| IPP | ❌ Gerät bietet keinen passenden Endpunkt |
| Duplex/Kopien | ❌ nicht in der CLI |

## Medien / Dokumente

| Punkt | Status |
|---|---|
| Scan → JPEG/PDF | ✅ |
| OCR | ✅ Windows.Media.Ocr |
| PDF-Textsuche | ✅ unsichtbarer OCR-Textlayer |
| PDF-Rendering zum Druck | ✅ PyMuPDF optional |

## Infrastruktur

| Punkt | Status |
|---|---|
| Tests | 389 |
| CI | grün |
| Code-Signatur | ❌ bewusst nicht |
| 32-Bit-Python | ✅ im App-/Portable-Paket |
| NAPS2 | optional, nicht gebündelt |

## Nächste sinnvolle Blöcke

1. NAPS2 portable freiwillig installieren und 32-Bit-TWAIN real testen
2. OCR über Tesseract optional anbinden
3. Matter/Thread-Commissioning
4. Tuya 3.4/3.5
5. echte Hardware für HomePilot/Becker/TaHoma
