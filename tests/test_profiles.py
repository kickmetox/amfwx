from __future__ import annotations
import os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from amfwx import ProfileStore

class ProfileTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'profiles.json'
            store=ProfileStore(path)
            store.save('scanner','A4',{'dpi':'300'})
            self.assertEqual(ProfileStore(path).load('scanner','A4')['dpi'],'300')
            self.assertEqual(store.names('scanner'),['A4'])
            store.delete('scanner','A4')
            self.assertEqual(store.names('scanner'),[])
    def test_missing(self):
        with tempfile.TemporaryDirectory() as folder:
            store=ProfileStore(Path(folder)/'p.json')
            with self.assertRaises(Exception):
                store.load('scanner','x')

if __name__ == '__main__':
    unittest.main(verbosity=2)
