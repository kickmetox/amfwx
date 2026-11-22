# MCP

AMFWX can expose its UI tools as an MCP server and connect to MCP servers.

## Server

```powershell
python -m amfwx.mcp
```

The server speaks JSON-RPC over stdio and exposes:

- `create_window`
- `add_widget`
- `set_widget_text`
- `click`
- `list_widgets`
- `snapshot`
- `snapshot_base64`

## Client

```python
from amfwx import MCPClient

client = MCPClient(["python", "-m", "amfwx.mcp"])
client.initialize()
print(client.list_tools())
client.call_tool("create_window", {"title": "MCP"})
client.close()
```

## Protocol

- MCP initialize
- `tools/list`
- `tools/call`
- JSON-RPC 2.0 over stdio

## Limits

- stdio transport only
- no resources/prompts
- no authentication
- no SSE/HTTP transport
- single session per process
