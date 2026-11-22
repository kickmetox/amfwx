# AMFWX SDK and LLM integration

AMFWX 3.0 includes a unified SDK for:

- UI sessions
- AMFW bridges
- LLM providers (Ollama, OpenAI-compatible)
- LLM-callable UI tools

No external Python package is required. HTTP uses `urllib`.

## Quick start

```python
from amfwx import create_sdk, OllamaProvider

sdk = create_sdk()
provider = OllamaProvider(model="llama3.2")
agent = sdk.agent(provider)
print(agent.run("Baue ein Fenster mit einem Button 'OK'."))
sdk.run()
```

## Ollama

```powershell
ollama serve
ollama pull llama3.2
```

```python
from amfwx import OllamaProvider
provider = OllamaProvider(model="llama3.2",
                          base_url="http://127.0.0.1:11434")
print(provider.list_models())
```

Ollama must support tool calling for the agent loop. If it does not, use
`EchoProvider` for a deterministic demo or call `sdk.call_tool()` directly.

## OpenAI-compatible endpoints

Works with OpenAI, LM Studio, llama.cpp server, vLLM and similar:

```python
from amfwx import OpenAICompatibleProvider

# LM Studio / llama.cpp local
provider = OpenAICompatibleProvider(
    model="local-model",
    base_url="http://127.0.0.1:1234/v1",
)

# Online OpenAI-compatible
provider = OpenAICompatibleProvider(
    model="gpt-4o-mini",
    base_url="https://api.openai.com/v1",
)
```

`OPENAI_API_KEY` is read from the environment if no key is passed.

## Direct tool use

```python
sdk = create_sdk()
sdk.call_tool("create_window", {"title": "Demo"})
sdk.call_tool("add_widget", {"kind": "label", "text": "Hallo"})
sdk.call_tool("add_widget", {"kind": "button", "text": "OK"})
sdk.snapshot("demo.png")
sdk.run()
```

Available tools:

| Tool | Purpose |
|---|---|
| `create_window` | create/replace window |
| `add_widget` | label, button, line_edit, text_edit, checkbox, slider, combo |
| `set_widget_text` | change text |
| `click` | activate/toggle |
| `list_widgets` | ids, kinds, geometry |
| `snapshot` | PNG file |
| `snapshot_base64` | PNG as base64 |

## Offline behavior

- Ollama and local OpenAI-compatible servers need only localhost.
- No telemetry, no cloud calls unless configured.
- Online providers are opt-in.
- API keys are read from environment or passed explicitly.
- The SDK never writes keys to disk.

## Bridges

```python
sdk.amfwx_view(amfwx_root)       # AMFWX inside AMFW
sdk.amfw_host(amfw_window)       # AMFW inside AMFWX
```

AMFW must be importable for these calls. AMFW is not a hard dependency.

## Streaming

```python
for chunk in provider.stream_chat(messages):
    print(chunk["content"], end="", flush=True)
```

## Persistence and keys

```python
from amfwx import Conversation, KeyStore
conversation = Conversation()
conversation.save("chat.json")
conversation = Conversation.load("chat.json")

keys = KeyStore()
keys.save("openai", "...")
keys.load("openai")
```

`KeyStore` uses Windows DPAPI and stores only encrypted files.

## Vision

```python
agent.run("Beschreibe das Bild", image="shot.png")
```

`amfwx.vision` provides `image_base64`, `image_data_url` and
`vision_message`.

## Limits

- vision via Ollama `images` and OpenAI `image_url` blocks
- tool calling depends on the model
- no automatic retry/backoff
- no conversation persistence
- UI created by the model still needs human review

## Package

All of this ships in the `amfwx` wheel. AMFW remains optional for the
bridges, so there is one SDK package and no second runtime.
