from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import bootstrap, install, routing


class BootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.home = Path(self.tempdir.name).resolve() / "home"
        self.home.mkdir()
        self.state = Path(self.tempdir.name) / "state"
        self.environment = patch.dict(os.environ, {"ASTROBYTE_CONFIG_HOME": str(self.state)})
        self.environment.start()
        for name in routing.ENVIRONMENT_OVERRIDES:
            os.environ.pop(name, None)

    def tearDown(self) -> None:
        self.environment.stop()
        self.tempdir.cleanup()

    def test_shared_destination_is_bootstrapped_once(self) -> None:
        plan = bootstrap.build_bootstrap_plan(["codex", "opencode"], self.home)

        self.assertEqual(len(plan), 2)
        self.assertTrue(all(item["harnesses"] == ["codex", "opencode"] for item in plan))
        self.assertEqual({item["skill"] for item in plan}, set(bootstrap.ENTRY_SKILLS))

    def test_bootstrap_backs_up_conflicting_entry_skill(self) -> None:
        target = self.home / ".agents" / "skills" / "adopt-skill-stack"
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text("local edit\n", encoding="utf-8")

        plan = bootstrap.build_bootstrap_plan(["codex"], self.home)
        backups = bootstrap.apply_bootstrap_plan(plan, self.home)

        self.assertTrue(backups)
        self.assertIn("name: adopt-skill-stack", (target / "SKILL.md").read_text(encoding="utf-8"))
        adopted_backup = next(path for path in backups if path.name == "adopt-skill-stack")
        self.assertEqual((adopted_backup / "SKILL.md").read_text(encoding="utf-8"), "local edit\n")

    def test_unknown_harness_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown harnesses"):
            bootstrap.parse_harnesses("codex,mystery")

    def test_bootstrap_is_checkable_and_shared_owners_can_uninstall(self) -> None:
        self.assertEqual(bootstrap.main([
            "--harnesses", "codex,opencode", "--home", str(self.home), "--yes",
        ]), 0)
        self.assertEqual(install.check_install(self.home), 0)
        manifest = install.read_manifest(self.home)
        self.assertEqual(len(manifest["targets"]), 2)
        self.assertTrue(all(item["harnesses"] == ["codex", "opencode"]
                            for item in manifest["targets"].values()))
        self.assertEqual(bootstrap.apply_bootstrap_plan(
            bootstrap.build_bootstrap_plan(["codex", "opencode"], self.home), self.home,
        ), [])
        target = self.home / ".agents/skills/adopt-skill-stack"
        self.assertEqual(install.main([
            "--uninstall", "--harnesses", "codex", "--home", str(self.home), "--yes",
        ]), 0)
        self.assertTrue(target.is_dir())
        self.assertEqual(install.read_manifest(self.home)["targets"][str(target)]["harnesses"], ["opencode"])
        self.assertEqual(install.main([
            "--uninstall", "--all", "--home", str(self.home), "--yes",
        ]), 0)
        self.assertFalse(target.exists())
        self.assertEqual(install.read_manifest(self.home)["targets"], {})

    def test_later_adoption_installs_full_default_and_routing(self) -> None:
        bootstrap.main(["--harnesses", "cursor", "--home", str(self.home), "--yes"])
        config = install.load_json(self.state / "config.json")
        self.assertNotIn("selected_skills", config)
        self.assertFalse(install.read_manifest(self.home).get("routing"))
        self.assertEqual(install.main([
            "--harnesses", "cursor", "--home", str(self.home), "--yes",
        ]), 0)
        catalog = install.load_json(install.CATALOG_PATH)
        profile, _, _ = install.load_operator(install.REPO_ROOT)
        installed = {path.name for path in (self.home / ".cursor/skills").iterdir()}
        self.assertEqual(installed, set(catalog["profiles"][profile["skill_profile"]]))
        self.assertEqual(install.read_manifest(self.home)["routing_mode"], "enabled")
        self.assertEqual(install.check_install(self.home), 0)

    def test_bootstrap_preserves_managed_skills_preferences_and_routing(self) -> None:
        preferences = {
            "schema_version": 1,
            "baseline": {"handle": "astrobyte", "repository_version": "0.5.0"},
            "overrides": {"optional_skills": ["git-workflow-and-versioning"]},
        }
        install.atomic_json_write(self.state / "preferences.json", preferences)
        install.main([
            "--harnesses", "cursor", "--skills", "astrobyte-mode", "--home", str(self.home), "--yes",
        ])
        config = install.load_json(self.state / "config.json")
        config.update({"delivery_mode": "prototype", "custom_preference": "keep"})
        install.atomic_json_write(self.state / "config.json", config)
        # Bootstrap must not prune installed optional skills even if the local delta changed.
        preferences["overrides"]["optional_skills"] = []
        install.atomic_json_write(self.state / "preferences.json", preferences)
        prior = install.read_manifest(self.home)
        hashes = {path: install.tree_hash(Path(path)) for path in prior["targets"]}
        unrelated = self.home / ".agents/skills/unrelated/SKILL.md"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text("Unrelated skill\n")

        bootstrap.main(["--harnesses", "codex", "--home", str(self.home), "--yes"])

        current = install.load_json(self.state / "config.json")
        for key in ("profile", "selected_skills", "delivery_mode", "custom_preference"):
            self.assertEqual(current[key], config[key])
        self.assertEqual(current["harnesses"], ["cursor", "codex"])
        self.assertEqual(install.load_json(self.state / "preferences.json"), preferences)
        manifest = install.read_manifest(self.home)
        self.assertEqual(manifest["routing"], prior["routing"])
        self.assertEqual(manifest["routing_mode"], "enabled")
        self.assertTrue(set(prior["targets"]).issubset(manifest["targets"]))
        self.assertEqual(hashes, {path: install.tree_hash(Path(path)) for path in hashes})
        self.assertEqual({path.name for path in unrelated.parent.parent.iterdir()},
                         {*bootstrap.ENTRY_SKILLS, "unrelated"})
        self.assertEqual(unrelated.read_text(), "Unrelated skill\n")
        self.assertEqual(install.check_install(self.home), 0)

    def test_failed_bootstrap_copy_preserves_existing_skill_and_state(self) -> None:
        bootstrap.main(["--harnesses", "cursor", "--home", str(self.home), "--yes"])
        target = self.home / ".cursor/skills/adopt-skill-stack/SKILL.md"
        target.write_text("Local edit\n")
        state = {path.name: path.read_bytes() for path in self.state.iterdir() if path.is_file()}
        plan = bootstrap.build_bootstrap_plan(["cursor"], self.home)
        copytree = shutil.copytree

        def fail_entry_copy(source: Path, destination: Path, *args: object, **kwargs: object) -> object:
            if Path(source).name == "adopt-skill-stack":
                Path(destination).mkdir()
                (Path(destination) / "partial").write_text("Incomplete\n")
                raise OSError("Injected bootstrap copy failure")
            return copytree(source, destination, *args, **kwargs)

        with patch("scripts.install.shutil.copytree", side_effect=fail_entry_copy):
            with self.assertRaisesRegex(OSError, "Injected bootstrap copy failure"):
                bootstrap.apply_bootstrap_plan(plan, self.home)
        self.assertEqual(target.read_text(), "Local edit\n")
        self.assertEqual(state, {path.name: path.read_bytes() for path in self.state.iterdir() if path.is_file()})
        self.assertFalse((target.parent / "partial").exists())

    def test_bootstrap_preview_and_cancellation_write_nothing(self) -> None:
        with patch("builtins.input", side_effect=AssertionError("Unexpected prompt")):
            self.assertEqual(bootstrap.main([
                "--harnesses", "cursor", "--home", str(self.home), "--dry-run",
            ]), 0)
        with patch("scripts.bootstrap.install.ask_bool", return_value=False):
            self.assertEqual(bootstrap.main([
                "--harnesses", "cursor", "--home", str(self.home),
            ]), 0)
        self.assertFalse(self.state.exists())
        self.assertFalse((self.home / ".cursor").exists())


if __name__ == "__main__":
    unittest.main()
