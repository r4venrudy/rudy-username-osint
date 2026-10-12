import unittest

from rudy_runtime.validation import clamp_timeout, clean_username


class CleanUsernameTests(unittest.TestCase):
    def test_accepts_safe_names_and_strips_spaces(self):
        self.assertEqual(clean_username("  r4ven.rudy_-  "), "r4ven.rudy_-")

    def test_rejects_too_short_and_too_long(self):
        self.assertIsNone(clean_username("ab"))
        self.assertIsNone(clean_username("a" * 31))
        self.assertEqual(clean_username("a" * 30), "a" * 30)

    def test_rejects_unsafe_characters(self):
        for bad in ("raven rudy", "raven/../x", "raven;ls", "ra$ven", ""):
            self.assertIsNone(clean_username(bad), bad)

    def test_rejects_names_that_look_like_options(self):
        for bad in ("--version", "-raven", "--site"):
            self.assertIsNone(clean_username(bad), bad)
        self.assertEqual(clean_username("raven-rudy"), "raven-rudy")

    def test_handles_none(self):
        self.assertIsNone(clean_username(None))


class ClampTimeoutTests(unittest.TestCase):
    def test_default_when_missing(self):
        self.assertEqual(clamp_timeout(None), 60)
        self.assertEqual(clamp_timeout(0), 60)

    def test_limits(self):
        self.assertEqual(clamp_timeout(5), 15)
        self.assertEqual(clamp_timeout(-30), 15)
        self.assertEqual(clamp_timeout(999), 180)
        self.assertEqual(clamp_timeout(90), 90)
