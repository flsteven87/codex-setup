import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("git_state.py")
SPEC = importlib.util.spec_from_file_location("latest_git_state", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout.strip()


class RemoteWorktreeFixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.remote = root / "remote.git"
        self.seed = root / "seed"
        self.primary = root / "primary"
        self.feature = root / "feature"

        subprocess.run(
            ["git", "init", "--bare", "--initial-branch=main", str(self.remote)],
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "init", "--initial-branch=main", str(self.seed)],
            capture_output=True,
            check=True,
        )
        self.configure(self.seed)
        git(self.seed, "commit", "--allow-empty", "-m", "initial")
        git(self.seed, "remote", "add", "origin", str(self.remote))
        git(self.seed, "push", "-u", "origin", "main")
        subprocess.run(
            ["git", "clone", str(self.remote), str(self.primary)],
            capture_output=True,
            check=True,
        )
        self.configure(self.primary)
        git(self.primary, "worktree", "add", "-b", "feature", str(self.feature))

    @staticmethod
    def configure(repo: Path) -> None:
        git(repo, "config", "user.name", "Codex Test")
        git(repo, "config", "user.email", "codex-test@example.invalid")

    def advance_remote(self, subject: str) -> None:
        git(self.seed, "commit", "--allow-empty", "-m", subject)
        git(self.seed, "push")

    def add_remote_file(self, path: str, content: str) -> None:
        target = self.seed / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        git(self.seed, "add", path)
        git(self.seed, "commit", "-m", f"add {path}")
        git(self.seed, "push")


class GitStateTests(unittest.TestCase):
    def test_sync_from_feature_fast_forwards_clean_primary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = RemoteWorktreeFixture(Path(directory))
            fixture.advance_remote("remote change")

            result = MODULE.sync_default(fixture.feature, None, None, True)

            self.assertEqual(result["status"], "aligned")
            self.assertEqual(result["action"], "fast_forwarded_default_worktree")
            self.assertEqual(
                git(fixture.primary, "rev-parse", "HEAD"),
                git(fixture.primary, "rev-parse", "origin/main"),
            )
            audit = MODULE.build_audit(fixture.feature, "origin", "main")
            self.assertEqual(audit["summary"]["worktrees"], 2)

    def test_sync_blocks_when_primary_has_tracked_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = RemoteWorktreeFixture(Path(directory))
            (fixture.primary / "blocked.txt").write_text("blocked\n")
            git(fixture.primary, "add", "blocked.txt")
            fixture.advance_remote("remote change")

            result = MODULE.sync_default(fixture.feature, None, None, True)

            self.assertEqual(result["status"], "blocked")
            self.assertIn(
                "default_tracked_changes",
                {blocker["code"] for blocker in result["blockers"]},
            )

    def test_sync_blocks_before_overwriting_an_ignored_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = RemoteWorktreeFixture(Path(directory))
            exclude = Path(
                git(
                    fixture.primary,
                    "rev-parse",
                    "--path-format=absolute",
                    "--git-path",
                    "info/exclude",
                )
            )
            exclude.write_text("ignored.txt\n")
            (fixture.primary / "ignored.txt").write_text("local-only\n")
            fixture.add_remote_file("ignored.txt", "upstream\n")

            result = MODULE.sync_default(fixture.feature, None, None, True)

            self.assertEqual(result["status"], "blocked")
            self.assertIn(
                "ignored_incoming_collision",
                {blocker["code"] for blocker in result["blockers"]},
            )
            self.assertEqual((fixture.primary / "ignored.txt").read_text(), "local-only\n")

    def test_sync_preserves_blocker_for_a_missing_primary_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = RemoteWorktreeFixture(Path(directory))
            git(fixture.primary, "switch", "-c", "primary-owner")
            default_worktree = fixture.root / "default"
            git(fixture.primary, "worktree", "add", str(default_worktree), "main")
            fixture.advance_remote("remote change")
            shutil.rmtree(default_worktree)

            result = MODULE.sync_default(fixture.feature, None, None, True)

            self.assertEqual(result["status"], "blocked")
            self.assertIn(
                "default_worktree_unavailable",
                {blocker["code"] for blocker in result["blockers"]},
            )

    def test_sync_without_remote_returns_a_stable_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            subprocess.run(
                ["git", "init", "--initial-branch=main", str(repo)],
                capture_output=True,
                check=True,
            )

            result = MODULE.sync_default(repo, None, None, False)

            self.assertEqual(result["status"], "blocked")
            self.assertEqual(result["blockers"][0]["code"], "remote_unresolved")


if __name__ == "__main__":
    unittest.main()
