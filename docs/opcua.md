# OPC UA (optional)

The OPC UA binary stack is **not** reimplemented in AMFWX.

If the optional `asyncua` package is installed:

```powershell
pip install asyncua
```

```python
from amfwx import OpcUaClient

with OpcUaClient("opc.tcp://192.168.1.20:4840") as client:
    value = client.read("ns=2;i=2")
    client.write("ns=2;i=2", 42)
    children = client.browse("ns=2;i=1")
```

Without `asyncua`, `OpcUaError` is raised with an install hint.

## Why optional

OPC UA needs:

- secure channel handshake
- session/authentication
- certificates
- chunking
- service encoding
- subscription/monitoring

That is a separate protocol stack, not a small wrapper.

## FireWire

FireWire/IEEE 1394 is not supported. Modern Windows no longer ships a
general FireWire stack, and camera/industrial devices need vendor SDKs.

## Limits

- optional dependency
- no bundled OPC UA stack
- no FireWire
