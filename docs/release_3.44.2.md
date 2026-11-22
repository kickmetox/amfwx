# AMFWX 3.44.2

TWAIN ABI fix.

## Fix

- `DSM_Entry` passes `DAT`/`MSG` as 16-bit
- TWAIN structs use `pack(2)`
- DSM is opened before enumeration
- 261 tests

## Status

TWAIN sources are still not registered on this machine. TWAIN image
transfer remains unimplemented.
