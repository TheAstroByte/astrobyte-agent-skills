from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.package_licenses import REPO_ROOT, generate, validate_licenses
from scripts.packages import validate_package
from scripts.validate import validate_repository


class PackageLicenseTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "repo"
        shutil.copytree(REPO_ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__"))

    def test_stale_notice_is_reported_and_regeneration_is_idempotent(self) -> None:
        notice = self.root / "skills/diagnosing-bugs/LICENSES.txt"
        notice.write_text("stale", encoding="utf-8")
        self.assertTrue(any("diagnosing-bugs/LICENSES.txt: stale" in error for error in validate_repository(self.root)))

        self.assertEqual(generate(self.root), 1)
        self.assertEqual(generate(self.root), 0)
        self.assertEqual(validate_licenses(self.root), [])

    def test_source_license_update_reaches_direct_and_derived_packages(self) -> None:
        source = self.root / "licenses/pstack-MIT.txt"
        source.write_text(source.read_text(encoding="utf-8") + "\nFixture notice update\n", encoding="utf-8")
        unaffected = self.root / "skills/diagnosing-bugs/LICENSES.txt"
        before = unaffected.read_bytes()

        errors = validate_licenses(self.root)
        self.assertTrue(any("skills/unslop/LICENSES.txt: stale" in error for error in errors))
        self.assertTrue(any("skills/astrobyte-review/LICENSES.txt: stale" in error for error in errors))
        generate(self.root)

        for name in ("unslop", "astrobyte-review"):
            self.assertIn("Fixture notice update", (self.root / "skills" / name / "LICENSES.txt").read_text(encoding="utf-8"))
        self.assertEqual(unaffected.read_bytes(), before)

    def test_missing_notice_is_rejected_in_a_standalone_copy(self) -> None:
        package = self.root / "skills/diagnosing-bugs"
        catalog = json.loads((self.root / "catalog.json").read_text(encoding="utf-8"))
        metadata = catalog["skills"][package.name]
        (package / "LICENSES.txt").unlink()

        self.assertTrue(any("missing resource: LICENSES.txt" in error for error in validate_package(package, metadata)))
        self.assertTrue(any("diagnosing-bugs/LICENSES.txt: missing" in error for error in validate_licenses(self.root)))

    def test_unknown_provenance_stops_generation_before_writing(self) -> None:
        catalog_path = self.root / "catalog.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog["skills"]["astrobyte-review"]["derived_from"].append("missing:review")
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        notice = self.root / "skills/unslop/LICENSES.txt"
        notice.write_text("unchanged", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "unknown license source missing"):
            generate(self.root)
        self.assertEqual(notice.read_text(encoding="utf-8"), "unchanged")

    def test_license_paths_cannot_escape_or_overwrite_an_upstream_license(self) -> None:
        catalog_path = self.root / "catalog.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog["sources"]["pstack"]["license_file"] = "../outside.txt"
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        self.assertTrue(any("license_file escapes repository" in error for error in validate_licenses(self.root)))

        shutil.copyfile(REPO_ROOT / "catalog.json", catalog_path)
        package = self.root / "skills/frontend-design"
        original = (package / "LICENSE.txt").read_bytes()
        (package / "LICENSES.txt").unlink()
        (package / "LICENSES.txt").symlink_to("LICENSE.txt")
        with self.assertRaisesRegex(ValueError, "must not be a symlink"):
            generate(self.root)
        self.assertEqual((package / "LICENSE.txt").read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
