from __future__ import annotations
import hashlib, json, os, struct, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from amfwx import AppConfig, tuya_discovery_parse

class TuyaDiscoveryTests(unittest.TestCase):
    def test_plain_55aa(self):
        body=json.dumps({'gwId':'abc123','ver':'3.3'}).encode()
        data=struct.pack('>IIII',0x000055AA,1,0,16+len(body)) + body
        result=tuya_discovery_parse(data,'192.168.1.5')
        self.assertEqual(result['device_id'],'abc123')
    def test_gcm_6699(self):
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            self.skipTest('cryptography fehlt')
        key=hashlib.md5(b'yGAdlopoPVldABfn').digest()
        plain=json.dumps({'gwId':'gcm1','ver':'3.5'}).encode()
        iv=os.urandom(12); header=struct.pack('>I',0x00006699)+b'\x00\x00'+struct.pack('>III',1,0x25,12+len(plain)+16)
        data=header+iv+AESGCM(key).encrypt(iv,plain,header[4:])+struct.pack('>I',0x00009966)
        result=tuya_discovery_parse(data,'192.168.1.6')
        self.assertEqual(result['device_id'],'gcm1')
    def test_cli(self):
        self.assertEqual(AppConfig.parse(['--tuya-discover','2']).tuya_discover, 2.0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
