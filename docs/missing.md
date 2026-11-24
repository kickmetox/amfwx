# Was noch fehlt

Stand: AMFWX 5.20.0

## Scanner

| Punkt | Status |
|---|---|
| WIA | ✅ |
| TWAIN 64-bit Enumeration | ✅ |
| TWAIN 32-bit Python-Brücke | ✅ real am Canon |
| Scanner-CLI WIA/TWAIN32/NAPS2 | ✅ |
| Scanner-Fenster WIA/TWAIN32/NAPS2 | ✅ |
| NAPS2-Adapter + ADF-Batch | ✅ |
| eSCL HTTP/HTTPS | ✅ |
| Kyocera ADF + Weck-Scan | ✅ real |
| NAPS2 installiert/getestet | ❌ nicht installiert |
| NAPS2 bündeln | ❌ GPL |
| Treiberpakete bündeln | ❌ Herstellersache |
| WIA/TWAIN32-Mehrseiten im Treiber | ⚠️ treiberabhängig |
| Scan-Profile/Deskew/Crop | ❌ |

## Kameras

| Punkt | Status |
|---|---|
| PnP-Inventar | ✅ |
| UVC/Webcam | ✅ optional OpenCV |
| ONVIF/WS-Discovery | ✅ |
| RTSP/HTTP | ✅ |
| Snapshot | ✅ |
| IP-Videoaufnahme | ✅ |
| UVC-Videoaufnahme | ❌ |
| Live-Vorschau im Fenster | ❌ |
| Kamera-Steuerung | ⚠️ nur API/Treiber |
| Tethering | ✅ UVC/IP/GoPro/gPhoto2 |
| Chroma Key | ✅ |
| GoPro HTTP | ⚠️ Status/Foto, kein Medien-Download |
| gPhoto2-DSLR | ⚠️ CLI-Adapter, keine Live-View |
| MTP/PTP-Download | ✅ |
| Canon EDSDK | ❌ |
| Nikon SDK | ❌ |
| Sony Camera Remote SDK | ❌ |
| Fuji/Olympus/Leica native SDK | ❌ |
| DJI UVC | ⚠️ nur Webcam-Modus |
| DJI MTP | ⚠️ nur gemountet |
| DJI native Steuerung | ❌ |

## IoT / Fernzugriff

| Punkt | Status |
|---|---|
| FRITZ!Box TR-064 | ✅ |
| Shelly | ✅ |
| Fibaro | ✅ |
| HomePilot | ✅ |
| Becker CC51 | ✅ |
| TaHoma | ✅ |
| Tuya LAN 3.3/3.4/3.5 | ✅ |
| Zigbee2MQTT | ✅ |
| Matter über chip-tool | ✅ optional |
| Becker Centronic USB | ✅ Protokoll |
| Jarolift/Becker RF-Discovery | ✅ optional rtl_433 |
| Jarolift-Steuerung | ❌ |
| Becker-Rückkanal | ❌ |
| Matter ohne chip-tool | ❌ |
| Thread-Border-Router | ❌ |
| Tuya-Geräte-Onboarding | ⚠️ Local Key nötig |
| MQTT TLS | ❌ |
| echte Hardwaretests | ❌ |

## Drucken

| Punkt | Status |
|---|---|
| Windows-Queue | ✅ |
| GDI-DIB | ✅ |
| Kyocera TCP/IP 9100 | ✅ real |
| Kopien/Duplex (Windows) | ✅ DEVMODE |
| IPP Print-Job | ✅ Client |
| IPP Kopien/Duplex | ✅ |
| Kyocera-IPP-Endpunkt | ❌ Gerät bietet keinen |
| Papierformat/Orientierung | ❌ CLI |
| Finishing/Stapling | ❌ |
| IPP Digest/TLS-Auth | ⚠️ Basic/TLS |

## Dokumente

| Punkt | Status |
|---|---|
| Scan → JPEG/PDF | ✅ |
| OCR | ✅ Windows.Media.Ocr |
| Durchsuchbares PDF | ✅ real |
| Scan → OCR | ✅ real |
| OCR im Scan-Fenster | ✅ |
| OCR-Sprachpakete | ⚠️ Systemabhängig |
| PDF zusammenführen/teilen | ❌ |
| PDF-Text extrahieren als Datei | ⚠️ CLI-Ausgabe |
| Tesseract | ❌ nicht gebündelt |

## Infrastruktur

| Punkt | Status |
|---|---|
| Tests | 404 |
| CI | grün |
| 32-Bit-Python im Release | ✅ |
| 32-Bit-Python im CI-Artefakt | ❌ gitignored |
| NAPS2 | optional |
| Code-Signatur | ❌ bewusst |
| Auto-Update | ❌ |
| Einheitliches Geräte-Dashboard | ❌ |
| Persistente Einstellungen | ⚠️ teilweise |

## Die größten echten Lücken

1. **Hardware-Verifikation**: Tuya 3.4/3.5, Matter, Becker und Jarolift sind nur gegen Fakes/Adapter getestet.
2. **Vendor-SDKs**: Canon EDSDK, Nikon SDK, Sony Camera Remote SDK, Fuji/Olympus/Leica fehlen.
3. **DJI**: keine native Steuerung, nur MTP/UVC.
4. **Kamera-Livebild**: kein Preview im Kamera-Fenster.
5. **NAPS2**: nicht installiert, daher kein echter 32-Bit-NAPS2-Test.
6. **IPP**: Kyocera stellt keinen nutzbaren IPP-Endpunkt bereit.
7. **Matter**: nur mit externem chip-tool.
8. **Jarolift**: Discovery, aber keine Steuerung.

## Nächste sinnvolle Reihenfolge

1. Kamera-Livevorschau und UVC-Videoaufnahme
2. GoPro-Medien-Download
3. PDF merge/split
4. NAPS2 installieren und real testen
5. Matter/Thread mit echter Hardware
6. Tuya 3.4/3.5 mit echtem Gerät
7. echte Becker/Jarolift-Hardware
