from __future__ import annotations

import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.plugin_packages import MARKETPLACE, REPO_ROOT, build, check, description, write
from scripts.validate import validate_repository

HIDDEN = re.compile(r"(?m)^disable-model-invocation:\s*true\s*$")


def frontmatter(path: Path) -> str:
    return path.read_text(encoding="utf-8")[4:].split("\n---\n", 1)[0]


class PluginPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repo"
        shutil.copytree(REPO_ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        self.catalog = json.loads((self.root / "catalog.json").read_text(encoding="utf-8"))
        self.plugins = REPO_ROOT / "plugins"

    def write_catalog(self) -> None:
        (self.root / "catalog.json").write_text(json.dumps(self.catalog), encoding="utf-8")

    def test_committed_packages_match_the_catalog(self) -> None:
        self.assertEqual(check(REPO_ROOT), [])

    def test_hand_edit_to_a_generated_copy_is_detected(self) -> None:
        skill = self.root / "plugins/astrobyte/skills/unslop/SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nedited\n", encoding="utf-8")
        self.assertTrue(any("unslop/SKILL.md: stale" in error for error in check(self.root)))

    def test_core_shows_only_its_entry_points_and_excludes_moved_skills(self) -> None:
        core = self.plugins / "astrobyte/skills"
        members = {path.name for path in core.iterdir()}
        self.assertEqual(members, set(self.catalog["packages"]["astrobyte"]["skills"]))
        self.assertNotIn("astrobyte-tdd", members)
        self.assertNotIn("diagnosing-bugs", members)
        visible = {name for name in members if not HIDDEN.search(frontmatter(core / name / "SKILL.md"))}
        self.assertEqual(visible, {"astrobyte-mode", "unslop"})

    def test_optional_package_skills_are_model_visible(self) -> None:
        for name in ("technical-writing", "handoff", "blast-radius", "to-questionnaire"):
            canonical = frontmatter(REPO_ROOT / "skills" / name / "SKILL.md")
            self.assertTrue(HIDDEN.search(canonical), name)
        for package in ("astrobyte-web", "astrobyte-writing", "astrobyte-reliability", "astrobyte-continuity"):
            for skill in (self.plugins / package / "skills").iterdir():
                with self.subTest(package=package, skill=skill.name):
                    self.assertFalse(HIDDEN.search(frontmatter(skill / "SKILL.md")))

    def test_trimmed_workflow_copy_keeps_only_council_and_review_loop(self) -> None:
        workflow = self.plugins / "astrobyte/skills/astrobyte-workflows"
        self.assertEqual({p.name for p in (workflow / "references").iterdir()}, {"council.md", "review-loop.md", "t3.md"})
        text = (workflow / "SKILL.md").read_text(encoding="utf-8")
        operations = {line.split("`")[1] for line in text.splitlines() if line.startswith("| `")}
        self.assertEqual(operations, {"review-loop", "council"})
        for removed in ("finish.md", "continuation.md", "pr-feedback.md", "full-stop", "full-send", "modernize", "babysit-pr", "file-pr", "finish command"):
            self.assertNotIn(removed, text)
        self.assertIn("are in the full skill collection", text)
        self.assertTrue((REPO_ROOT / "skills/astrobyte-workflows/references/finish.md").is_file())

    def test_browser_copy_has_no_fetch_and_run_setup(self) -> None:
        copy = (self.plugins / "astrobyte-web/skills/browser-testing-with-devtools/SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("npx", copy)
        self.assertIn("npx", (REPO_ROOT / "skills/browser-testing-with-devtools/SKILL.md").read_text(encoding="utf-8"))

    def test_every_generated_description_fits(self) -> None:
        for skill_md in self.plugins.glob("*/skills/*/SKILL.md"):
            with self.subTest(skill=str(skill_md.relative_to(self.plugins))):
                self.assertLessEqual(len(description(skill_md.read_text(encoding="utf-8"))), 200)

    def test_optional_packages_depend_on_core(self) -> None:
        for package in ("astrobyte-web", "astrobyte-writing", "astrobyte-reliability", "astrobyte-continuity"):
            manifest = json.loads((self.plugins / package / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["dependencies"], ["astrobyte"])
        marketplace = json.loads((REPO_ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual({item["name"] for item in marketplace["plugins"]}, set(self.catalog["packages"]))

    def test_missing_hard_dependency_is_rejected(self) -> None:
        self.catalog["packages"]["astrobyte"]["skills"].remove("codebase-design")
        self.write_catalog()
        errors = build(self.root, Path(self.temporary.name) / "out")
        self.assertTrue(any("astrobyte-architect needs codebase-design" in error for error in errors), errors)

    def test_overlay_that_does_not_match_exactly_once_is_rejected(self) -> None:
        overlays_path = self.root / "plugins/overlays.json"
        overlays = json.loads(overlays_path.read_text(encoding="utf-8"))
        overlays["skills"]["frontend-design"]["SKILL.md"][0]["find"] = "text that is not in the file"
        overlays_path.write_text(json.dumps(overlays), encoding="utf-8")
        output = Path(self.temporary.name) / "out"
        (output / "plugins").mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "matched 0 times"):
            build(self.root, output)

    def test_skill_in_two_packages_is_rejected(self) -> None:
        self.catalog["packages"]["astrobyte-web"]["skills"].append("unslop")
        self.write_catalog()
        errors = build(self.root, Path(self.temporary.name) / "out")
        self.assertTrue(any("unslop is already in astrobyte" in error for error in errors), errors)


    def test_type_swaps_symlinks_and_nested_overlay_files_are_detected(self) -> None:
        skill = self.root / "plugins/astrobyte/skills/unslop"
        (skill / "SKILL.md").unlink()
        (skill / "SKILL.md").mkdir()
        self.assertTrue(any("unslop/SKILL.md: is a dir, expected a file" in e for e in check(self.root)))
        shutil.rmtree(skill / "SKILL.md")
        (skill / "SKILL.md").symlink_to(REPO_ROOT / "plugins/astrobyte/skills/unslop/SKILL.md")
        self.assertTrue(any("unslop/SKILL.md: is a symlink, expected a file" in e for e in check(self.root)))
        (skill / "SKILL.md").unlink()
        shutil.copy2(REPO_ROOT / "plugins/astrobyte/skills/unslop/SKILL.md", skill / "SKILL.md")
        (skill / "overlays.json").write_text("{}", encoding="utf-8")
        self.assertTrue(any("unslop/overlays.json: unexpected" in e for e in check(self.root)))

    def test_removed_package_is_cleaned_up_by_regeneration(self) -> None:
        self.catalog["packages"]["astrobyte-docs"] = self.catalog["packages"].pop("astrobyte-writing")
        self.write_catalog()
        self.assertEqual(write(self.root), [])
        self.assertFalse((self.root / "plugins/astrobyte-writing").exists())
        self.assertTrue((self.root / "plugins/astrobyte-docs/skills/research/SKILL.md").is_file())
        self.assertEqual(check(self.root), [])

    def test_unknown_directory_in_plugins_is_not_deleted(self) -> None:
        stray = self.root / "plugins/notes"
        stray.mkdir()
        (stray / "keep.md").write_text("mine", encoding="utf-8")
        self.assertTrue(any("plugins/notes: not a generated package" in e for e in write(self.root)))
        self.assertEqual((stray / "keep.md").read_text(encoding="utf-8"), "mine")

    def test_missing_overlay_configuration_fails_validation(self) -> None:
        (self.root / "plugins/overlays.json").unlink()
        self.assertTrue(any(error.startswith("plugins:") and "overlays.json" in error for error in validate_repository(self.root)))

    def test_modified_vendored_copy_carries_a_notice(self) -> None:
        copy = (self.plugins / "astrobyte-web/skills/frontend-design/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Modified by Astrobyte", copy)
        self.assertTrue((self.plugins / "astrobyte-web/skills/frontend-design/LICENSE.txt").is_file())
        self.assertNotIn("Modified by Astrobyte", (REPO_ROOT / "skills/frontend-design/SKILL.md").read_text(encoding="utf-8"))

    def test_copies_with_npx_examples_say_not_to_fetch(self) -> None:
        for document in self.plugins.glob("*/skills/**/*.md"):
            text = document.read_text(encoding="utf-8")
            if re.search(r"(?m)\bnpx (?!--no-install)", text):
                with self.subTest(document=str(document.relative_to(self.plugins))):
                    self.assertIn("do not fetch and run missing packages", text)

    def test_marketplace_name_differs_from_core_plugin(self) -> None:
        marketplace = json.loads((REPO_ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(marketplace["name"], MARKETPLACE)
        self.assertNotIn(MARKETPLACE, self.catalog["packages"])

if __name__ == "__main__":
    unittest.main()
