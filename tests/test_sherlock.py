import unittest

import sys

from rudy_runtime.sherlock import parse_sherlock_output, results_text, sherlock_command

SAMPLE = """[*] Checking username johndoe on:

[+] GitHub: https://www.github.com/johndoe
[+] Reddit: https://www.reddit.com/user/johndoe
[-] Twitch: Not Found!
[+] GitHub: https://www.github.com/johndoe
[*] Search completed with 2 results
[*] Results saved to https://example.invalid/report
"""


class SherlockParseTests(unittest.TestCase):
    def test_only_found_profiles_without_duplicates(self):
        self.assertEqual(parse_sherlock_output(SAMPLE), [
            {"name": "GitHub", "url": "https://www.github.com/johndoe"},
            {"name": "Reddit", "url": "https://www.reddit.com/user/johndoe"},
        ])

    def test_empty_output(self):
        self.assertEqual(parse_sherlock_output(""), [])


if __name__ == "__main__":
    unittest.main()


class SherlockCommandTests(unittest.TestCase):
    def test_prefers_console_script(self):
        self.assertEqual(sherlock_command(lambda name: "/usr/bin/sherlock"), ["sherlock"])

    def test_falls_back_to_module(self):
        self.assertEqual(sherlock_command(lambda name: None), [sys.executable, "-m", "sherlock_project"])


class ResultsTextTests(unittest.TestCase):
    def test_lists_every_match(self):
        found = [{"name": "GitHub", "url": "https://github.com/x"}, {"name": "Reddit", "url": "https://reddit.com/u/x"}]
        self.assertEqual(results_text("x", found),
                         "Sherlock matches for x (2)\n\nGitHub: https://github.com/x\nReddit: https://reddit.com/u/x\n")
