from __future__ import annotations

import json
import unittest

from scripts.validate import REPO_ROOT


class ProjectStartupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = json.loads((REPO_ROOT / "catalog.json").read_text(encoding="utf-8"))
        defaults_path = (
            REPO_ROOT
            / "skills"
            / "astrobyte-project-startup"
            / "references"
            / "project-defaults.json"
        )
        self.defaults = json.loads(defaults_path.read_text(encoding="utf-8"))

    def test_startup_skill_is_installed_in_every_profile(self) -> None:
        self.assertIn("astrobyte-project-startup", self.catalog["skills"])
        for profile, members in self.catalog["profiles"].items():
            with self.subTest(profile=profile):
                self.assertIn("astrobyte-project-startup", members)

    def test_defaults_encode_the_selected_stack_policy(self) -> None:
        self.assertEqual(self.defaults["schema_version"], 1)
        self.assertEqual(self.defaults["python"]["package_manager"], "uv")
        self.assertEqual(self.defaults["python"]["package_manager_fallback"], "poetry")
        self.assertEqual(self.defaults["api"]["framework"], "fastapi")
        self.assertEqual(self.defaults["javascript"]["package_manager"], "pnpm")
        self.assertEqual(self.defaults["javascript"]["quality_tool"], "biome")
        self.assertEqual(self.defaults["storage"]["dedicated_vector_store"], "qdrant")
        self.assertEqual(self.defaults["storage"]["colocated_vector_store"], "pgvector")
        self.assertTrue(self.defaults["llm"]["openai_compatible_local_endpoints"])
        self.assertEqual(self.defaults["llm"]["adapter_style"], "hand-coded-typed")
        self.assertEqual(
            set(self.defaults["llm"]["excluded_frameworks"]),
            {"langchain", "llamaindex"},
        )
        self.assertEqual(self.defaults["experiments"]["default_tracker"], "mlflow")
        self.assertEqual(self.defaults["llm_observability"]["preferred_when_needed"], "opik")
        self.assertEqual(
            set(self.defaults["experiments"]["exception_only_trackers"]),
            {"wandb", "trackio"},
        )

    def test_router_reaches_startup_when_stack_is_unresolved(self) -> None:
        router = (REPO_ROOT / "skills" / "astrobyte-mode" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("astrobyte-project-startup", router)
        self.assertIn("unresolved", router.lower())


if __name__ == "__main__":
    unittest.main()
