from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "skills" / "astrobyte-pr-workflows"
SCRIPT = PACKAGE / "scripts" / "workflow_state.py"


class PRWorkflowStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.state = self.root / "state"
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("ASTROBYTE_") and key != "PYTHONPATH"}
        self.env["HOME"] = str(self.root / "empty-home")
        self.env["ASTROBYTE_CONFIG_HOME"] = str(self.state)
        self.members = {
            "members": [
                {"label": "First", "model": "offered-first", "provider": "First provider", "route": "native"},
                {"label": "Second", "model": "offered-second", "route": "approved-gateway"},
                {"model": "offered-third", "route": "native"},
            ]
        }

    def input_file(self, name: str, value: object) -> Path:
        path = self.root / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def cli(self, *args: str, script: Path = SCRIPT, expected: int = 0, env: dict[str, str] | None = None) -> dict | subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, "-B", str(script), *args],
            cwd=self.root,
            env=self.env if env is None else env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, expected, result.stderr)
        return json.loads(result.stdout) if expected == 0 else result

    def test_council_first_use_repeat_and_host_isolation(self) -> None:
        self.assertEqual(self.cli("council", "show", "--harness", "codex"), {"configured": False, "harness": "codex"})
        self.assertFalse(self.state.exists())
        approved = self.input_file("council.json", self.members)
        expected = self.cli("council", "set", "--harness", "codex", "--input", str(approved))
        self.assertTrue(expected["configured"])
        self.assertEqual(expected["council"], self.members)
        self.assertEqual(self.cli("council", "show", "--harness", "codex"), expected)
        saved = self.state / "pr-workflows/councils/codex.json"
        modified = saved.stat().st_mtime_ns
        self.assertEqual(self.cli("council", "set", "--harness", "codex", "--input", str(approved)), expected)
        self.assertEqual(saved.stat().st_mtime_ns, modified)
        self.assertFalse(self.cli("council", "show", "--harness", "t3")["configured"])

    def test_repository_policy_has_independent_repo_and_base_keys(self) -> None:
        approved = self.input_file("bots.json", {"required_bots": [], "advisory_bots": ["Example Bot"]})
        original = self.cli("repository", "set", "--repo", "Owner/Project", "--base", "main", "--input", str(approved))
        self.assertEqual(original["repository"], "github.com/owner/project")
        self.assertEqual(self.cli("repository", "show", "--repo", "github.com/OWNER/PROJECT", "--base", "main"), original)
        self.assertFalse(self.cli("repository", "show", "--repo", "owner/project", "--base", "release")["configured"])
        ci_only = self.input_file("ci-only.json", {"required_bots": [], "advisory_bots": []})
        self.cli("repository", "set", "--repo", "owner/project", "--base", "release", "--input", str(ci_only))
        self.cli("repository", "set", "--repo", "enterprise.example/owner/project", "--base", "main", "--input", str(ci_only))
        self.assertEqual(len(list((self.state / "pr-workflows/repositories").glob("*.json"))), 3)
        self.assertEqual(self.cli("repository", "show", "--repo", "owner/project", "--base", "main"), original)

    def test_invalid_selections_fail_before_any_state_write(self) -> None:
        invalid_members = [
            {},
            {"members": []},
            {"members": [{"model": "one", "route": "native"}]},
            {"members": [self.members["members"][0]] * 3},
            {"members": [{"model": "one", "route": "native", "token": "NOT_A_CREDENTIAL"}, self.members["members"][1]]},
        ]
        for index, value in enumerate(invalid_members):
            approved = self.input_file(f"invalid-council-{index}.json", value)
            self.cli("council", "set", "--harness", "codex", "--input", str(approved), expected=1)
            self.assertFalse(self.state.exists())
        for index, value in enumerate((
            {"required_bots": ["Same"], "advisory_bots": ["same"]},
            {"required_bots": [], "advisory_bots": [], "allow_merge": True},
            {"required_bots": ["Bot", "bot"], "advisory_bots": []},
            {"required_bots": [], "advisory_bots": "none"},
        )):
            approved = self.input_file(f"invalid-policy-{index}.json", value)
            self.cli("repository", "set", "--repo", "owner/project", "--base", "main", "--input", str(approved), expected=1)
            self.assertFalse(self.state.exists())

    def test_stored_state_is_validated_and_read_errors_preserve_it(self) -> None:
        approved = self.input_file("council.json", self.members)
        self.cli("council", "set", "--harness", "codex", "--input", str(approved))
        saved = self.state / "pr-workflows/councils/codex.json"
        for value in ("not JSON", json.dumps({"schema_version": 1, "harness": "other", "council": self.members}), json.dumps({"schema_version": True, "harness": "codex", "council": self.members})):
            saved.write_text(value)
            self.cli("council", "show", "--harness", "codex", expected=1)
            self.assertEqual(saved.read_text(), value)

    def test_config_location_precedence_and_invalid_keys(self) -> None:
        selected = self.root / "selected"
        selected.mkdir()
        config = selected / "config.json"
        config.write_text("{}")
        env = {**self.env, "ASTROBYTE_CONFIG": str(config)}
        approved = self.input_file("council.json", self.members)
        self.cli("council", "set", "--harness", "codex", "--input", str(approved), env=env)
        self.assertTrue((selected / "pr-workflows/councils/codex.json").is_file())
        self.assertFalse(self.state.exists())
        self.assertTrue(self.cli("council", "show", "--harness", "codex", env={**env, "ASTROBYTE_CONFIG": str(selected)})["configured"])
        override = self.root / "override"
        self.cli("--state-dir", str(override), "council", "set", "--harness", "codex", "--input", str(approved), env=env)
        self.assertTrue((override / "pr-workflows/councils/codex.json").is_file())
        self.cli("council", "show", "--harness", "../escape", expected=1)
        self.cli("repository", "show", "--repo", "owner/../escape", "--base", "main", expected=1)
        self.cli("repository", "show", "--repo", "owner/project", "--base", "main\nother", expected=1)
        self.cli("--state-dir", "/", "council", "show", "--harness", "codex", expected=1)
        self.cli("council", "show", "--harness", "codex", expected=1, env={**self.env, "ASTROBYTE_CONFIG": str(self.root / "missing")})
        config.write_text("[]")
        self.cli("council", "show", "--harness", "codex", expected=1, env=env)

    def test_copied_package_has_no_source_dependency_for_state_or_policy(self) -> None:
        installed = self.root / "installed"
        copied = installed / PACKAGE.name
        shutil.copytree(PACKAGE, copied)
        shutil.copytree(ROOT / "skills/astrobyte-mode", installed / "astrobyte-mode")
        script = copied / "scripts/workflow_state.py"
        self.assertEqual(self.cli("policy", script=script)["pr_workflows"], {"review_method": "baseline", "council_round_limit": 3, "t3": False})
        approved = self.input_file("members.json", self.members)
        saved = self.cli("council", "set", "--harness", "t3", "--input", str(approved), script=script)
        self.assertEqual(self.cli("council", "show", "--harness", "t3", script=script), saved)

    def test_portable_policy_and_local_project_precedence(self) -> None:
        installed = self.root / "installed"
        copied = installed / PACKAGE.name
        shutil.copytree(PACKAGE, copied)
        mode = installed / "astrobyte-mode"
        shutil.copytree(ROOT / "skills/astrobyte-mode", mode)
        preferences = {
            "schema_version": 1,
            "baseline": {"handle": "astrobyte", "repository_version": "0.5.0"},
            "overrides": {"pr_workflows": {"review_method": "sol-loop", "council_round_limit": 4, "t3": True}},
        }
        (mode / "references/preferences.json").write_text(json.dumps(preferences))
        project = self.root / "project"
        (project / ".astrobyte").mkdir(parents=True)
        (project / ".astrobyte/config.json").write_text(json.dumps({"pr_workflows": {"council_round_limit": 2}}))
        effective = self.cli("policy", "--project", str(project), script=copied / "scripts/workflow_state.py")
        self.assertEqual(effective["pr_workflows"], {"review_method": "sol-loop", "council_round_limit": 2, "t3": True})
        self.assertEqual(effective["sources"]["review_method"], "portable-personal")
        self.assertEqual(effective["sources"]["council_round_limit"], "project")

    def test_missing_runtime_dependency_is_an_error_not_default_policy(self) -> None:
        copied = self.root / "isolated/astrobyte-pr-workflows"
        shutil.copytree(PACKAGE, copied)
        self.cli("policy", script=copied / "scripts/workflow_state.py", expected=1)
        self.assertFalse(self.state.exists())

    def test_native_install_keeps_default_clean_and_exports_selected_policy(self) -> None:
        home = self.root / "installed-home"
        command = [sys.executable, "-B", str(ROOT / "scripts/install.py"), "--harnesses", "cursor", "--home", str(home), "--yes"]

        def install(*extra: str) -> None:
            result = subprocess.run([*command, *extra], cwd=self.root, env=self.env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        install()
        target = home / ".cursor/skills/astrobyte-pr-workflows"
        self.assertFalse(target.exists())
        delta = {
            "schema_version": 1,
            "baseline": {"handle": "astrobyte", "repository_version": "0.5.0"},
            "overrides": {
                "optional_skills": ["astrobyte-pr-workflows"],
                "pr_workflows": {"review_method": "sol-loop", "council_round_limit": 3, "t3": True},
            },
        }
        reviewed = self.input_file("reviewed-personal-options.json", delta)
        install("--preferences", str(reviewed), "--portable-preferences")
        self.assertEqual(json.loads((target / "references/preferences.json").read_text()), delta)
        isolated = {key: value for key, value in self.env.items() if not key.startswith("ASTROBYTE_")}
        effective = self.cli("policy", script=target / "scripts/workflow_state.py", env=isolated)
        self.assertEqual(effective["pr_workflows"], delta["overrides"]["pr_workflows"])
        self.assertEqual(set(effective["sources"].values()), {"portable-personal"})
        self.assertFalse((self.state / "pr-workflows").exists())
        before = (target / "references/preferences.json").read_bytes()
        install()
        self.assertEqual((target / "references/preferences.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
