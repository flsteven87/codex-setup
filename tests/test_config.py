import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "config.example.toml"


class ConfigExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = CONFIG_PATH.read_text()
        cls.config = tomllib.loads(cls.text)

    def test_leaves_model_selection_to_codex(self) -> None:
        self.assertNotIn("model", self.config)

    def test_uses_high_trust_local_execution(self) -> None:
        self.assertEqual(self.config["approval_policy"], "on-request")
        self.assertEqual(self.config["sandbox_mode"], "danger-full-access")

    def test_enables_reviewed_agent_workflow_features(self) -> None:
        self.assertEqual(self.config["web_search"], "live")
        self.assertEqual(self.config["features"], {"hooks": True, "goals": True})
        self.assertEqual(self.config["agents"], {"max_threads": 6, "max_depth": 1})

    def test_pins_executable_mcp_packages(self) -> None:
        context7 = self.config["mcp_servers"]["context7"]
        self.assertEqual(context7["args"], ["-y", "@upstash/context7-mcp@3.2.3"])

    def test_contains_no_project_or_literal_authorization_state(self) -> None:
        self.assertNotIn("projects", self.config)
        self.assertNotIn("authorization", self.text.lower())
        self.assertNotIn("js_repl", self.config.get("features", {}))

    def test_serena_is_codex_aware_and_disabled_by_default(self) -> None:
        serena = self.config["mcp_servers"]["serena"]
        self.assertFalse(serena["enabled"])
        self.assertIn("--context=codex", serena["args"])
        self.assertIn("--project-from-cwd", serena["args"])

    def test_global_mcp_set_is_portable(self) -> None:
        servers = self.config["mcp_servers"]
        self.assertEqual(
            set(servers),
            {"openaiDeveloperDocs", "context7", "linear", "serena"},
        )


if __name__ == "__main__":
    unittest.main()
