# AMFWX 5.21.0

Camera live preview and UVC recording.

## New

- live preview in CameraWindow
- preview start/stop
- UVC video recording (`Webcam.record`)
- IP camera recording retained
- preview stops before snapshot/tether/record
- 404 tests

## Notes

No UVC camera was available for a live test. Preview and recording use the same
OpenCV capture path as snapshot.
