# AMFWX 5.39.0

Provider plugins.

## New

- `register_provider`
- `unregister_provider`
- `list_providers`
- `load_provider_plugins`
- `SDK.register_provider`
- Python entry point group `amfwx.providers`
- 426 tests

## Usage

```python
from amfwx import register_provider

register_provider("my-llm", MyProvider)
provider = sdk.provider("my-llm", model="...")
```

External packages can register a provider through `amfwx.providers`.

## Security

Provider plugins run in-process and are trusted Python code.
