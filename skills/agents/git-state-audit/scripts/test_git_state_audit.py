import unittest

import git_state_audit as audit


class GitStateAuditTests(unittest.TestCase):
    def test_cli_side_effects_are_opt_in(self):
        defaults = audit.build_parser().parse_args([])
        self.assertFalse(defaults.fetch)
        self.assertFalse(defaults.safe_pull)
        self.assertFalse(defaults.gh_auth_switch)

        enabled = audit.build_parser().parse_args(
            ["--fetch", "--safe-pull", "--gh-auth-switch"]
        )
        self.assertTrue(enabled.fetch)
        self.assertTrue(enabled.safe_pull)
        self.assertTrue(enabled.gh_auth_switch)

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

    def test_extracts_github_owner_from_https_and_ssh_urls(self):
        self.assertEqual(
            audit.github_owner_from_remote("https://github.com/flsteven87/contextra.git"),
            "flsteven87",
        )
        self.assertEqual(
            audit.github_owner_from_remote("git@github.com:flsteven87/contextra.git"),
            "flsteven87",
        )
        self.assertIsNone(audit.github_owner_from_remote("https://gitlab.com/acme/repo.git"))

    def test_detects_github_auth_or_visibility_failures(self):
        self.assertTrue(audit.is_github_auth_failure("remote: Repository not found."))
        self.assertTrue(audit.is_github_auth_failure("fatal: Authentication failed"))
        self.assertFalse(audit.is_github_auth_failure("fatal: not a git repository"))

    def test_safe_pull_requires_clean_local_main_only_behind_origin_main(self):
        self.assertTrue(
            audit.is_safe_pull_candidate(
                branch="main",
                upstream="origin/main",
                clean=True,
                ahead=0,
                behind=2,
            )
        )

        unsafe_cases = [
            {"branch": "feature", "upstream": "origin/feature", "clean": True, "ahead": 0, "behind": 2},
            {"branch": "main", "upstream": "origin/main", "clean": False, "ahead": 0, "behind": 2},
            {"branch": "main", "upstream": "origin/main", "clean": True, "ahead": 1, "behind": 2},
            {"branch": "main", "upstream": "upstream/main", "clean": True, "ahead": 0, "behind": 2},
            {"branch": "main", "upstream": "origin/main", "clean": True, "ahead": 0, "behind": 0},
        ]
        for case in unsafe_cases:
            with self.subTest(case=case):
                self.assertFalse(audit.is_safe_pull_candidate(**case))


if __name__ == "__main__":
    unittest.main()
