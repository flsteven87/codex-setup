from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import discover_graphs as discovery


class DiscoverGraphsTests(unittest.TestCase):
    def test_discovers_graphs_and_prunes_dependency_trees(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            expected = root / "api" / "graphify-out" / "graph.json"
            ignored = root / "node_modules" / "pkg" / "graphify-out" / "graph.json"
            expected.parent.mkdir(parents=True)
            ignored.parent.mkdir(parents=True)
            expected.write_text("{}\n")
            ignored.write_text("{}\n")

            self.assertEqual(discovery.discover(root), [expected.resolve()])

    def test_prefers_the_narrowest_graph_that_covers_the_target(self):
        root = Path("/repo")
        target = root / "api" / "services"

        broad = discovery.relation(root, target)
        narrow = discovery.relation(root / "api", target)

        self.assertLess(narrow, broad)
        self.assertEqual(narrow[2], "covers-target")


if __name__ == "__main__":
    unittest.main()
