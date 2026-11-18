from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "astrobyte-review"


class ReviewerStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        # A standalone copy proves review works without the optional workflow package.
        self.skill = self.root / "astrobyte-review"
        shutil.copytree(SOURCE, self.skill)
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("ASTROBYTE_")}
        self.env["HOME"] = str(self.root / "home")

    def cli(self, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-I", "-B", str(self.skill / "scripts/reviewer_state.py"), *arguments],
            cwd=self.root, env=self.env, capture_output=True, text=True, check=check,
        )

    def test_unconfigured_harness_reports_first_use(self) -> None:
        result = json.loads(self.cli("show", "--harness", "claude").stdout)
        self.assertEqual(result, {"configured": False, "harness": "claude"})

    def test_saved_selection_round_trips_beside_council_state(self) -> None:
        choice = self.root / "choice.json"
        choice.write_text(json.dumps({"model": "gpt-6.1-sol", "route": "claude -p via gateway"}))
        self.cli("set", "--harness", "claude", "--input", str(choice))
        stored = self.root / "home/.config/astrobyte-agent-skills/pr-workflows/reviewers/claude.json"
        self.assertTrue(stored.is_file())
        shown = json.loads(self.cli("show", "--harness", "claude").stdout)
        self.assertEqual(shown["reviewer"], {"model": "gpt-6.1-sol", "route": "claude -p via gateway"})
        self.assertTrue(shown["configured"])
        self.assertEqual(json.loads(self.cli("show", "--harness", "codex").stdout)["configured"], False)

    def test_invalid_selections_are_rejected_without_writing(self) -> None:
        for value in ({"model": "gpt-6.1-sol"}, {"model": "", "route": "x"}, {"model": "m", "route": "r", "command": "rm -rf /"}):
            choice = self.root / "bad.json"
            choice.write_text(json.dumps(value))
            result = self.cli("set", "--harness", "claude", "--input", str(choice), check=False)
            self.assertEqual(result.returncode, 1, value)
        self.assertFalse((self.root / "home/.config/astrobyte-agent-skills/pr-workflows/reviewers").exists())
        self.assertEqual(self.cli("show", "--harness", "Bad Name", check=False).returncode, 1)


    def test_corrupted_state_is_rejected_and_left_unchanged(self) -> None:
        stored = self.root / "home/.config/astrobyte-agent-skills/pr-workflows/reviewers/claude.json"
        stored.parent.mkdir(parents=True)
        good = {"model": "gpt-6.1-sol", "route": "gateway"}
        for value in (
            {"schema_version": True, "harness": "claude", "reviewer": good},
            {"schema_version": 1, "harness": "claude", "reviewer": good, "configured": False},
            {"schema_version": 1, "harness": "codex", "reviewer": good},
            {"schema_version": 1, "harness": "claude", "reviewer": {"model": "m"}},
        ):
            with self.subTest(value=value):
                stored.write_text(json.dumps(value))
                before = stored.read_bytes()
                self.assertEqual(self.cli("show", "--harness", "claude", check=False).returncode, 1)
                self.assertEqual(stored.read_bytes(), before)

if __name__ == "__main__":
    unittest.main()
