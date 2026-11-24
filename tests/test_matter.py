from __future__ import annotations
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from amfwx import AppConfig, MatterController

class Result:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode=returncode; self.stdout=stdout; self.stderr=stderr

class MatterTests(unittest.TestCase):
    def test_commands(self):
        calls=[]
        def runner(command, **kwargs):
            calls.append(command); return Result()
        controller=MatterController(chip_tool="chip-tool", runner=runner)
        controller.commission(7,"1234")
        controller.on(7)
        self.assertIn("pairing", calls[0]); self.assertIn("onoff", calls[1])
        controller.level(7, 50)
        controller.color_temperature(7, 370)
        self.assertIn("levelcontrol", calls[2])
        self.assertIn("colorcontrol", calls[3])
    def test_cli(self):
        config=AppConfig.parse(["--matter-code","1234","--matter-node","7"])
        self.assertEqual(config.matter_node,7)

if __name__ == "__main__":
    unittest.main(verbosity=2)
