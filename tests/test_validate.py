from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.validate import REPO_ROOT, validate_repository


class ValidateTests(unittest.TestCase):
    def test_repository_is_valid(self) -> None:
        self.assertEqual(validate_repository(REPO_ROOT), [])

    def test_optional_skill_in_default_profile_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            shutil.copytree(REPO_ROOT, root, ignore=shutil.ignore_patterns(".git", ".hermes", "__pycache__"))
            catalog_path = root / "catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["profiles"]["full"].append("git-workflow-and-versioning")
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            self.assertTrue(any("optional" in error for error in validate_repository(root)))

    def copy_repository(self, directory: str) -> Path:
        root = Path(directory) / "repo"
        shutil.copytree(REPO_ROOT, root, ignore=shutil.ignore_patterns(".git", ".hermes", "__pycache__"))
        return root

    def test_retired_skill_names_are_rejected_in_packaged_instructions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.copy_repository(directory)
            catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
            for relative, template in (
                ("skills/unslop/SKILL.md", "\nUse the `{}` skill.\n"),
                ("skills/unslop/references/workflow.md", "\n```text\nTest failure -> use {}\n```\n"),
            ):
                document = root / relative
                document.parent.mkdir(parents=True, exist_ok=True)
                original = document.read_text() if document.exists() else "# Workflow\n"
                for retired in catalog["superseded_skills"]:
                    with self.subTest(document=relative, retired=retired):
                        document.write_text(original + template.format(retired))
                        self.assertIn(f"{relative}: retired skill reference: {retired}", validate_repository(root))
                        document.write_text(original + f"\nAn unrelated not-{retired}-replacement identifier.\n")
                        self.assertNotIn(f"{relative}: retired skill reference: {retired}", validate_repository(root))
                document.write_text(original)

    def test_routing_template_rejects_machine_paths_and_versioned_models(self) -> None:
        for content, expected in (
            ("Read ~/.cursor/skills first.", "home-relative path"),
            ("Use $HOME/skills.", "$HOME"),
            ("See .config/astrobyte-agent-skills.", "local Astrobyte config path"),
            ("Open /Users/someone/skills.", "absolute user path"),
            ("Review with gpt-5.6-sol.", "versioned model slug"),
        ):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                root = self.copy_repository(directory)
                template = root / "templates/routing.md"
                template.write_text(template.read_text(encoding="utf-8") + content + "\n", encoding="utf-8")
                self.assertTrue(any(expected in error for error in validate_repository(root)), expected)

    def test_version_fields_must_match(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.copy_repository(directory)
            catalog_path = root / "catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["sources"]["astrobyte"]["version"] = "0.0.1"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            preferences_path = root / "templates/preferences.json"
            preferences = json.loads(preferences_path.read_text(encoding="utf-8"))
            preferences["baseline"]["repository_version"] = "0.0.1"
            preferences_path.write_text(json.dumps(preferences), encoding="utf-8")
            errors = validate_repository(root)
            self.assertIn("catalog sources.astrobyte.version does not match VERSION", errors)
            self.assertIn("templates/preferences.json baseline repository_version does not match VERSION", errors)


if __name__ == "__main__":
    unittest.main()
