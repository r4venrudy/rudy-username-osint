import tempfile
import unittest
from pathlib import Path
from rudy_runtime.config import load_config

class BomConfigTests(unittest.TestCase):
    def test_bom_and_unicode_round_trip_without_modification(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'config.json'
            original = b'\xef\xbb\xbf{"TOKEN":"dummy-\xc3\xa9"}'
            path.write_bytes(original)
            self.assertEqual(load_config({'TOKEN':'DISCORD_TOKEN'},env={},filename=path)['TOKEN'], 'dummy-\u00e9')
            self.assertEqual(path.read_bytes(),original)
