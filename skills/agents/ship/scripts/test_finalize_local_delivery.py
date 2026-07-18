from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

import finalize_local_delivery as finalizer


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


class FinalizeLocalDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.repo = self.root / "repo"
        self.task = self.root / "task"
        self.repo.mkdir()
        git(self.repo, "init", "-b", "main")
        git(self.repo, "config", "user.name", "Test User")
        git(self.repo, "config", "user.email", "test@example.com")
        (self.repo / "base.txt").write_text("base\n")
        git(self.repo, "add", "base.txt")
        git(self.repo, "commit", "-m", "base")
        git(self.repo, "branch", "feature/test")
        git(self.repo, "worktree", "add", str(self.task), "feature/test")
        (self.task / "feature.txt").write_text("feature\n")
        git(self.task, "add", "feature.txt")
        git(self.task, "commit", "-m", "feature")
        self.feature_head = git(self.task, "rev-parse", "HEAD")

    def build_plan(self, **overrides):
        values = {
            "repo": self.repo,
            "worktree_path": self.task,
            "branch": "feature/test",
            "expected_head_revision": self.feature_head,
            "default_branch": "main",
            "integrated_ref": "main",
            "squash_commit_revision": None,
        }
        values.update(overrides)
        return finalizer.build_plan(**values)

    def test_preview_and_execute_merged_linked_worktree(self):
        git(self.repo, "remote", "add", "origin", "https://example.invalid/repo.git")
        git(
            self.repo,
            "update-ref",
            "refs/remotes/origin/feature/test",
            self.feature_head,
        )
        git(
            self.repo,
            "branch",
            "--set-upstream-to=origin/feature/test",
            "feature/test",
        )
        git(self.repo, "update-ref", "-d", "refs/remotes/origin/feature/test")
        git(self.repo, "merge", "--no-ff", "feature/test", "-m", "merge feature")

        plan = self.build_plan()

        self.assertFalse(plan.force_delete)
        self.assertIn("ancestor", plan.proof)
        self.assertTrue(self.task.exists())
        finalizer.execute_plan(plan)
        self.assertFalse(self.task.exists())
        branches = git(self.repo, "branch", "--format=%(refname:short)").splitlines()
        self.assertNotIn("feature/test", branches)

    def test_refuses_dirty_worktree(self):
        git(self.repo, "merge", "--no-ff", "feature/test", "-m", "merge feature")
        (self.task / "dirty.txt").write_text("dirty\n")

        with self.assertRaisesRegex(finalizer.SafetyError, "worktree is dirty"):
            self.build_plan()

    def test_refuses_branch_that_moved_after_recorded_head(self):
        git(self.repo, "merge", "--no-ff", "feature/test", "-m", "merge feature")
        (self.task / "later.txt").write_text("later\n")
        git(self.task, "add", "later.txt")
        git(self.task, "commit", "-m", "later")

        with self.assertRaisesRegex(finalizer.SafetyError, "delivery branch moved"):
            self.build_plan()

    def test_accepts_matching_squash_commit_and_force_deletes(self):
        git(self.repo, "merge", "--squash", "feature/test")
        git(self.repo, "commit", "-m", "squash feature")
        squash_commit = git(self.repo, "rev-parse", "HEAD")

        plan = self.build_plan(squash_commit_revision=squash_commit)

        self.assertTrue(plan.force_delete)
        self.assertIn(squash_commit, plan.proof)
        finalizer.execute_plan(plan)
        branches = git(self.repo, "branch", "--format=%(refname:short)").splitlines()
        self.assertNotIn("feature/test", branches)

    def test_refuses_unproven_squash_merge(self):
        git(self.repo, "merge", "--squash", "feature/test")
        git(self.repo, "commit", "-m", "squash feature")

        with self.assertRaisesRegex(finalizer.SafetyError, "no squash proof"):
            self.build_plan()

    def test_primary_worktree_switches_and_fast_forwards_default_branch(self):
        git(self.repo, "worktree", "remove", str(self.task))
        git(self.repo, "switch", "feature/test")
        git(self.repo, "merge", "--ff-only", self.feature_head)
        git(self.repo, "switch", "main")
        base_head = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "merge", "--no-ff", "feature/test", "-m", "remote merge")
        integrated_head = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "update-ref", "refs/remotes/origin/main", integrated_head)
        git(self.repo, "reset", "--hard", base_head)
        git(self.repo, "switch", "feature/test")

        plan = finalizer.build_plan(
            repo=self.repo,
            worktree_path=self.repo,
            branch="feature/test",
            expected_head_revision=self.feature_head,
            default_branch="main",
            integrated_ref="origin/main",
            squash_commit_revision=None,
        )

        self.assertTrue(plan.task_worktree.primary)
        self.assertTrue(plan.fast_forward_default)
        finalizer.execute_plan(plan)
        self.assertEqual(git(self.repo, "branch", "--show-current"), "main")
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), integrated_head)
        branches = git(self.repo, "branch", "--format=%(refname:short)").splitlines()
        self.assertNotIn("feature/test", branches)


if __name__ == "__main__":
    unittest.main()
