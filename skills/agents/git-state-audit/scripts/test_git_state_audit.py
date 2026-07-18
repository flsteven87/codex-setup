import subprocess
import tempfile
import unittest
from pathlib import Path

import git_state_audit as audit


def git(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    return completed.stdout.strip()


class GitStateAuditTests(unittest.TestCase):
    def test_remote_refresh_and_edge_checks_are_opt_in(self):
        defaults = audit.build_parser().parse_args([])
        self.assertFalse(defaults.fetch)
        self.assertFalse(defaults.edge_checks)
        self.assertFalse(hasattr(defaults, "safe_pull"))
        self.assertFalse(hasattr(defaults, "gh_auth_switch"))

        enabled = audit.build_parser().parse_args(["--fetch", "--edge-checks"])
        self.assertTrue(enabled.fetch)
        self.assertTrue(enabled.edge_checks)

    def test_summarizes_porcelain_counts(self):
        summary = audit.summarize_porcelain(
            [
                "M  staged.py",
                " M unstaged.py",
                "?? new.txt",
                "MM both.py",
                "A  added.py",
            ]
        )

        self.assertEqual(summary.staged, 3)
        self.assertEqual(summary.unstaged, 2)
        self.assertEqual(summary.untracked, 1)
        self.assertFalse(summary.clean)

    def test_redacts_token_like_values_and_credentialed_urls(self):
        output = (
            "origin https://user:ghp_1234567890abcdef@github.com/acme/repo.git\n"
            "token=github_pat_abcdef1234567890\n"
        )

        redacted = audit.redact(output)

        self.assertNotIn("ghp_1234567890abcdef", redacted)
        self.assertNotIn("github_pat_abcdef1234567890", redacted)
        self.assertIn("https://<redacted>@github.com/acme/repo.git", redacted)

    def test_preserves_colons_in_oldest_stash_timestamp(self):
        stash_output = (
            "stash@{2026-07-18 14:15:16 +0800}: On main: recent\n"
            "stash@{2026-07-17 09:08:07 +0800}: On main: oldest\n"
        )

        self.assertEqual(
            audit.oldest_stash(stash_output),
            "2026-07-17 09:08:07 +0800",
        )

    def test_edge_recovery_check_does_not_write_lost_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            git(repo, "init", "-b", "main")
            git(repo, "config", "user.name", "Test User")
            git(repo, "config", "user.email", "test@example.com")
            (repo / "tracked.txt").write_text("tracked\n")
            git(repo, "add", "tracked.txt")
            git(repo, "commit", "-m", "initial")

            result = audit.collect_audit(repo, fetch=False, edge_checks=True)

            commands = [command["command"] for command in result["commands"]]
            flattened = [argument for command in commands for argument in command]
            self.assertNotIn("pull", flattened)
            self.assertNotIn("--lost-found", flattened)
            self.assertIn("--unreachable", flattened)
            self.assertFalse((repo / ".git" / "lost-found").exists())


if __name__ == "__main__":
    unittest.main()
