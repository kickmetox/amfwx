# AMFWX 3.80.0

Native Becker CentralControl CC31/CC41/CC51 client.

## New

- `BeckerCentral`
- JSON-RPC endpoint `/cgi-bin/cc51rpc.cgi`
- group list, remote list
- group/remote state
- open/close/stop/position
- awning direction reversal
- registry adapter
- 331 tests

## Protocol

- `deviced.deviced_get_item_list`
- `deviced.group_send_command`
- `deviced.group_get_state`
- `deviced.item_get_state`

## Notes

Protocol details follow the open-source Gladys Becker integration and Becker's
reference behavior. Not tested against real CC hardware here.
