from __future__ import annotations
import json, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from amfwx import AppConfig, JaroliftController

class Fake:
    def __init__(self,*a,**k): self.published=[]; self.message=None
    def connect(self): return self
    def publish(self,topic,payload,retain=False): self.published.append((topic,payload)); return True
    def subscribe(self,topic): return True
    def read_message(self,timeout=None):
        message,self.message=self.message,None; return message
    def close(self): pass

class JaroliftTests(unittest.TestCase):
    def test_commands(self):
        fake=Fake()
        controller=JaroliftController('localhost', client_factory=lambda *a,**k: fake)
        controller.up(3)
        controller.position(3, 45)
        self.assertEqual(fake.published[0][0], 'ESP32-Jarolift-Controller/cmd/shutter/3')
        self.assertEqual(fake.published[0][1], 'UP')
        self.assertEqual(fake.published[1][0], 'ESP32-Jarolift-Controller/cmd/position/3')
    def test_cli(self):
        config=AppConfig.parse(['--jarolift-host','x','--jarolift-action','UP'])
        self.assertEqual(config.jarolift_action,'UP')

if __name__ == '__main__':
    unittest.main(verbosity=2)
