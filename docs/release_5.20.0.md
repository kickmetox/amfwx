# AMFWX 5.20.0

IP/RTSP cameras and ONVIF discovery.

## New

- `IpCamera`
- RTSP/HTTP capture
- snapshot
- MJPEG AVI recording
- ONVIF WS-Discovery
- `--onvif-discover`
- `--ip-camera`
- `--ip-snapshot`
- `--ip-record`
- CameraWindow URL field
- 404 tests

## Camera coverage

| Type | Support |
|---|---|
| UVC webcam | OpenCV |
| ONVIF/RTSP | OpenCV |
| GoPro | HTTP |
| DSLR | gPhoto2 optional |
| DJI | PnP/MTP/UVC |
| Chroma key | yes |
| Tethering | yes |

## Limits

No ONVIF camera or RTSP stream was available for a live test. XML parsing and
command construction are tested.
