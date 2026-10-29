from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import bootstrap


class BootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.home = Path(self.tempdir.name) / "home"
        self.home.mkdir()
        self.state = Path(self.tempdir.name) / "state"
        self.environment = patch.dict(os.environ, {"ASTROBYTE_CONFIG_HOME": str(self.state)})
        self.environment.start()

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


if __name__ == "__main__":
    unittest.main()
