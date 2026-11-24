# AMFWX 5.37.0

Agent streaming and cancellation.

## New

- `LLMAgent.run_stream`
- `LLMAgent.cancel`
- streaming through `provider.stream_chat`
- 423 tests

## Usage

```python
agent = sdk.agent(provider)
for chunk in agent.run_stream("Baue ein Fenster."):
    print(chunk, end="", flush=True)
```

`run_stream` yields content chunks. Tool calls are not executed in streaming
mode; use `run()` for tool execution.

```python
agent.cancel()
```
