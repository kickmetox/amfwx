from __future__ import annotations
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from amfwx import (CameraDriver, create_camera_driver, list_camera_drivers,
                   register_camera_driver, unregister_camera_driver)

class Fake(CameraDriver):
    name='fake'

class CameraPluginTests(unittest.TestCase):
    def test_registry(self):
        register_camera_driver('fake', lambda **kw: Fake())
        try:
            self.assertIn('fake', list_camera_drivers())
            self.assertIsInstance(create_camera_driver('fake'), Fake)
            with self.assertRaises(Exception):
                register_camera_driver('fake', lambda **kw: Fake())
        finally:
            unregister_camera_driver('fake')

if __name__ == '__main__':
    unittest.main(verbosity=2)
