import os
import runpy
import unittest
from unittest.mock import patch


class ScaffoldTests(unittest.TestCase):
    def test_missing_configuration_is_reported(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "Missing required runner configuration"):
                runpy.run_path(".github/scripts/anzerai.py", run_name="not_main")


if __name__ == "__main__":
    unittest.main()
