from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.portable_profile import REPO_ROOT, generate, resource_contents, validate_resources
from scripts.validate import validate_repository


class PortableProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repo"
        shutil.copytree(REPO_ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__"))

    def test_generation_preserves_baseline_and_is_idempotent(self) -> None:
        generate(self.root)
        self.assertEqual(generate(self.root), 0)
        self.assertEqual(validate_resources(self.root), [])
        baseline = json.loads((self.root / "skills/astrobyte-mode/references/baseline.json").read_text())
        self.assertEqual(baseline["profile"], "full")
        self.assertEqual(baseline["defaults"]["delivery_mode"], "durable")
        source = (self.root / "profiles/astrobyte/working-agreement.md").read_text()
        self.assertTrue((self.root / "skills/astrobyte-mode/references/working-agreement.md").read_text().endswith(source))

    def test_validator_rejects_missing_resources_and_source_drift(self) -> None:
        generate(self.root)
        target = self.root / "skills/astrobyte-review/references/review-policy.json"
        target.unlink()
        self.assertTrue(any("missing or unreadable generated resource" in error for error in validate_repository(self.root)))
        generate(self.root)
        agreement = self.root / "profiles/astrobyte/working-agreement.md"
        agreement.write_text(agreement.read_text().replace("Use one reviewer.", "Use one independent reviewer."))
        self.assertTrue(any("stale generated resource" in error for error in validate_repository(self.root)))
        generate(self.root)
        self.assertEqual(validate_repository(self.root), [])

    def test_machine_and_publication_fields_are_not_exported(self) -> None:
        path = self.root / "profiles/astrobyte/profile.json"
        profile = json.loads(path.read_text())
        profile["git_identity"]["human"] = {"name": "PRIVATE_SENTINEL", "email": "private@example.com"}
        profile["git_identity"]["agents"]["codex"]["endpoint"] = "PRIVATE_SENTINEL"
        profile["defaults"]["hostname"] = "PRIVATE_SENTINEL"
        profile["repository"]["credential"] = "PRIVATE_SENTINEL"
        path.write_text(json.dumps(profile))
        contents = "\n".join(resource_contents(self.root).values())
        self.assertNotIn("PRIVATE_SENTINEL", contents)
        self.assertNotIn("private@example.com", contents)
        baseline = json.loads(resource_contents(self.root)[Path("skills/astrobyte-mode/references/baseline.json")])
        self.assertNotIn("machine_delivery_policy", baseline["defaults"])
        self.assertNotIn("browser_automation", baseline["defaults"])
        self.assertNotIn("machine_registry", baseline)
        self.assertNotIn("repository", baseline)

    def test_independent_copies_carry_policies_without_source(self) -> None:
        generate(self.root)
        installed = Path(self.temporary.name) / "installed"
        for skill in ("astrobyte-mode", "astrobyte-review", "astrobyte-git-identity"):
            shutil.copytree(self.root / "skills" / skill, installed / skill)
        shutil.rmtree(self.root)
        baseline = json.loads((installed / "astrobyte-mode/references/baseline.json").read_text())
        review = json.loads((installed / "astrobyte-review/references/review-policy.json").read_text())
        identity = json.loads((installed / "astrobyte-git-identity/references/git-policy.json").read_text())
        self.assertEqual(baseline["baseline"], review["baseline"])
        self.assertEqual(baseline["baseline"], identity["baseline"])
        self.assertIn("newest GPT Sol", review["review"]["instructions"])
        self.assertEqual(identity["git_identity"]["mode"], "dual-attribution")
        self.assertNotIn("human", identity["git_identity"])

    def test_missing_review_section_fails_generation(self) -> None:
        agreement = self.root / "profiles/astrobyte/working-agreement.md"
        agreement.write_text(agreement.read_text().replace("## Review", "## Other review"))
        with self.assertRaisesRegex(ValueError, "exactly one 'Review' section"):
            generate(self.root)


if __name__ == "__main__":
    unittest.main()
