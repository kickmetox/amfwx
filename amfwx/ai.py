"""LLM providers for local and online models.

No third-party dependency: HTTP via urllib, JSON via stdlib.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse


class AIError(RuntimeError):
    pass


class AIProvider:
    name = "provider"

    def __init__(self, model="", base_url="", timeout=120.0, api_key=None,
                 retries=0, backoff=0.5):
        self.model = str(model)
        self.base_url = str(base_url).rstrip("/")
        self.timeout = float(timeout)
        self.api_key = api_key if api_key is not None else self._env_key()
        self.retries = max(0, int(retries))
        self.backoff = max(0.0, float(backoff))
        parsed = urlparse(self.base_url)
        if parsed.scheme not in ("http", "https"):
            raise AIError(f"ungueltige Base-URL: {self.base_url!r}")

    def _env_key(self):
        return ""

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _request(self, path, payload=None, method="POST"):
        url = self.base_url + path
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=data, method=method,
                                         headers=self._headers())
        last_error = None
        for attempt in range(self.retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    raw = response.read(8 * 1024 * 1024)
                try:
                    return json.loads(raw.decode("utf-8"))
                except ValueError as error:
                    raise AIError(f"{self.name} lieferte kein JSON") from error
            except urllib.error.HTTPError as error:
                body = error.read(4096).decode("utf-8", "replace")
                last_error = AIError(f"{self.name} HTTP {error.code}: {body}")
                if error.code < 500 or attempt >= self.retries:
                    raise last_error from error
            except urllib.error.URLError as error:
                last_error = AIError(
                    f"{self.name} nicht erreichbar: {error.reason}")
                if attempt >= self.retries:
                    raise last_error from error
            time.sleep(self.backoff * (2 ** attempt))
        raise last_error or AIError(f"{self.name}: unbekannter Fehler")

    def _open_stream(self, path, payload):
        url = self.base_url + path
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=data, method="POST",
                                         headers=self._headers())
        try:
            return urllib.request.urlopen(request, timeout=self.timeout)
        except urllib.error.HTTPError as error:
            body = error.read(4096).decode("utf-8", "replace")
            raise AIError(f"{self.name} HTTP {error.code}: {body}") from error
        except urllib.error.URLError as error:
            raise AIError(f"{self.name} nicht erreichbar: {error.reason}") from error

    def list_models(self):
        raise NotImplementedError

    def chat(self, messages, tools=None, stream=False):
        raise NotImplementedError


def _normalize_ollama(data):
    message = data.get("message") or {}
    calls = []
    for call in message.get("tool_calls") or []:
        function = call.get("function") or {}
        arguments = function.get("arguments", {})
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except ValueError:
                arguments = {}
        calls.append({"id": call.get("id", ""),
                      "name": function.get("name", ""),
                      "arguments": arguments or {}})
    return {"content": message.get("content") or "",
            "tool_calls": calls, "raw": data}


class OllamaProvider(AIProvider):
    """Local Ollama server (default http://127.0.0.1:11434)."""

    name = "ollama"

    def __init__(self, model="llama3.2", base_url="http://127.0.0.1:11434",
                 timeout=120.0, api_key=None, retries=0, backoff=0.5):
        super().__init__(model, base_url, timeout, api_key, retries, backoff)

    def list_models(self):
        data = self._request("/api/tags", method="GET")
        return [item.get("name", "") for item in data.get("models", [])]

    def chat(self, messages, tools=None, stream=False):
        payload = {"model": self.model, "messages": messages,
                   "stream": False}
        if tools:
            payload["tools"] = tools
        data = self._request("/api/chat", payload)
        return _normalize_ollama(data)

    def stream_chat(self, messages, tools=None):
        payload = {"model": self.model, "messages": messages,
                   "stream": True}
        if tools:
            payload["tools"] = tools
        response = self._open_stream("/api/chat", payload)
        try:
            for raw in response:
                line = raw.decode("utf-8", "replace").strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except ValueError:
                    continue
                message = data.get("message") or {}
                calls = message.get("tool_calls") or []
                if message.get("content") or calls:
                    yield {"content": message.get("content") or "",
                           "tool_calls": calls, "raw": data}
                if data.get("done"):
                    break
        finally:
            response.close()

    def pull(self, model=None):
        return self._request("/api/pull", {"name": model or self.model,
                                           "stream": False})

    def delete(self, model=None):
        return self._request("/api/delete", {"name": model or self.model})


def _normalize_openai(data):
    choice = (data.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    calls = []
    for call in message.get("tool_calls") or []:
        function = call.get("function") or {}
        arguments = function.get("arguments", {})
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except ValueError:
                arguments = {}
        calls.append({"id": call.get("id", ""),
                      "name": function.get("name", ""),
                      "arguments": arguments or {}})
    return {"content": message.get("content") or "",
            "tool_calls": calls, "raw": data}


class OpenAICompatibleProvider(AIProvider):
    """OpenAI-compatible endpoint (OpenAI, LM Studio, llama.cpp, vLLM)."""

    name = "openai-compatible"

    def __init__(self, model="gpt-4o-mini",
                 base_url="http://127.0.0.1:1234/v1", timeout=120.0,
                 api_key=None, retries=0, backoff=0.5):
        super().__init__(model, base_url, timeout, api_key, retries, backoff)

    def _env_key(self):
        return os.environ.get("OPENAI_API_KEY", "")

    def list_models(self):
        data = self._request("/models", method="GET")
        return [item.get("id", "") for item in data.get("data", [])]

    def _vision_messages(self, messages):
        result = []
        for message in messages:
            images = message.get("images") or []
            if images:
                content = message.get("content", "")
                blocks = [{"type": "text", "text": str(content)}]
                for image in images:
                    if not str(image).startswith("data:"):
                        image = "data:image/png;base64," + str(image)
                    blocks.append({"type": "image_url",
                                   "image_url": {"url": str(image)}})
                result.append({"role": message.get("role", "user"),
                               "content": blocks})
            else:
                result.append(message)
        return result

    def chat(self, messages, tools=None, stream=False):
        payload = {"model": self.model,
                   "messages": self._vision_messages(messages),
                   "stream": False}
        if tools:
            payload["tools"] = tools
        data = self._request("/chat/completions", payload)
        return _normalize_openai(data)

    def stream_chat(self, messages, tools=None):
        payload = {"model": self.model, "messages": messages,
                   "stream": True}
        if tools:
            payload["tools"] = tools
        response = self._open_stream("/chat/completions", payload)
        try:
            for raw in response:
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                data_text = line[5:].strip()
                if data_text == "[DONE]":
                    break
                try:
                    data = json.loads(data_text)
                except ValueError:
                    continue
                choice = (data.get("choices") or [{}])[0]
                delta = choice.get("delta") or {}
                if delta.get("content"):
                    yield {"content": delta["content"],
                           "tool_calls": [], "raw": data}
        finally:
            response.close()


class EchoProvider(AIProvider):
    """Deterministic offline provider for tests and demos."""

    name = "echo"

    def __init__(self, model="echo", base_url="http://127.0.0.1:9",
                 timeout=1.0, api_key=None):
        super().__init__(model, base_url, timeout, api_key)

    def list_models(self):
        return [self.model]

    def chat(self, messages, tools=None, stream=False):
        last = messages[-1].get("content", "") if messages else ""
        return {"content": f"echo: {last}", "tool_calls": [], "raw": {}}


def provider_from_name(name, **kwargs):
    key = str(name).lower()
    if key == "ollama":
        return OllamaProvider(**kwargs)
    if key in ("openai", "lmstudio", "llama.cpp", "vllm"):
        defaults = {}
        if key == "lmstudio":
            defaults["base_url"] = "http://127.0.0.1:1234/v1"
        return OpenAICompatibleProvider(**{**defaults, **kwargs})
    if key == "echo":
        return EchoProvider(**kwargs)
    raise AIError(f"unbekannter Provider: {name}")
