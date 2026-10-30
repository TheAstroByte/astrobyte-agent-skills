from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import install, routing
from scripts.preferences import validate_preferences
from scripts.runtime_config import resolve


class PreferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.home = self.root / "home"
        self.state = self.root / "state"
        self.environment = patch.dict(os.environ, {"ASTROBYTE_CONFIG_HOME": str(self.state)})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        for name in routing.ENVIRONMENT_OVERRIDES:
            os.environ.pop(name, None)
        self.profile, self.registry, self.directory = install.load_operator(install.REPO_ROOT)
        self.catalog = install.load_json(install.CATALOG_PATH)
        self.preferences = {
            "schema_version": 1,
            "baseline": {"handle": "astrobyte", "repository_version": "0.4.0"},
            "overrides": {"defaults": {"delivery_mode": "production"}},
        }
        self.path = self.root / "reviewed-preferences.json"
        self.path.write_text(json.dumps(self.preferences))

    def apply(self, *args: str) -> int:
        return install.main(["--harnesses", "cursor", "--home", str(self.home), "--yes", *args])

    def test_local_only_preferences_do_not_export(self) -> None:
        self.assertEqual(self.apply("--preferences", str(self.path)), 0)
        self.assertEqual(install.load_json(self.state / "config.json")["delivery_mode"], "production")
        self.assertEqual(install.load_json(self.state / "preferences.json"), self.preferences)
        skill = self.home / ".cursor/skills/astrobyte-mode"
        self.assertFalse((skill / "references/preferences.json").exists())
        with patch.dict(os.environ, {"ASTROBYTE_CONFIG": str(self.state)}):
            result = resolve(skill, self.root, self.home)
        self.assertEqual(result["preferences"]["delivery_mode"], "production")
        self.assertEqual(result["sources"]["delivery_mode"], "personal-delta")

    def test_portable_preferences_work_without_local_config_and_repeat_cleanly(self) -> None:
        self.preferences["overrides"].update({"review": {"instructions": "Use the explicitly selected available reviewer."}, "git_identity": {"mode": "human-with-agent-trailer"}})
        self.preferences["working_agreement"] = "Explain consequential choices concisely."
        self.path.write_text(json.dumps(self.preferences))
        self.assertEqual(self.apply("--preferences", str(self.path), "--portable-preferences"), 0)
        hashes = {name: install.tree_hash(self.home / ".cursor/skills" / name) for name in ("astrobyte-mode", "astrobyte-review", "astrobyte-git-identity", "astrobyte-project-startup")}
        for name in hashes:
            self.assertEqual(install.load_json(self.home / ".cursor/skills" / name / "references/preferences.json"), self.preferences)
        self.assertEqual(self.apply(), 0)
        self.assertEqual(hashes, {name: install.tree_hash(self.home / ".cursor/skills" / name) for name in hashes})
        env = {key: value for key, value in os.environ.items() if not key.startswith(("ASTROBYTE_", "GIT_"))}
        env["GIT_CONFIG_NOSYSTEM"] = "1"
        env["HOME"] = str(self.root / "empty-cloud-home")
        for name in ("astrobyte-review", "astrobyte-project-startup"):
            result = subprocess.run([sys.executable, "-B", str(self.home / ".cursor/skills" / name / "scripts/runtime_config.py")], env=env, cwd=self.root, check=True, capture_output=True, text=True)
            resolved = json.loads(result.stdout)
            self.assertEqual(resolved["preferences"]["delivery_mode"], "production")
            self.assertEqual(resolved["review_instructions"], self.preferences["overrides"]["review"]["instructions"])
            self.assertEqual(resolved["working_agreement_overrides"], [self.preferences["working_agreement"]])
        repository = self.root / "cloud-repository"
        repository.mkdir()
        for command in (["git", "init", "-b", "main"], ["git", "config", "user.name", "Cloud Owner"], ["git", "config", "user.email", "cloud@example.com"]):
            subprocess.run(command, cwd=repository, env=env, check=True, capture_output=True)
        identity = subprocess.run([sys.executable, "-B", str(self.home / ".cursor/skills/astrobyte-git-identity/scripts/git_agent_identity.py"), "--harness", "cursor", "show"], cwd=repository, env=env, check=True, capture_output=True, text=True)
        self.assertIn("committer: Cloud Owner <cloud@example.com>", identity.stdout)
        self.assertEqual(self.apply("--local-preferences"), 0)
        for name in hashes:
            self.assertFalse((self.home / ".cursor/skills" / name / "references/preferences.json").exists())

    def test_agreement_layers_preserve_precedence(self) -> None:
        self.preferences["working_agreement"] = "Approved local difference"
        self.path.write_text(json.dumps(self.preferences))
        self.apply("--preferences", str(self.path), "--portable-preferences")
        (self.state / "working-agreement.md").write_text("Legacy agreement")
        with patch.dict(os.environ, {"ASTROBYTE_CONFIG": str(self.state)}):
            resolved = resolve(self.home / ".cursor/skills/astrobyte-mode", self.root, self.home)
        self.assertEqual([layer["source"] for layer in resolved["working_agreement_layers"]], ["portable-personal", "personal", "personal-delta"])
        self.assertEqual(resolved["working_agreement_layers"][-1]["rules"], self.preferences["working_agreement"])

    def test_new_baseline_updates_inheritance_but_preserves_edits(self) -> None:
        self.assertEqual(self.apply(), 0)
        updated = copy.deepcopy(self.profile)
        updated["defaults"]["delivery_mode"] = "production"
        self.assertEqual(install.quick_answers(self.home, updated, ["cursor"])["delivery_mode"], "production")
        config = install.load_json(self.state / "config.json")
        config["delivery_mode"] = "prototype"
        (self.state / "config.json").write_text(json.dumps(config))
        answers = install.quick_answers(self.home, updated, ["cursor"])
        self.assertEqual(answers["delivery_mode"], "prototype")
        self.assertNotIn("delivery_mode", answers["_baseline_values"])

    def test_legacy_snapshot_remains_explicit(self) -> None:
        self.assertEqual(self.apply(), 0)
        config = install.load_json(self.state / "config.json")
        config.pop("baseline_inheritance")
        (self.state / "config.json").write_text(json.dumps(config))
        updated = copy.deepcopy(self.profile)
        updated["defaults"]["delivery_mode"] = "production"
        answers = install.quick_answers(self.home, updated, ["cursor"])
        self.assertEqual(answers["delivery_mode"], "durable")

    def test_replaced_preferences_are_backed_up(self) -> None:
        self.apply("--preferences", str(self.path))
        self.preferences["overrides"]["defaults"]["delivery_mode"] = "explore"
        self.path.write_text(json.dumps(self.preferences))
        self.apply("--preferences", str(self.path))
        backups = list((self.state / "backups").rglob("preferences.json"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(install.load_json(backups[0])["overrides"]["defaults"]["delivery_mode"], "production")

    def test_nonportable_or_invalid_preferences_are_rejected_before_writes(self) -> None:
        for overrides in ({"defaults": {"hostname": "PRIVATE"}}, {"git_identity": {"human": {"name": "PRIVATE"}}}, {"defaults": {"max_parallel_workers": True}}, {"skill_profile": []}):
            data = {**self.preferences, "overrides": overrides}
            with self.assertRaises(ValueError):
                validate_preferences(data)
        self.path.write_text(json.dumps({**self.preferences, "secret": "PRIVATE"}))
        with self.assertRaises(ValueError):
            self.apply("--preferences", str(self.path))
        self.assertFalse(self.home.exists())
        self.assertFalse(self.state.exists())

    def test_personal_optional_selection_updates_and_removes_only_that_selection(self) -> None:
        self.preferences["overrides"]["optional_skills"] = ["git-workflow-and-versioning"]
        self.path.write_text(json.dumps(self.preferences))
        self.assertEqual(self.apply("--preferences", str(self.path)), 0)
        skills = self.home / ".cursor/skills"
        optional = skills / "git-workflow-and-versioning"
        unrelated = skills / "unrelated-local-skill"
        unrelated.mkdir()
        (unrelated / "SKILL.md").write_text("User-owned skill")
        self.assertTrue(optional.is_dir())
        config = install.load_json(self.state / "config.json")
        config["custom_preference"] = "preserve"
        (self.state / "config.json").write_text(json.dumps(config))
        self.preferences["overrides"].pop("optional_skills")
        self.path.write_text(json.dumps(self.preferences))
        self.assertEqual(self.apply("--preferences", str(self.path)), 0)
        self.assertTrue(optional.is_dir())
        self.assertEqual(install.load_json(self.state / "config.json")["optional_skills"], ["git-workflow-and-versioning"])
        self.preferences["overrides"]["optional_skills"] = []
        self.path.write_text(json.dumps(self.preferences))
        self.assertEqual(self.apply("--preferences", str(self.path)), 0)
        self.assertFalse(optional.exists())
        self.assertTrue(list((self.state / "backups").rglob("git-workflow-and-versioning/SKILL.md")))
        self.assertEqual((unrelated / "SKILL.md").read_text(), "User-owned skill")
        self.assertEqual(install.load_json(self.state / "config.json")["custom_preference"], "preserve")
        self.assertEqual(self.apply(), 0)
        self.assertTrue(unrelated.exists())

    def test_combined_answer_file_and_personal_delta_preserve_machine_choices(self) -> None:
        self.preferences["overrides"].update({
            "optional_skills": ["git-workflow-and-versioning"],
            "pr_workflows": {"review_method": "sol-loop", "council_round_limit": 3, "t3": False},
        })
        self.path.write_text(json.dumps(self.preferences))
        machine = {key: value for key, value in install.quick_answers(self.home, self.profile, ["codex", "opencode"]).items() if not key.startswith("_")}
        machine.update({"delivery_mode": "prototype", "max_parallel_workers": 1})
        machine.pop("optional_skills")
        answer_path = self.root / "machine-answers.json"
        answer_path.write_text(json.dumps(machine))
        self.assertEqual(install.main([
            "--answers", str(answer_path), "--preferences", str(self.path),
            "--portable-preferences", "--home", str(self.home), "--yes",
        ]), 0)
        config = install.load_json(self.state / "config.json")
        self.assertEqual(config["delivery_mode"], "prototype")
        self.assertEqual(config["max_parallel_workers"], 1)
        self.assertEqual(config["optional_skills"], ["git-workflow-and-versioning"])
        self.assertNotIn("pr_workflows", config)
        self.assertEqual(config["harnesses"], ["codex", "opencode"])
        self.assertEqual(install.load_json(self.state / "preferences.json"), self.preferences)
        with patch.dict(os.environ, {"ASTROBYTE_CONFIG": str(self.state)}):
            resolved = resolve(self.home / ".agents/skills/astrobyte-review", self.root, self.home)
        self.assertEqual(resolved["preferences"]["delivery_mode"], "prototype")
        self.assertEqual(resolved["pr_workflows"]["review_method"], "sol-loop")
        self.assertIn("literal PASS", resolved["review_instructions"])

    def test_personal_delta_can_seed_an_explicit_interview(self) -> None:
        machine = {"harnesses": ["cursor"], "delivery_mode": "prototype"}
        with patch("scripts.install.interactive_answers", return_value=machine) as interview:
            self.assertEqual(install.main([
                "--interview", "--preferences", str(self.path), "--home", str(self.home), "--dry-run",
            ]), 0)
        self.assertEqual(interview.call_args.args[3], self.preferences)
        self.assertFalse(self.state.exists())

    def test_current_machine_optional_choice_overrides_personal_selection(self) -> None:
        self.preferences["overrides"]["optional_skills"] = ["git-workflow-and-versioning"]
        answers = install.resolve_install_answers(
            self.home, self.profile, ["cursor"], self.preferences,
            {"harnesses": ["cursor"], "optional_skills": []},
        )
        self.assertEqual(answers["optional_skills"], [])

    def test_optional_preferences_are_catalog_checked_before_interview_or_writes(self) -> None:
        for name in ("unknown-optional-skill", "unslop"):
            self.preferences["overrides"]["optional_skills"] = [name]
            self.path.write_text(json.dumps(self.preferences))
            with patch("scripts.install.interactive_answers", side_effect=AssertionError("Unexpected interview")):
                with self.assertRaisesRegex(ValueError, "Unknown optional_skills"):
                    install.main(["--interview", "--preferences", str(self.path), "--home", str(self.home), "--yes"])
        self.assertFalse(self.state.exists())

    def test_catalog_can_opt_an_optional_package_into_portable_preferences(self) -> None:
        self.preferences["overrides"]["optional_skills"] = ["git-workflow-and-versioning"]
        answers = install.quick_answers(self.home, self.profile, ["cursor"], self.preferences)
        answers["portable_preferences"] = True
        catalog = copy.deepcopy(self.catalog)
        catalog["skills"]["git-workflow-and-versioning"]["portable_preferences"] = True
        plan = install.build_plan(answers, self.home, catalog)
        install.apply_plan(answers, plan, self.home, preserve_existing=True)
        path = self.home / ".cursor/skills/git-workflow-and-versioning/references/preferences.json"
        self.assertEqual(install.load_json(path), self.preferences)

    def test_personal_workflow_policy_updates_without_becoming_machine_override(self) -> None:
        self.preferences["overrides"]["pr_workflows"] = {"review_method": "sol-loop", "council_round_limit": 3}
        self.path.write_text(json.dumps(self.preferences))
        self.assertEqual(self.apply("--preferences", str(self.path)), 0)
        self.preferences["overrides"]["pr_workflows"]["council_round_limit"] = 5
        self.path.write_text(json.dumps(self.preferences))
        self.assertEqual(self.apply("--preferences", str(self.path)), 0)
        self.assertNotIn("pr_workflows", install.load_json(self.state / "config.json"))
        with patch.dict(os.environ, {"ASTROBYTE_CONFIG": str(self.state)}):
            resolved = resolve(self.home / ".cursor/skills/astrobyte-review", self.root, self.home)
        self.assertEqual(resolved["pr_workflows"]["council_round_limit"], 5)
        self.assertEqual(resolved["pr_workflow_sources"]["council_round_limit"], "personal-delta")

    def test_invalid_workflow_choices_are_rejected(self) -> None:
        for options in ({"merge": True}, {"models": ["model"]}, {"council_round_limit": True}, {"council_round_limit": 0}, {"council_round_limit": 21}, {"t3": "yes"}, {"review_method": "council"}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                validate_preferences({**self.preferences, "overrides": {"pr_workflows": options}})
        for names in (["skill", "skill"], ["../skill"], "skill", [True]):
            with self.subTest(names=names), self.assertRaises(ValueError):
                validate_preferences({**self.preferences, "overrides": {"optional_skills": names}})


if __name__ == "__main__":
    unittest.main()
