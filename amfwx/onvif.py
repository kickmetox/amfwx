"""ONVIF WS-Discovery for IP cameras."""

from __future__ import annotations

import re
import socket
import uuid
import xml.etree.ElementTree as ET

MULTICAST = "239.255.255.250"
PORT = 3702
NS = {
    "d": "http://schemas.xmlsoap.org/ws/2005/04/discovery",
    "a": "http://schemas.xmlsoap.org/ws/2004/08/addressing",
}

PROBE = """<?xml version="1.0" encoding="UTF-8"?>
<e:Envelope xmlns:e="http://www.w3.org/2003/05/soap-envelope"
 xmlns:w="http://schemas.xmlsoap.org/ws/2004/08/addressing"
 xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery"
 xmlns:dn="http://www.onvif.org/ver10/network/wsdl">
 <e:Header>
  <w:MessageID>uuid:{message_id}</w:MessageID>
  <w:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</w:To>
  <w:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</w:Action>
 </e:Header>
 <e:Body><d:Probe><d:Types>dn:NetworkVideoTransmitter</d:Types></d:Probe></e:Body>
</e:Envelope>"""


class OnvifError(RuntimeError):
    pass


def probe_xml(message_id=None):
    return PROBE.format(message_id=message_id or uuid.uuid4())


def parse_response(data, address=""):
    try:
        root = ET.fromstring(data)
    except ET.ParseError as error:
        raise OnvifError(f"ungueltige ONVIF-Antwort: {error}") from error
    endpoints = []
    for match in root.findall(".//d:XAddrs", NS):
        for value in re.split(r"\s+", match.text or ""):
            if value.startswith(("http://", "https://")):
                endpoints.append(value)
    types = [node.text or "" for node in root.findall(".//d:Types", NS)]
    scopes = [node.text or "" for node in root.findall(
        ".//d:Scopes", NS)]
    return {
        "address": address,
        "endpoints": sorted(set(endpoints)),
        "types": types,
        "scopes": scopes,
    }


def discover(timeout=3.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                         socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(float(timeout))
    results = []
    try:
        sock.sendto(probe_xml().encode("utf-8"), (MULTICAST, PORT))
        while True:
            try:
                data, address = sock.recvfrom(65535)
            except socket.timeout:
                break
            try:
                results.append(parse_response(data, address[0]))
            except OnvifError:
                continue
    finally:
        sock.close()
    return results
