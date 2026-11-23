"""Becker CentralControl CC31/CC41/CC51 JSON-RPC client."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

RPC_PATH = "/cgi-bin/cc51rpc.cgi"

LIST_METHOD = "deviced.deviced_get_item_list"
COMMAND_METHOD = "deviced.group_send_command"
GROUP_STATE_METHOD = "deviced.group_get_state"
ITEM_STATE_METHOD = "deviced.item_get_state"

COVER_TYPES = {"shutter", "venetian", "screen", "awning", "sun-sail",
               "shutter-blinds", "shutter-foldout"}
REVERSED_TYPES = {"awning"}


class BeckerError(RuntimeError):
    pass


class BeckerCentral:
    def __init__(self, host, port=80, timeout=5.0):
        self.host = str(host)
        self.port = int(port)
        self.timeout = float(timeout)
        self._id = 0

    def _rpc(self, method, params=None):
        self._id += 1
        payload = json.dumps({"jsonrpc": "2.0", "id": self._id,
                              "method": method,
                              "params": params or {}}) + "\0"
        request = urllib.request.Request(
            f"http://{self.host}:{self.port}{RPC_PATH}",
            data=payload.encode("utf-8"), method="POST",
            headers={"Content-Type": "text/plain",
                     "Accept": "application/json",
                     "Connection": "close"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read()
        except urllib.error.HTTPError as error:
            raise BeckerError(f"HTTP {error.code}") from error
        except OSError as error:
            raise BeckerError(str(error)) from error
        text = body.decode("utf-8", "replace").rstrip("\0").strip()
        try:
            data = json.loads(text)
        except ValueError as error:
            raise BeckerError("ungueltige JSON-RPC-Antwort") from error
        if data.get("error") is not None:
            raise BeckerError(str(data["error"]))
        if "result" not in data:
            raise BeckerError("Antwort ohne result")
        return data["result"]

    def groups(self):
        result = self._rpc(LIST_METHOD, {"item_type": "group"})
        return [item for item in result.get("item_list", [])
                if item.get("device_type") in COVER_TYPES]

    def remotes(self):
        result = self._rpc(LIST_METHOD, {"item_type": "remote"})
        return result.get("item_list", [])

    def sensors(self):
        result = []
        for remote in self.remotes():
            try:
                state = self.item_state(remote.get("id"))
            except BeckerError:
                state = {}
            values = {key[6:]: value for key, value in state.items()
                      if key.startswith("value-")}
            result.append({"id": remote.get("id"),
                           "name": remote.get("name", ""),
                           "type": remote.get("remote_type", ""),
                           "values": values})
        return result

    def group_state(self, group_id):
        return self._rpc(GROUP_STATE_METHOD,
                         {"group_id": int(group_id)}).get("state", {})

    def item_state(self, item_id):
        return self._rpc(ITEM_STATE_METHOD,
                         {"item_id": int(item_id)}).get("state", {})

    def _move(self, group_id, value):
        return self._rpc(COMMAND_METHOD, {
            "group_id": int(group_id), "command": "move",
            "value": int(value)})

    def open_cover(self, group_id, device_type="shutter"):
        return self._move(group_id, 1 if device_type in REVERSED_TYPES else -1)

    def close_cover(self, group_id, device_type="shutter"):
        return self._move(group_id, -1 if device_type in REVERSED_TYPES else 1)

    def stop_cover(self, group_id):
        return self._move(group_id, 0)

    def set_position(self, group_id, position, device_type="shutter"):
        position = max(0, min(100, int(position)))
        value = position if device_type in REVERSED_TYPES else 100 - position
        return self._rpc(COMMAND_METHOD, {
            "group_id": int(group_id), "command": "moveto",
            "value": value})
