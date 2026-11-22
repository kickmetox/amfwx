"""Serial framing, Modbus and socket tests."""

from __future__ import annotations

import socket
import struct
import threading
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.io import (FrameDecoder, ModbusTCP, SerialError, SerialPort,
                      TcpClient, cobs_decode, cobs_encode, list_ports)


class FramingTests(unittest.TestCase):
    def test_cobs_roundtrip(self):
        data = b"hello\x00world\x00"
        self.assertEqual(cobs_decode(cobs_encode(data)), data)

    def test_delimiter_frames(self):
        decoder = FrameDecoder(b"\n")
        self.assertEqual(decoder.feed(b"a\nb"), [b"a"])
        self.assertEqual(decoder.feed(b"c\n"), [b"bc"])

    def test_serial_list(self):
        self.assertIsInstance(list_ports(), list)
        with self.assertRaises(SerialError):
            SerialPort("COM999", timeout=0.1).open()


class ModbusTests(unittest.TestCase):
    def test_read_registers(self):
        server = socket.socket()
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]

        def serve():
            connection, _address = server.accept()
            request = connection.recv(12)
            _tid, _pid, _length, _unit, function, _addr, count = struct.unpack(
                ">HHHBBHH", request)
            payload = struct.pack(">BBHH", 3, count * 2, 0x1234, 0x5678)
            connection.sendall(struct.pack(">HHHB", 1, 0, len(payload) + 1, 1)
                               + payload)
            connection.close()
            server.close()

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        client = ModbusTCP("127.0.0.1", port)
        self.assertEqual(client.read_holding_registers(0, 2),
                         [0x1234, 0x5678])
        thread.join(timeout=2)


class SocketTests(unittest.TestCase):
    def test_tcp_echo(self):
        server = socket.socket()
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]

        def serve():
            connection, _address = server.accept()
            data = connection.recv(100)
            connection.sendall(data)
            connection.close()
            server.close()

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        with TcpClient("127.0.0.1", port) as client:
            client.send(b"ping")
            self.assertEqual(client.recv(4), b"ping")
        thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
