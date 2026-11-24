from __future__ import annotations
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from amfwx import AppConfig, onvif_parse
from amfwx.onvif import probe_xml

XML = b'''<?xml version="1.0"?><Envelope xmlns="http://www.w3.org/2003/05/soap-envelope" xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery" xmlns:a="http://schemas.xmlsoap.org/ws/2004/08/addressing"><Body><ProbeMatches><ProbeMatch><d:XAddrs>http://192.168.1.20/onvif/device_service</d:XAddrs><d:Types>dn:NetworkVideoTransmitter</d:Types></ProbeMatch></ProbeMatches></Body></Envelope>'''

class OnvifTests(unittest.TestCase):
    def test_parse(self):
        data=onvif_parse(XML, '192.168.1.20')
        self.assertEqual(data['endpoints'][0], 'http://192.168.1.20/onvif/device_service')
    def test_cli_and_probe(self):
        self.assertIn(b'Probe', probe_xml().encode())
        self.assertEqual(AppConfig.parse(['--onvif-discover','2']).onvif_seconds,2.0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
