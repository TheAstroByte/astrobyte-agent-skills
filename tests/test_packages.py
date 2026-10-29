from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import install, routing
from scripts.packages import resolve_selection, validate_dependencies, validate_package


class PackageTests(unittest.TestCase):
    def setUp(self) -> None:
        isolation = patch.dict(os.environ)
        isolation.start()
        self.addCleanup(isolation.stop)
        for name in routing.ENVIRONMENT_OVERRIDES:
            os.environ.pop(name, None)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.catalog = install.load_json(install.CATALOG_PATH)

    def test_workflow_closure_and_leaf_independence(self) -> None:
        workflow = resolve_selection(self.catalog, ["astrobyte-mode"])
        self.assertIn("astrobyte-review", workflow)
        self.assertIn("astrobyte-git-identity", workflow)
        self.assertIn("codebase-design", workflow)
        self.assertNotIn("adopt-skill-stack", workflow)
        self.assertNotIn("api-and-interface-design", workflow)
        self.assertNotIn("frontend-design", workflow)
        self.assertNotIn("frontend-ui-engineering", workflow)
        self.assertNotIn("browser-testing-with-devtools", workflow)
        self.assertEqual(resolve_selection(self.catalog, ["diagnosing-bugs"]), ["diagnosing-bugs"])
        self.assertEqual(resolve_selection(self.catalog, ["frontend-design"]), ["frontend-design"])
        self.assertEqual(len(resolve_selection(self.catalog, self.catalog["profiles"]["full"])), 39)

    def test_frontend_profiles_and_copied_license_requirement(self) -> None:
        for profile in ("builder", "full"):
            with self.subTest(profile=profile):
                selected = resolve_selection(self.catalog, self.catalog["profiles"][profile])
                self.assertIn("frontend-design", selected)
                self.assertIn("frontend-ui-engineering", selected)
        self.assertNotIn("frontend-design", resolve_selection(self.catalog, self.catalog["profiles"]["core"]))
        package = self.root / "frontend-design"
        shutil.copytree(install.REPO_ROOT / "skills/frontend-design", package)
        metadata = self.catalog["skills"][package.name]
        self.assertEqual(validate_package(package, metadata), [])
        (package / "LICENSE.txt").unlink()
        self.assertTrue(any("missing resource: LICENSE.txt" in error for error in validate_package(package, metadata)))

    def test_standalone_frontend_install_across_harnesses_and_conflict_backup(self) -> None:
        home, state = self.root / "home", self.root / "state"
        unrelated = home / ".agents/skills/unrelated/SKILL.md"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text("Keep me")
        args = ["--harnesses", ",".join(install.HARNESSES), "--home", str(home),
                "--skills", "frontend-design", "--yes"]
        with patch.dict(os.environ, {"ASTROBYTE_CONFIG_HOME": str(state)}), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(install.main(args), 0)
            groups = install.destination_groups(list(install.HARNESSES), home)
            self.assertEqual(len(groups), 4)
            self.assertEqual(groups[home / ".agents/skills"], ["codex", "opencode"])
            for destination in groups:
                with self.subTest(destination=destination.relative_to(home)):
                    package = destination / "frontend-design"
                    for name in ("SKILL.md", "LICENSE.txt"):
                        self.assertEqual((package / name).read_bytes(),
                                         (install.REPO_ROOT / "skills/frontend-design" / name).read_bytes())
                    self.assertFalse((destination / "astrobyte-mode").exists())
            config = install.load_json(state / "config.json")
            config["custom_preference"] = "keep"
            install.atomic_json_write(state / "config.json", config)
            edited = home / ".agents/skills/frontend-design/SKILL.md"
            edited.write_text(edited.read_text() + "\nLocal design guidance\n")
            self.assertEqual(install.main(args), 0)
            backups = list((state / "backups").rglob("frontend-design/SKILL.md"))
            self.assertEqual(len(backups), 1)
            self.assertIn("Local design guidance", backups[0].read_text())
            self.assertEqual(edited.read_bytes(), (install.REPO_ROOT / "skills/frontend-design/SKILL.md").read_bytes())
            self.assertEqual(install.load_json(state / "config.json")["custom_preference"], "keep")
            self.assertEqual(unrelated.read_text(), "Keep me")
            self.assertEqual(install.check_install(home), 0)
            self.assertEqual(install.main(args), 0)
            self.assertEqual(len(list((state / "backups").rglob("frontend-design/SKILL.md"))), 1)

    def test_unknown_cycle_and_incomplete_profile_are_errors(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown"):
            resolve_selection(self.catalog, ["missing"])
        catalog = copy.deepcopy(self.catalog)
        catalog["skills"]["unslop"]["dependencies"] = ["astrobyte-mode"]
        self.assertTrue(any("cycle" in error for error in validate_dependencies(catalog)))
        catalog = copy.deepcopy(self.catalog)
        catalog["profiles"]["core"].remove("astrobyte-review")
        self.assertTrue(any("missing hard dependencies" in error for error in validate_dependencies(catalog)))

    def test_all_copied_packages_validate_without_source_context(self) -> None:
        for name, metadata in self.catalog["skills"].items():
            package = self.root / name
            shutil.copytree(install.REPO_ROOT / "skills" / name, package)
            self.assertEqual(validate_package(package, metadata), [], name)
        mode = self.root / "astrobyte-mode"
        (mode / "references/build-and-debug.md").unlink()
        self.assertTrue(any("build-and-debug.md" in error for error in validate_package(mode, self.catalog["skills"][mode.name])))
        (mode / "scripts/preferences.py").unlink()
        self.assertTrue(any("missing resource" in error for error in validate_package(mode, self.catalog["skills"][mode.name])))

    def test_native_installs_carry_applicable_license_notices(self) -> None:
        cases = {
            "full": (["--profile", "full"], {
                "diagnosing-bugs": ["licenses/mattpocock-skills-MIT.txt"],
                "unslop": ["licenses/pstack-MIT.txt"],
                "api-and-interface-design": ["licenses/addyosmani-agent-skills-MIT.txt"],
                "frontend-design": ["skills/frontend-design/LICENSE.txt"],
                "astrobyte-mode": ["LICENSE"],
            }),
            "leaf": (["--skills", "diagnosing-bugs"], {
                "diagnosing-bugs": ["licenses/mattpocock-skills-MIT.txt"],
            }),
            "derived": (["--skills", "astrobyte-review"], {
                "astrobyte-review": ["LICENSE", "licenses/pstack-MIT.txt", "licenses/mattpocock-skills-MIT.txt"],
            }),
            "optional": (["--skills", "astrobyte-pr-workflows"], {
                "astrobyte-pr-workflows": ["LICENSE", "skills/astrobyte-pr-workflows/LICENSE.tstack.txt"],
            }),
        }
        for name, (selection, packages) in cases.items():
            with self.subTest(selection=name):
                home, state = self.root / name / "home", self.root / name / "state"
                args = ["--harnesses", "cursor", "--home", str(home), "--yes", *selection]
                with patch.dict(os.environ, {"ASTROBYTE_CONFIG_HOME": str(state)}), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(install.main(args), 0)
                for skill, licenses in packages.items():
                    notice = home / ".cursor/skills" / skill / "LICENSES.txt"
                    self.assertTrue(notice.is_file(), f"{skill}: installed license notices missing")
                    content = notice.read_text(encoding="utf-8")
                    for license_path in licenses:
                        self.assertIn((install.REPO_ROOT / license_path).read_text(encoding="utf-8").strip(), content)

    def test_reference_resources_cannot_escape_or_disappear(self) -> None:
        package = self.root / "leaf"
        package.mkdir()
        (package / "SKILL.md").write_text("# leaf")
        references = package / "references"
        references.mkdir()
        document = references / "extra.md"
        document.write_text("[missing](absent.md)\n[outside](../../outside.md)")
        (self.root / "outside.md").write_text("source-only")
        errors = validate_package(package, {})
        self.assertTrue(any("escapes package" in error for error in errors))
        self.assertTrue(any("missing resource" in error for error in errors))
        document.write_text("```md\n[template](project/example.md)\n```\n")
        self.assertEqual(validate_package(package, {}), [])
        (references / "alias.md").symlink_to(self.root / "outside.md")
        self.assertTrue(any("symlink escapes" in error for error in validate_package(package, {})))

    def test_explicit_install_subset_preserves_other_skills_and_can_select_profile(self) -> None:
        home, state = self.root / "home", self.root / "state"
        unrelated = home / ".cursor/skills/unrelated/SKILL.md"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text("Keep me")
        args = ["--harnesses", "cursor", "--home", str(home), "--yes"]
        with patch.dict(os.environ, {"ASTROBYTE_CONFIG_HOME": str(state)}), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(install.main([*args, "--skills", "diagnosing-bugs"]), 0)
            self.assertEqual({p.name for p in unrelated.parent.parent.iterdir()}, {"unrelated", "diagnosing-bugs"})
            self.assertEqual(install.main(args), 0)
            self.assertFalse((home / ".cursor/skills/astrobyte-mode").exists())
            self.assertEqual(install.main([*args, "--skills", "astrobyte-mode"]), 0)
            self.assertTrue((home / ".cursor/skills/astrobyte-review/SKILL.md").is_file())
            self.assertFalse((home / ".cursor/skills/api-and-interface-design").exists())
            self.assertEqual(install.main([*args, "--profile", "full"]), 0)
            self.assertTrue((home / ".cursor/skills/api-and-interface-design/SKILL.md").is_file())
            self.assertNotIn("selected_skills", install.load_json(state / "config.json"))
            self.assertEqual(unrelated.read_text(), "Keep me")

    def test_router_reaches_explicit_review_gate_in_native_subset_install(self) -> None:
        home, state = self.root / "home", self.root / "state"
        args = ["--harnesses", "codex", "--home", str(home), "--skills", "astrobyte-mode", "--yes"]
        with patch.dict(os.environ, {"ASTROBYTE_CONFIG_HOME": str(state)}), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(install.main(args), 0)
        router = home / ".agents/skills/astrobyte-mode"
        siblings = re.findall(r"`(\.\./[a-z0-9-]+/SKILL\.md)`", (router / "SKILL.md").read_text(encoding="utf-8"))
        self.assertIn("../astrobyte-review/SKILL.md", siblings)
        self.assertIn("../astrobyte-git-identity/SKILL.md", siblings)
        for sibling in siblings:
            self.assertTrue((router / sibling).is_file(), sibling)
        harnesses = router / "references/harnesses.md"
        self.assertIn("`../../astrobyte-review/references/reviewer-dispatch.md`", harnesses.read_text(encoding="utf-8"))
        self.assertTrue((harnesses.parent / "../../astrobyte-review/references/reviewer-dispatch.md").is_file())

        review = router.parent / "astrobyte-review"
        self.assertIn("allow_implicit_invocation: false", (review / "agents/openai.yaml").read_text(encoding="utf-8"))
        gate = (review / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn('opencode/autoinvoke: "false"', gate)
        dispatch = (review / "references/reviewer-dispatch.md").read_text(encoding="utf-8")
        self.assertIn("Do not propose or select another model", gate)
        self.assertIn("the push or pull request waits", gate)
        self.assertIn("Ask for a first line of exactly `PASS` or `BLOCK`", gate)
        self.assertIn("never infer a verdict from the wording", gate)
        self.assertIn("if the second reply is also unclear, report the gate pending", gate)
        self.assertGreaterEqual(dispatch.count("Otherwise the gate is blocked"), 2)
        self.assertIn("Without either, the gate is blocked", dispatch)
        self.assertIn("`claude -p --model <model> --setting-sources user --tools Read,Grep,Glob --strict-mcp-config --permission-mode plan --output-format json`", dispatch)
        self.assertIn("a fallback model does not satisfy the gate", dispatch)
        self.assertIn("`codex --ask-for-approval never exec --sandbox read-only --model <model>`", dispatch)
        for text in (gate, dispatch):
            self.assertNotIn("usable reviewer", text)
            self.assertNotIn("replacement reviewer", text)

    def test_invalid_subset_is_rejected_before_writes(self) -> None:
        home, state = self.root / "home", self.root / "state"
        with patch.dict(os.environ, {"ASTROBYTE_CONFIG_HOME": str(state)}), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ValueError, "Unknown"):
                install.main(["--harnesses", "cursor", "--home", str(home), "--skills", "missing", "--yes"])
        self.assertFalse(home.exists())
        self.assertFalse(state.exists())


if __name__ == "__main__":
    unittest.main()
