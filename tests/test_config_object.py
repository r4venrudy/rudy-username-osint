import json
import tempfile
import unittest
from pathlib import Path
from rudy_runtime.config import load_config

class ConfigObjectTests(unittest.TestCase):
    def test_non_objects_fail_before_environment_overrides(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'config.json'
            for value in (None, [], False, 42, 'dummy-secret'):
                path.write_text(json.dumps(value),encoding='utf-8')
                with self.subTest(value=value), self.assertRaisesRegex(ValueError,'Configuration must be a JSON object'):
                    load_config({'TOKEN':'DISCORD_TOKEN'},env={'DISCORD_TOKEN':'dummy-env'},filename=path)
