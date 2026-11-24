# AMFWX 5.36.0

MCP server entry point and LLM app tools.

## New

- `amfwx-mcp` console entry point
- `MCPServer` exposes AMFWX tools over stdio JSON-RPC
- app tools for LLMs:
  - `list_devices`
  - `scan_document`
  - `print_file`
  - `camera_snapshot`
- app tools are **disabled by default**
- `UiSession.allow_app_actions = True` enables them
- 422 tests

## Security

A language model must not be able to start a scan or print job silently.
App tools therefore require an explicit opt-in flag on the session.

## Usage

```powershell
amfwx-mcp
amfwx-sdk --tools
```
