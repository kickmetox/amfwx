# AMFWX 3.98.0

Kyocera eSCL verified against real hardware.

## Fix

- eSCL HTTP port 9095 added
- self-signed HTTPS 9096 now works (`verify_tls=False`)
- subnet scan includes 9095/9096

## Hardware result

Kyocera ECOSYS M5521cdn at `192.168.178.93`:

- platen + ADF
- resolutions 200/100/400/300/600
- color: BlackAndWhite1, Grayscale8, RGB24
- real scan: 1654x2337 JPEG, 217958 bytes

The scanned document was deleted after verification because it contained
personal data.

## Tests

353 tests.
