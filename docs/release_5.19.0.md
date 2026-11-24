# AMFWX 5.19.0

Windows print copies and duplex.

## New

- DEVMODE from `GetPrinter` level 2
- `dmCopies`
- `dmDuplex`
- `--copies` and `--duplex` now apply to Windows PDF printing as well as IPP
- 402 tests

## Notes

No paper test with two copies/duplex was performed. The DEVMODE values are read
back and tested against the installed Kyocera queue.
