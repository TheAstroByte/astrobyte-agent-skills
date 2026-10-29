from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER = REPO_ROOT / "skills" / "astrobyte-git-identity" / "scripts" / "git_agent_identity.py"


def run(command: list[str], cwd: Path, *, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, env=env, check=check, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class GitIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.repository = self.root / "repository"
        self.repository.mkdir()
        run(["git", "init", "-b", "main"], self.repository)
        run(["git", "config", "user.name", "Human Local"], self.repository)
        run(["git", "config", "user.email", "human-local@example.com"], self.repository)
        self.config = self.root / "config.json"
        self.config.write_text(
            json.dumps(
                {
                    "git_identity": {
                        "mode": "dual-attribution",
                        "human": {
                            "name": "Human Owner",
                            "email": "human-owner@example.com",
                        },
                        "trailer_key": "Agent",
                        "verify_before_push": True,
                        "agents": {
                            "codex": {
                                "name": "Codex",
                                "email": "codex@local.invalid",
                            }
                        },
                    }
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def helper(self, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return run(
            [
                sys.executable,
                str(HELPER),
                "--config",
                str(self.config),
                "--harness",
                "codex",
                *arguments,
            ],
            self.repository,
            check=check,
        )

    def test_agent_commit_shows_human_author_and_agent_committer(self) -> None:
        tracked = self.repository / "change.txt"
        tracked.write_text("agent change\n", encoding="utf-8")
        run(["git", "add", "change.txt"], self.repository)

        result = self.helper("commit", "--", "-m", "agent change")

        self.assertIn("author: Human Owner <human-owner@example.com>", result.stdout)
        self.assertIn("committer: Codex <codex@local.invalid>", result.stdout)
        metadata = run(
            ["git", "show", "-s", "--format=%an|%ae|%cn|%ce|%B", "HEAD"],
            self.repository,
        ).stdout
        self.assertIn("Human Owner|human-owner@example.com|Codex|codex@local.invalid", metadata)
        self.assertIn("Agent: Codex <codex@local.invalid>", metadata)
        audit = self.helper("audit", "HEAD^!")
        self.assertIn("agent:codex", audit.stdout)

    def test_agent_commit_does_not_change_later_human_identity(self) -> None:
        tracked = self.repository / "change.txt"
        tracked.write_text("agent change\n", encoding="utf-8")
        run(["git", "add", "change.txt"], self.repository)
        self.helper("commit", "--", "-m", "agent change")

        tracked.write_text("human change\n", encoding="utf-8")
        run(["git", "commit", "-am", "human change"], self.repository)

        metadata = run(
            ["git", "show", "-s", "--format=%an|%ae|%cn|%ce|%B", "HEAD"],
            self.repository,
        ).stdout
        self.assertIn("Human Local|human-local@example.com|Human Local|human-local@example.com", metadata)
        self.assertNotIn("Agent:", metadata)
        self.assertEqual(run(["git", "config", "user.name"], self.repository).stdout.strip(), "Human Local")

    def test_unknown_harness_is_rejected(self) -> None:
        result = run(
            [
                sys.executable,
                str(HELPER),
                "--config",
                str(self.config),
                "--harness",
                "opencode",
                "show",
            ],
            self.repository,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("No Git identity configured", result.stderr)

    def portable_helper(self, *arguments: str, check: bool = True, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        skill = self.root / "installed-git-identity"
        if not skill.exists():
            shutil.copytree(HELPER.parent.parent, skill)
        environment = {key: value for key, value in os.environ.items() if not key.startswith(("GIT_", "ASTROBYTE_"))}
        environment.update({"HOME": str(self.root / "empty-home"), "GIT_CONFIG_NOSYSTEM": "1"})
        environment.update(extra_env or {})
        return run([sys.executable, "-B", str(skill / "scripts/git_agent_identity.py"), "--harness", "cursor", *arguments],
                   self.repository, check=check, env=environment)

    def test_portable_commit_amend_and_audit_preserve_normal_git(self) -> None:
        (self.repository / "change.txt").write_text("portable change")
        run(["git", "add", "change.txt"], self.repository)
        result = self.portable_helper("commit", "--", "-m", "portable change", extra_env={
            "GIT_COMMITTER_NAME": "Ambient", "GIT_COMMITTER_EMAIL": "ambient@example.com",
        })
        self.assertIn("author: Human Local <human-local@example.com>", result.stdout)
        self.assertIn("committer: Cursor <cursor@local.invalid>", result.stdout)
        self.portable_helper("commit", "--", "--amend", "--no-edit")
        self.assertIn("agent:cursor", self.portable_helper("audit", "HEAD^!").stdout)
        self.assertEqual(run(["git", "config", "user.name"], self.repository).stdout.strip(), "Human Local")
        self.assertNotIn("Agent:", run(["git", "config", "--list"], self.repository).stdout)

    def test_effective_conditional_config_and_author_environment_are_used(self) -> None:
        included = self.root / "identity.gitconfig"
        included.write_text("[user]\n name = Conditional Owner\n email = conditional@example.com\n")
        run(["git", "config", f"includeIf.gitdir:{self.repository.resolve()}/.git.path", str(included)], self.repository)
        self.assertIn("Conditional Owner <conditional@example.com>", self.portable_helper("show").stdout)
        result = self.portable_helper("show", extra_env={"GIT_AUTHOR_NAME": "Environment Owner", "GIT_AUTHOR_EMAIL": "env@example.com"})
        self.assertIn("Environment Owner <env@example.com>", result.stdout)

    def test_missing_identity_and_explicit_config_fail_before_commit(self) -> None:
        run(["git", "config", "--unset", "user.name"], self.repository)
        run(["git", "config", "--unset", "user.email"], self.repository)
        result = self.portable_helper("commit", "--", "--allow-empty", "-m", "must not commit", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Configure your own Git author", result.stderr)
        self.assertNotEqual(run(["git", "rev-parse", "HEAD"], self.repository, check=False).returncode, 0)
        result = self.portable_helper("show", check=False, extra_env={"ASTROBYTE_CONFIG": str(self.root / "missing.json")})
        self.assertIn("Explicit Git config is unavailable", result.stderr)

    def test_disabled_and_malformed_explicit_policy_do_not_fall_back(self) -> None:
        policy = json.loads(self.config.read_text())
        policy["git_identity"]["mode"] = "disabled"
        self.config.write_text(json.dumps(policy))
        result = self.helper("show", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("does not enable agent attribution", result.stderr)
        self.config.write_text("invalid JSON")
        self.assertEqual(self.helper("show", check=False).returncode, 2)

    def test_amend_keeps_an_existing_different_author(self) -> None:
        run(["git", "commit", "--allow-empty", "-m", "original", "--author", "Original Owner <original@example.com>"], self.repository)
        result = self.portable_helper("commit", "--", "--amend", "--no-edit", "--allow-empty")
        self.assertIn("author: Original Owner <original@example.com>", result.stdout)
        self.assertIn("committer: Cursor <cursor@local.invalid>", result.stdout)
        self.assertEqual(self.portable_helper("verify-head").returncode, 0)
        self.assertIn("agent:cursor", self.portable_helper("audit", "HEAD^!").stdout)

    def test_wrong_author_without_preservation_record_fails_audit(self) -> None:
        run(["git", "-c", "user.name=Cursor", "-c", "user.email=cursor@local.invalid", "commit",
             "--allow-empty", "--author", "Wrong <wrong@example.com>", "-m", "Agent: Cursor <cursor@local.invalid>"], self.repository)
        self.assertEqual(self.portable_helper("verify-head", check=False).returncode, 1)
        self.assertEqual(self.portable_helper("audit", "HEAD^!", check=False).returncode, 1)


if __name__ == "__main__":
    unittest.main()
