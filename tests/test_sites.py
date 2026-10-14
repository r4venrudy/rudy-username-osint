import importlib.util
import json
import os
import unittest

from rudy_runtime.sites import SITES_TO_CHECK, pick_sites


def sherlock_data():
    # locate the package without importing it (its __init__ needs extra dependencies)
    spec = importlib.util.find_spec("sherlock_project")
    if spec is None or not spec.submodule_search_locations:
        return None
    path = os.path.join(spec.submodule_search_locations[0], "resources", "data.json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


DATA = sherlock_data()


class SiteListTests(unittest.TestCase):
    def test_no_duplicates(self):
        self.assertEqual(len(SITES_TO_CHECK), len({s.lower() for s in SITES_TO_CHECK}))

    @unittest.skipIf(DATA is None, "sherlock-project is not installed")
    def test_every_site_is_known_to_sherlock(self):
        known = {k.lower() for k in DATA}
        self.assertEqual([s for s in SITES_TO_CHECK if s.lower() not in known], [])


class PickSitesTests(unittest.TestCase):
    def test_empty_filter_means_all(self):
        self.assertEqual(pick_sites(None), (SITES_TO_CHECK, []))
        self.assertEqual(pick_sites("  "), (SITES_TO_CHECK, []))

    def test_case_insensitive_without_duplicates(self):
        self.assertEqual(pick_sites("github, REDDIT,github,"), (["GitHub", "Reddit"], []))

    def test_unknown_names_are_reported(self):
        self.assertEqual(pick_sites("GitHub, MySpace"), (["GitHub"], ["MySpace"]))
