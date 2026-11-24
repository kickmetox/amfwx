from __future__ import annotations
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from amfwx import AppConfig
from amfwx.rf import discover, jarolift_devices

class Result:
    def __init__(self, stdout=""): self.stdout=stdout; self.stderr=""; self.returncode=0

class RfTests(unittest.TestCase):
    def test_discover(self):
        def runner(command, **kwargs):
            return Result('{"model":"Jarolift TDR","id":42,"channel":1}\n')
        items=discover(1, runner=runner, protocols=("jarolift",))
        self.assertEqual(items[0]["id"],42)
        self.assertEqual(len(jarolift_devices(1, runner=runner)),1)
    def test_cli(self):
        self.assertEqual(AppConfig.parse(["--rf-discovery","5"]).rf_discovery,5)

if __name__ == "__main__":
    unittest.main(verbosity=2)
