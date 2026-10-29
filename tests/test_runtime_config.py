from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.runtime_config import resolve
from scripts.portable_profile import REPO_ROOT


class RuntimeConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.home = self.root / "home"
        self.project = self.root / "project"
        self.project.mkdir()
        self.skill = self.root / "astrobyte-mode"
        shutil.copytree(REPO_ROOT / "skills/astrobyte-mode", self.skill)
        self.environment = patch.dict(os.environ, {}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def write(self, path: Path, value: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    def test_packaged_command_runs_without_source_or_config(self) -> None:
        for name in ("astrobyte-mode", "astrobyte-review"):
            skill = self.root / name
            if not skill.exists():
                shutil.copytree(REPO_ROOT / "skills" / name, skill)
            result = subprocess.run(
                [sys.executable, "-B", str(skill / "scripts/runtime_config.py"), "--project", str(self.project)],
                cwd=self.root, env={"HOME": str(self.home)}, capture_output=True, text=True, check=True,
            )
            policy = json.loads(result.stdout)
            self.assertEqual(policy["preferences"]["delivery_mode"], "durable")
            self.assertEqual(set(policy["sources"].values()), {"baseline"})
            self.assertIsNone(policy["local_working_agreement"])
            self.assertNotIn("pr_workflows", policy)
            if name == "astrobyte-review":
                self.assertIn("newest GPT Sol", policy["review_instructions"])

    def test_personal_machine_project_precedence_and_secret_exclusion(self) -> None:
        state = self.home / ".config/astrobyte-agent-skills"
        self.write(state / "operator-profile.json", {"defaults": {"delivery_mode": "prototype", "issue_tracker": "none"}})
        self.write(state / "config.json", {
            "delivery_mode": "production", "credential": "PRIVATE_SENTINEL",
            "max_parallel_workers": 1, "unattended_external_actions": "deny",
        })
        self.write(self.project / ".astrobyte/config.json", {"delivery_mode": "explore"})
        result = resolve(self.skill, self.project, self.home)
        self.assertEqual(result["preferences"]["delivery_mode"], "explore")
        self.assertEqual(result["sources"]["delivery_mode"], "project")
        self.assertEqual(result["preferences"]["issue_tracker"], "none")
        self.assertEqual(result["sources"]["issue_tracker"], "personal")
        self.assertNotIn("PRIVATE_SENTINEL", json.dumps(result))
        self.assertEqual(result["preferences"]["max_parallel_workers"], 1)
        self.assertEqual(result["preferences"]["unattended_external_actions"], "deny")
        (self.project / ".astrobyte/config.json").unlink()
        self.assertEqual(resolve(self.skill, self.project, self.home)["sources"]["delivery_mode"], "machine")

    def test_explicit_config_directory_and_local_agreement(self) -> None:
        state = self.root / "custom"
        self.write(state / "config.json", {"delivery_mode": "ask"})
        (state / "working-agreement.md").write_text("Choose a reviewer per task.")
        with patch.dict(os.environ, {"ASTROBYTE_CONFIG": str(state)}):
            result = resolve(self.skill, self.project, self.home)
        self.assertEqual(result["preferences"]["delivery_mode"], "ask")
        self.assertEqual(result["local_working_agreement"], str(state / "working-agreement.md"))

    def test_missing_explicit_config_and_invalid_preferences_fail(self) -> None:
        with patch.dict(os.environ, {"ASTROBYTE_CONFIG": str(self.root / "missing.json")}):
            with self.assertRaisesRegex(ValueError, "Explicit ASTROBYTE_CONFIG is unavailable"):
                resolve(self.skill, self.project, self.home)
        for value in ([], {"delivery_mode": "unknown"}, {"ci_validation": "true"}, {"max_parallel_workers": 0}):
            self.write(self.project / ".astrobyte/config.json", value)
            with self.assertRaises(ValueError):
                resolve(self.skill, self.project, self.home)

    def test_runtime_uses_installer_config_home_below_explicit_config(self) -> None:
        state = self.root / "installer-state"
        other = self.root / "explicit-state"
        self.write(state / "config.json", {"delivery_mode": "prototype"})
        self.write(other / "config.json", {"delivery_mode": "production"})
        with patch.dict(os.environ, {"ASTROBYTE_CONFIG_HOME": str(state)}):
            self.assertEqual(resolve(self.skill, self.project, self.home)["preferences"]["delivery_mode"], "prototype")
            with patch.dict(os.environ, {"ASTROBYTE_CONFIG": str(other)}):
                self.assertEqual(resolve(self.skill, self.project, self.home)["preferences"]["delivery_mode"], "production")

    def test_workflow_policy_resolves_each_field_and_selects_one_review_method(self) -> None:
        def delta(options: dict) -> dict:
            return {"schema_version": 1, "baseline": {"handle": "astrobyte", "repository_version": "0.5.0"}, "overrides": {"pr_workflows": options}}

        state = self.home / ".config/astrobyte-agent-skills"
        self.write(self.skill / "references/preferences.json", delta({"review_method": "sol-loop", "council_round_limit": 2, "t3": True}))
        self.write(state / "preferences.json", delta({"council_round_limit": 3}))
        self.write(state / "config.json", {"pr_workflows": {"t3": False}})
        self.write(self.project / ".astrobyte/config.json", {"pr_workflows": {"review_method": "baseline", "council_round_limit": 4}})
        result = resolve(self.skill, self.project, self.home)
        self.assertEqual(result["pr_workflows"], {"review_method": "baseline", "council_round_limit": 4, "t3": False})
        self.assertEqual(result["pr_workflow_sources"], {"review_method": "project", "council_round_limit": "project", "t3": "machine"})
        self.assertIsNone(result["review_instructions"])
        (self.project / ".astrobyte/config.json").unlink()
        result = resolve(self.skill, self.project, self.home)
        self.assertEqual(result["pr_workflows"]["council_round_limit"], 3)
        self.assertIn("../astrobyte-pr-workflows/references/sol-loop.md", result["review_instructions"])
        self.assertIn("literal PASS", result["review_instructions"])
        self.assertEqual(sum("review_instructions" in layer for layer in result["working_agreement_layers"]), 1)

    def test_invalid_machine_or_project_workflow_policy_fails(self) -> None:
        for value in (None, [], {"t3": "true"}, {"council_round_limit": 0}, {"merge": True}):
            self.write(self.project / ".astrobyte/config.json", {"pr_workflows": value})
            with self.subTest(value=value), self.assertRaises(ValueError):
                resolve(self.skill, self.project, self.home)


if __name__ == "__main__":
    unittest.main()
