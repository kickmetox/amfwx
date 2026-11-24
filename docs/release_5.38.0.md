# AMFWX 5.38.0

Async SDK entry points.

## New

- `AIProvider.async_chat`
- `LLMAgent.async_run`
- 425 tests

## Usage

```python
import asyncio

result = await provider.async_chat(messages, tools=TOOL_SPECS)
answer = await agent.async_run("Baue ein Fenster.")
```

Both use `asyncio.to_thread` around the existing synchronous HTTP/tool path, so
no third-party asyncio HTTP dependency is required.
