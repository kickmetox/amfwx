"""Tuya LAN discovery for protocol 3.3–3.5."""

from __future__ import annotations

import hashlib
import json
import socket
import os
import struct

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:  # optional
    Cipher = None
    AESGCM = None

DISCOVERY_KEY = hashlib.md5(b"yGAdlopoPVldABfn").digest()
PREFIX_55AA = 0x000055AA
PREFIX_6699 = 0x00006699


class TuyaDiscoveryError(RuntimeError):
    pass


def _unpad(data):
    if data and 1 <= data[-1] <= 16:
        return data[:-data[-1]]
    return data


def _json_from(data):
    start, end = data.find(b"{"), data.rfind(b"}")
    if start < 0 or end < start:
        return None
    try:
        return json.loads(data[start:end + 1].decode("utf-8", "replace"))
    except ValueError:
        return None


def parse_packet(data, address=""):
    data = bytes(data)
    if data.startswith(struct.pack(">I", PREFIX_6699)):
        if AESGCM is None:
            raise TuyaDiscoveryError("cryptography fehlt")
        if len(data) < 18 + 12 + 16 + 4:
            return None
        header = data[:18]
        _reserved, _seq, _cmd, length = struct.unpack(">HIII", header[4:18])
        body = data[18:18 + length]
        if len(body) < 28:
            return None
        iv, tag, ciphertext = body[:12], body[-16:], body[12:-16]
        try:
            plain = AESGCM(DISCOVERY_KEY).decrypt(iv, ciphertext + tag,
                                                   header[4:])
        except Exception:
            return None
        if len(plain) >= 4 and plain[:4] == b"\x00\x00\x00\x00":
            plain = plain[4:]
        payload = _json_from(plain)
    elif data.startswith(struct.pack(">I", PREFIX_55AA)):
        _prefix, _seq, _cmd, length = struct.unpack(">IIII", data[:16])
        body = data[16:16 + max(0, length - 8)]
        payload = _json_from(body)
        if payload is None and Cipher is not None and body:
            try:
                cipher = Cipher(algorithms.AES(DISCOVERY_KEY), modes.ECB())
                worker = cipher.decryptor()
                plain = _unpad(worker.update(body) + worker.finalize())
                payload = _json_from(plain)
            except Exception:
                payload = None
    else:
        payload = _json_from(data)
    if not payload:
        return None
    return {
        "ip": address,
        "device_id": payload.get("gwId") or payload.get("devId") or "",
        "version": str(payload.get("ver", payload.get("version", ""))),
        "product": payload.get("productKey", ""),
        "raw": payload,
    }


def _request_6699(payload):
    if AESGCM is None:
        return b""
    iv = os.urandom(12)
    header = (struct.pack(">I", PREFIX_6699) + b"\x00\x00" +
              struct.pack(">III", 1, 0x25, 12 + len(payload) + 16))
    encrypted = AESGCM(DISCOVERY_KEY).encrypt(iv, payload, header[4:])
    return header + iv + encrypted + struct.pack(">I", 0x00009966)


def discover(timeout=2.0, broadcast="255.255.255.255"):
    found = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(float(timeout))
    try:
        sock.sendto(b"\x00" * 16, (broadcast, 6667))
        if AESGCM is not None:
            sock.sendto(_request_6699(b'{"from":"app","ip":"0.0.0.0"}'),
                        (broadcast, 7000))
        while True:
            try:
                data, address = sock.recvfrom(65535)
            except socket.timeout:
                break
            packet = parse_packet(data, address[0])
            if packet and packet["device_id"]:
                found.append(packet)
    finally:
        sock.close()
    return found
