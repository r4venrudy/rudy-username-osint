import unittest

from rudy_runtime.sherlock import parse_sherlock_output

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
