# AMFWX 3.98.1

Clear ADF-empty error.

## Fix

- feeder 409/500/503 -> "Einzug ist leer oder noch nicht bereit"
- real Kyocera reports `ScannerAdfEmpty`, so the 409 was expected
- 354 tests
