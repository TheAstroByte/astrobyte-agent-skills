from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import install, routing


class InstallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.home = Path(self.tempdir.name) / "home"
        self.home.mkdir()
        self.state = Path(self.tempdir.name) / "state"
        self.environment = patch.dict(os.environ, {"ASTROBYTE_CONFIG_HOME": str(self.state)})
        self.environment.start()
        for name in routing.ENVIRONMENT_OVERRIDES:
            os.environ.pop(name, None)
        self.catalog = install.load_json(install.CATALOG_PATH)
        self.answers = {
            "operator_handle": "astrobyte",
            "machine_alias": "primary-dev",
            "delivery_mode": "durable",
            "production_capable": False,
            "autonomy_preset": "bounded-autonomy",
            "communication_style": "collaborative-challenge",
            "explanation_level": "collaborative",
            "git_identity": {
                "mode": "dual-attribution",
                "human": {"name": "Human Owner", "email": "human@example.com"},
                "trailer_key": "Agent",
                "verify_before_push": True,
                "agents": {
                    "codex": {"name": "Codex", "email": "codex@local.invalid"},
                    "opencode": {"name": "OpenCode", "email": "opencode@local.invalid"},
                },
            },
            "harnesses": ["codex", "opencode"],
            "primary_harness": "codex",
            "profile": "core",
            "model_environment": "mixed",
            "max_parallel_workers": 2,
            "unattended_runs": False,
            "external_actions": "ask",
            "unattended_external_actions": "ask",
            "git_workflow": "branch",
            "issue_tracker": "local",
            "docs_path": "docs",
            "compute": "cpu",
            "experiment_budget": "confirm first",
            "browser_automation": False,
            "containers": False,
            "archive_duplicates": True,
            "archive_superseded": True,
        }

    def tearDown(self) -> None:
        self.environment.stop()
        self.tempdir.cleanup()

    def test_shared_destination_is_deduplicated(self) -> None:
        groups = install.destination_groups(["codex", "opencode"], self.home)
        self.assertEqual(len(groups), 1)
        self.assertEqual(next(iter(groups.values())), ["codex", "opencode"])

    def test_mistral_vibe_shares_the_agents_skills_destination(self) -> None:
        groups = install.destination_groups(["codex", "opencode", "mistral-vibe"], self.home)
        self.assertEqual(len(groups), 1)
        self.assertEqual(next(iter(groups.values())), ["codex", "opencode", "mistral-vibe"])
        self.assertEqual(install.HARNESSES["mistral-vibe"].destination(self.home), self.home / ".agents" / "skills")

    def test_same_install_resolution_supports_one_shared_two_and_five_harnesses(self) -> None:
        profile, _, _ = install.load_operator(install.REPO_ROOT)
        for harnesses, destinations in ((["cursor"], 1), (["codex", "opencode"], 1), (list(install.HARNESSES), 4)):
            with self.subTest(harnesses=harnesses):
                answers = install.validate_answers(install.resolve_install_answers(self.home, profile, harnesses, None), self.catalog)
                self.assertEqual(answers["harnesses"], harnesses)
                self.assertEqual(answers["profile"], profile["skill_profile"])
                self.assertEqual(answers["delivery_mode"], profile["defaults"]["delivery_mode"])
                self.assertEqual(len(install.destination_groups(harnesses, self.home)), destinations)
                self.assertNotIn("pr_workflows", answers)

    def test_default_install_uses_shared_profile_without_interview(self) -> None:
        with patch("scripts.install.git_global_value", side_effect=lambda key: {
            "user.name": "New Owner", "user.email": "new-owner@example.com",
        }[key]), patch("builtins.input", side_effect=AssertionError("Unexpected interview")):
            result = install.main(["--harnesses", "cursor", "--home", str(self.home), "--yes"])
        self.assertEqual(result, 0)
        config = install.load_json(self.state / "config.json")
        baseline, _, directory = install.load_operator(install.REPO_ROOT)
        self.assertEqual(config["profile"], baseline["skill_profile"])
        self.assertEqual(config["delivery_mode"], baseline["defaults"]["delivery_mode"])
        self.assertEqual(config["git_workflow"], baseline["defaults"]["git_workflow"])
        self.assertNotIn("human", config["git_identity"])
        self.assertIsNone(config["machine_alias"])
        self.assertFalse((self.state / "machine-registry.json").exists())
        self.assertFalse((self.state / "working-agreement.md").exists())
        self.assertTrue((self.home / ".cursor/skills/astrobyte-mode/references/working-agreement.md").exists())
        self.assertTrue((self.home / ".cursor/skills/astrobyte-mode/references/frontend.md").is_file())
        for name in ("SKILL.md", "LICENSE.txt"):
            self.assertEqual((self.home / ".cursor/skills/frontend-design" / name).read_bytes(),
                             (install.REPO_ROOT / "skills/frontend-design" / name).read_bytes())
        installed = {path.name for path in (self.home / ".cursor" / "skills").iterdir()}
        self.assertEqual(installed, set(self.catalog["profiles"][baseline["skill_profile"]]))

    def test_quick_install_preserves_existing_preferences_and_managed_skills(self) -> None:
        original = install.validate_answers({**self.answers, "optional_skills": ["git-workflow-and-versioning"]}, self.catalog)
        install.apply_plan(original, install.build_plan(original, self.home, self.catalog), self.home)
        config = install.load_json(self.state / "config.json")
        config.update({"delivery_mode": "prototype", "optional_skills": [], "custom_preference": "keep"})
        install.atomic_json_write(self.state / "config.json", config)
        (self.state / "working-agreement.md").write_text("Personal agreement\n")
        prior_profile = (self.state / "operator-profile.json").read_bytes()
        optional_target = self.home / ".agents" / "skills" / "git-workflow-and-versioning"
        with patch("builtins.input", side_effect=AssertionError("Unexpected interview")):
            self.assertEqual(install.main(["--quick", "--harnesses", "cursor", "--home", str(self.home), "--yes"]), 0)
        current = install.load_json(self.state / "config.json")
        self.assertEqual(current["delivery_mode"], "prototype")
        self.assertEqual(current["profile"], "core")
        self.assertEqual(current["custom_preference"], "keep")
        self.assertEqual(current["git_identity"]["human"], original["git_identity"]["human"])
        self.assertEqual((self.state / "working-agreement.md").read_text(), "Personal agreement\n")
        self.assertEqual((self.state / "operator-profile.json").read_bytes(), prior_profile)
        self.assertTrue(optional_target.is_dir())
        self.assertIn(str(optional_target), install.read_manifest(self.home)["targets"])
        self.assertEqual(install.check_install(self.home), 0)

    def test_quick_install_without_git_identity_does_not_invent_an_author(self) -> None:
        baseline, _, _ = install.load_operator(install.REPO_ROOT)
        with patch("scripts.install.git_global_value", return_value=""):
            answers = install.validate_answers(install.quick_answers(self.home, baseline, ["cursor"]), self.catalog)
        self.assertEqual(answers["git_identity"]["mode"], "dual-attribution")
        self.assertNotIn("human", answers["git_identity"])

    def test_quick_dry_run_has_no_side_effects_or_interview(self) -> None:
        with patch("scripts.install.git_global_value", return_value=""), patch("builtins.input", side_effect=AssertionError("Unexpected interview")):
            self.assertEqual(install.main(["--harnesses", "cursor", "--home", str(self.home), "--dry-run"]), 0)
        self.assertFalse(self.state.exists())
        self.assertFalse((self.home / ".cursor").exists())
        with self.assertRaisesRegex(ValueError, "Unknown harnesses"):
            install.main(["--harnesses", "unknown", "--home", str(self.home), "--yes"])
        self.assertFalse(self.state.exists())

    def test_machine_interview_is_explicit(self) -> None:
        with patch("scripts.install.interactive_answers", return_value=dict(self.answers)) as interview:
            self.assertEqual(install.main(["--interview", "--home", str(self.home), "--dry-run"]), 0)
        interview.assert_called_once()
        self.assertFalse(self.state.exists())

    def test_quick_install_still_requires_plan_confirmation(self) -> None:
        with patch("scripts.install.git_global_value", return_value=""), patch("builtins.input", return_value="n") as question:
            self.assertEqual(install.main(["--quick", "--harnesses", "Cursor,cursor", "--home", str(self.home)]), 0)
        self.assertEqual(question.call_count, 1)
        self.assertFalse(self.state.exists())
        self.assertFalse((self.home / ".cursor").exists())

    def test_install_and_check(self) -> None:
        answers = install.validate_answers(dict(self.answers), self.catalog)
        plan = install.build_plan(answers, self.home, self.catalog)
        self.assertTrue(plan)
        self.assertTrue(all(item["status"] == "new" for item in plan))

        backups = install.apply_plan(answers, plan, self.home)

        self.assertEqual(backups, [])
        self.assertEqual(install.check_install(self.home), 0)
        config = json.loads((self.state / "config.json").read_text(encoding="utf-8"))
        self.assertEqual(config["primary_harness"], "codex")
        self.assertEqual(config["machine_alias"], "primary-dev")
        self.assertEqual(config["delivery_mode"], "durable")
        self.assertEqual(config["git_identity"]["agents"]["codex"]["name"], "Codex")
        self.assertTrue((self.state / "operator-profile.json").exists())
        self.assertTrue((self.state / "working-agreement.md").exists())
        self.assertTrue((self.home / ".agents" / "skills" / "astrobyte-mode" / "SKILL.md").exists())

    def test_divergent_skill_is_backed_up(self) -> None:
        answers = install.validate_answers(dict(self.answers), self.catalog)
        install.apply_plan(answers, install.build_plan(answers, self.home, self.catalog), self.home)
        target = self.home / ".agents" / "skills" / "astrobyte-mode" / "SKILL.md"
        target.write_text(target.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")

        plan = install.build_plan(answers, self.home, self.catalog)
        mode_item = next(item for item in plan if item["skill"] == "astrobyte-mode")
        self.assertEqual(mode_item["status"], "conflict")

        backups = install.apply_plan(answers, plan, self.home)
        self.assertTrue(backups)
        self.assertNotIn("local edit", target.read_text(encoding="utf-8"))
        backed_up_mode = [Path(path) for path in backups if path.endswith("astrobyte-mode")]
        self.assertEqual(len(backed_up_mode), 1)
        self.assertIn("local edit", (backed_up_mode[0] / "SKILL.md").read_text(encoding="utf-8"))

    def prepare_replacement(self):
        answers = install.validate_answers({**self.answers, "selected_skills": ["unslop"]}, self.catalog)
        install.apply_plan(answers, install.build_plan(answers, self.home, self.catalog), self.home)
        target = self.home / ".agents/skills/unslop"
        document = target / "SKILL.md"
        document.write_text(document.read_text(encoding="utf-8") + "\nLocal guidance\n", encoding="utf-8")
        previous_hash = install.tree_hash(target)
        state = {name: (self.state / name).read_bytes() for name in ("config.json", "install-manifest.json")}
        return answers, install.build_plan(answers, self.home, self.catalog), target, previous_hash, state

    def test_partial_copy_failure_preserves_installed_skill_and_state(self) -> None:
        answers, plan, target, previous_hash, state = self.prepare_replacement()

        def partial_copy(source, destination):
            Path(destination).mkdir()
            (Path(destination) / "partial.txt").write_text("incomplete", encoding="utf-8")
            raise OSError("copy failure")

        with patch.object(install.shutil, "copytree", side_effect=partial_copy):
            with self.assertRaisesRegex(OSError, "copy failure"):
                install.apply_plan(answers, plan, self.home)

        self.assertEqual(install.tree_hash(target), previous_hash)
        self.assertEqual(list(target.parent.iterdir()), [target])
        for name, content in state.items():
            self.assertEqual((self.state / name).read_bytes(), content)

    def test_damaged_staging_copy_is_rejected_before_replacement(self) -> None:
        answers, plan, target, previous_hash, _ = self.prepare_replacement()
        copytree = shutil.copytree

        def damaged_copy(source, destination):
            copytree(source, destination)
            (Path(destination) / "LICENSES.txt").unlink()

        with patch.object(install.shutil, "copytree", side_effect=damaged_copy):
            with self.assertRaisesRegex(ValueError, "Staged package hash"):
                install.apply_plan(answers, plan, self.home)

        self.assertEqual(install.tree_hash(target), previous_hash)
        self.assertEqual(list(target.parent.iterdir()), [target])

    def test_failed_promotion_restores_installed_skill_and_state(self) -> None:
        answers, plan, target, previous_hash, state = self.prepare_replacement()
        rename = Path.rename

        def failed_promotion(path, destination):
            if path.name == "package" and Path(destination) == target:
                raise OSError("promotion failure")
            return rename(path, destination)

        with patch.object(Path, "rename", new=failed_promotion):
            with self.assertRaisesRegex(OSError, "promotion failure"):
                install.apply_plan(answers, plan, self.home)

        self.assertEqual(install.tree_hash(target), previous_hash)
        self.assertEqual(list(target.parent.iterdir()), [target])
        for name, content in state.items():
            self.assertEqual((self.state / name).read_bytes(), content)

    def test_failed_restoration_keeps_backup_and_reports_its_path(self) -> None:
        answers, plan, target, previous_hash, state = self.prepare_replacement()
        rename, move = Path.rename, shutil.move

        def failed_promotion(path, destination):
            if path.name == "package" and Path(destination) == target:
                raise OSError("promotion failure")
            return rename(path, destination)

        def failed_restoration(source, destination):
            if Path(destination) == target:
                raise OSError("restoration failure")
            return move(source, destination)

        with patch.object(Path, "rename", new=failed_promotion), patch.object(install.shutil, "move", side_effect=failed_restoration):
            with self.assertRaisesRegex(OSError, "Recovery failed") as caught:
                install.apply_plan(answers, plan, self.home)

        backups = list((self.state / "backups").rglob("unslop/SKILL.md"))
        self.assertEqual(len(backups), 1)
        backup = backups[0].parent
        self.assertEqual(install.tree_hash(backup), previous_hash)
        self.assertIn(str(backup), str(caught.exception))
        for name, content in state.items():
            self.assertEqual((self.state / name).read_bytes(), content)

    def test_primary_harness_must_be_selected(self) -> None:
        invalid = dict(self.answers)
        invalid["primary_harness"] = "hermes"
        with self.assertRaisesRegex(ValueError, "primary_harness"):
            install.validate_answers(invalid, self.catalog)

    def test_answer_file_values_are_strictly_validated(self) -> None:
        invalid = dict(self.answers)
        invalid["unattended_runs"] = "no"
        with self.assertRaisesRegex(ValueError, "unattended_runs must be a boolean"):
            install.validate_answers(invalid, self.catalog)

        invalid = dict(self.answers)
        invalid["external_actions"] = "always"
        with self.assertRaisesRegex(ValueError, "Invalid external_actions"):
            install.validate_answers(invalid, self.catalog)

        invalid = dict(self.answers)
        invalid["unattended_external_actions"] = "always"
        with self.assertRaisesRegex(ValueError, "Invalid unattended_external_actions"):
            install.validate_answers(invalid, self.catalog)

        invalid = dict(self.answers)
        invalid["delivery_mode"] = "ship-it"
        with self.assertRaisesRegex(ValueError, "Invalid delivery_mode"):
            install.validate_answers(invalid, self.catalog)

        invalid = dict(self.answers)
        invalid["git_identity"] = dict(self.answers["git_identity"])
        invalid["git_identity"]["agents"] = {
            "codex": {"name": "Codex", "email": "codex@local.invalid"}
        }
        with self.assertRaisesRegex(ValueError, "missing active harnesses: opencode"):
            install.validate_answers(invalid, self.catalog)

    def test_unattended_policy_can_allow_preconfigured_actions(self) -> None:
        answers = dict(self.answers)
        answers["unattended_runs"] = True
        answers["external_actions"] = "ask"
        answers["unattended_external_actions"] = "allow-configured"

        validated = install.validate_answers(answers, self.catalog)

        self.assertEqual(validated["external_actions"], "ask")
        self.assertEqual(validated["unattended_external_actions"], "allow-configured")

    def test_optional_skill_is_absent_by_default_and_opted_in_only_when_selected(self) -> None:
        name = "git-workflow-and-versioning"
        answers = install.validate_answers(dict(self.answers), self.catalog)
        self.assertEqual(answers["optional_skills"], [])
        self.assertNotIn(name, {item["skill"] for item in install.build_plan(answers, self.home, self.catalog)})

        opted_in = install.validate_answers({**self.answers, "optional_skills": [name]}, self.catalog)
        plan = install.build_plan(opted_in, self.home, self.catalog)
        self.assertEqual([item["skill"] for item in plan].count(name), 1)
        install.apply_plan(opted_in, plan, self.home)
        target = self.home / ".agents" / "skills" / name
        self.assertTrue((target / "SKILL.md").exists())
        self.assertEqual(install.check_install(self.home), 0)
        self.assertEqual(json.loads((self.state / "config.json").read_text())["optional_skills"], [name])

        plan = install.build_plan(answers, self.home, self.catalog)
        self.assertIn(name, {item["skill"] for item in plan if item["status"] == "archive-profile"})
        backups = install.apply_plan(answers, plan, self.home)
        self.assertFalse(target.exists())
        self.assertTrue(any(path.endswith(name) for path in backups))

    def test_optional_skill_conflict_is_backed_up(self) -> None:
        name = "git-workflow-and-versioning"
        target = self.home / ".agents" / "skills" / name
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text("local version\n", encoding="utf-8")
        answers = install.validate_answers({**self.answers, "optional_skills": [name]}, self.catalog)
        plan = install.build_plan(answers, self.home, self.catalog)
        self.assertEqual(next(item for item in plan if item["skill"] == name)["status"], "conflict")
        backups = install.apply_plan(answers, plan, self.home)
        self.assertIn("local version", (next(Path(p) for p in backups if p.endswith(name)) / "SKILL.md").read_text())

    def test_optional_selection_can_be_cleared_interactively(self) -> None:
        name = "git-workflow-and-versioning"
        with patch.object(install, "ask", return_value="-"):
            self.assertEqual(install.ask_optional_skills([name], [name]), [])

    def test_optional_skill_answer_rejects_unknown_duplicates_and_wrong_type(self) -> None:
        for selection in (["unknown"], ["git-workflow-and-versioning"] * 2, "git-workflow-and-versioning"):
            with self.subTest(selection=selection), self.assertRaisesRegex(ValueError, "optional_skills"):
                install.validate_answers({**self.answers, "optional_skills": selection}, self.catalog)

    def test_hermes_only_does_not_archive_shared_agent_skills(self) -> None:
        shared = self.home / ".agents" / "skills" / "astrobyte-mode"
        shared.mkdir(parents=True)
        (shared / "SKILL.md").write_text("shared\n", encoding="utf-8")
        answers = dict(self.answers)
        answers["harnesses"] = ["hermes"]
        answers["primary_harness"] = "hermes"
        answers["git_identity"] = dict(self.answers["git_identity"])
        answers["git_identity"]["agents"] = {
            "hermes": {"name": "Hermes", "email": "hermes@local.invalid"}
        }
        answers = install.validate_answers(answers, self.catalog)

        plan = install.build_plan(answers, self.home, self.catalog)

        self.assertFalse(any(item["target"] == str(shared) for item in plan))

    def test_superseded_skill_is_archived(self) -> None:
        old = self.home / ".codex" / "skills" / "using-agent-skills"
        old.mkdir(parents=True)
        (old / "SKILL.md").write_text("legacy\n", encoding="utf-8")
        answers = install.validate_answers(dict(self.answers), self.catalog)

        plan = install.build_plan(answers, self.home, self.catalog)
        archived = [item for item in plan if item["status"] == "archive-superseded"]
        self.assertEqual([item["skill"] for item in archived], ["using-agent-skills"])

        backups = install.apply_plan(answers, plan, self.home)
        self.assertFalse(old.exists())
        self.assertTrue(any(path.endswith("using-agent-skills") for path in backups))

    def test_profile_downgrade_archives_removed_managed_skills(self) -> None:
        full = dict(self.answers)
        full["profile"] = "full"
        full = install.validate_answers(full, self.catalog)
        install.apply_plan(full, install.build_plan(full, self.home, self.catalog), self.home)

        core = install.validate_answers(dict(self.answers), self.catalog)
        plan = install.build_plan(core, self.home, self.catalog)
        removed = {item["skill"] for item in plan if item["status"] == "archive-profile"}

        self.assertIn("shipping-and-launch", removed)
        install.apply_plan(core, plan, self.home)
        self.assertFalse((self.home / ".agents" / "skills" / "shipping-and-launch").exists())


if __name__ == "__main__":
    unittest.main()
