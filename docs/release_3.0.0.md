# AMFWX 3.0.0

AMFWX 3.0 adds a unified SDK and local/online LLM integration.

## Highlights

- `create_sdk()` / `SDK`
- `UiSession` with LLM-callable UI tools
- `OllamaProvider`
- `OpenAICompatibleProvider` for LM Studio, llama.cpp, vLLM and OpenAI
- `LLMAgent` tool loop
- AMFW bridges available through the SDK
- no external Python dependencies for the AI layer
- 162 tests passing

## Assets

- `amfwx-3.0.0-py3-none-any.whl`
- `AMFWX-Portable-3.0.0.zip`
- `AMFWX-Own-Setup-3.0.0.exe` (unsigned)
- `SHA256SUMS.txt`

## Quick start

```python
from amfwx import create_sdk, OllamaProvider

sdk = create_sdk()
agent = sdk.agent(OllamaProvider(model="llama3.2"))
agent.run("Baue ein Fenster mit einem Button OK")
sdk.run()
```

## Notes

- Windows 10/11 x64
- local models stay local; online providers are opt-in
- no telemetry
- tool calling requires a model that supports it
- installer is unsigned; signing is the distributor's responsibility
- no cross-platform support
