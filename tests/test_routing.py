from __future__ import annotations

import contextlib
import io
import json
import os
import re
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import install, routing


BLOCK_BEGIN = routing.BEGIN_MARKER
BLOCK_END = routing.END_MARKER


class RoutingInstallTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.home = self.root / "home"
        self.home.mkdir()
        self.state = self.root / "state"
        environment = patch.dict(os.environ, {"ASTROBYTE_CONFIG_HOME": str(self.state)})
        environment.start()
        self.addCleanup(environment.stop)
        for name in routing.ENVIRONMENT_OVERRIDES:
            os.environ.pop(name, None)
        self.cursor_rule = self.home / ".cursor/rules/astrobyte-routing.mdc"
        self.claude_rule = self.home / ".claude/rules/astrobyte-routing.md"
        self.codex_agents = self.home / ".codex/AGENTS.md"
        self.opencode_agents = self.home / ".config/opencode/AGENTS.md"
        self.vibe_agents = self.home / ".vibe/AGENTS.md"

    def run_installer(self, *args: str, inputs: list[str] | None = None) -> tuple[int, str]:
        output = io.StringIO()
        prompts = patch("builtins.input", side_effect=inputs if inputs is not None else AssertionError("Unexpected prompt"))
        with contextlib.redirect_stdout(output), prompts:
            code = install.main([*args, "--home", str(self.home)])
        return code, output.getvalue()

    def install(self, harnesses: str, *args: str, skills: str = "astrobyte-mode") -> tuple[int, str]:
        return self.run_installer("--harnesses", harnesses, "--skills", skills, "--yes", *args)

    def manifest(self) -> dict:
        return install.load_json(self.state / "install-manifest.json")

    def check(self) -> tuple[int, str]:
        return self.run_installer("--check")

    def test_fresh_eligible_install_writes_owned_files_and_managed_blocks(self) -> None:
        code, output = self.install("cursor,codex,opencode,claude")
        self.assertEqual(code, 0, output)
        cursor = self.cursor_rule.read_text(encoding="utf-8")
        self.assertTrue(cursor.startswith("---\ndescription:"))
        self.assertIn("alwaysApply: true", cursor)
        self.assertIn(routing.OWNED_MARKER, cursor)
        self.assertIn(routing.OWNED_MARKER, self.claude_rule.read_text(encoding="utf-8"))
        for path in (self.codex_agents, self.opencode_agents):
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith(BLOCK_BEGIN))
            self.assertIn("`astrobyte-review`", text)
        manifest = self.manifest()
        self.assertEqual(manifest["schema_version"], 3)
        self.assertEqual(manifest["routing_mode"], "enabled")
        self.assertEqual(manifest["source"]["path"], str(install.REPO_ROOT))
        self.assertEqual({record["harness"] for record in manifest["routing"].values()}, {"cursor", "codex", "opencode", "claude"})
        self.assertEqual(manifest["routing"][str(self.cursor_rule)]["kind"], "owned-file")
        self.assertEqual(manifest["routing"][str(self.codex_agents)]["kind"], "managed-block")
        self.assertTrue(all(target["source_hash"] for target in manifest["targets"].values()))
        shared = manifest["targets"][str(self.home / ".agents/skills/astrobyte-mode")]
        self.assertEqual(shared["harnesses"], ["codex", "opencode"])
        self.assertEqual(self.check()[0], 0)

    def test_leaf_install_skips_routing_and_reports_why(self) -> None:
        code, output = self.install("cursor", skills="diagnosing-bugs")
        self.assertEqual(code, 0, output)
        self.assertIn("lacks astrobyte-git-identity, astrobyte-mode, astrobyte-review", output)
        self.assertFalse(self.cursor_rule.exists())
        self.assertNotIn("routing_mode", self.manifest())
        code, output = self.install("cursor")
        self.assertEqual(code, 0, output)
        self.assertTrue(self.cursor_rule.exists())

    def test_hermes_stays_skills_only_with_warning(self) -> None:
        code, output = self.install("hermes,cursor")
        self.assertEqual(code, 0, output)
        self.assertIn("Hermes: automatic routing is unavailable", output)
        self.assertEqual({record["harness"] for record in self.manifest()["routing"].values()}, {"cursor"})

    def test_schema_two_install_requires_explicit_routing(self) -> None:
        self.assertEqual(self.install("cursor")[0], 0)
        manifest = self.manifest()
        self.cursor_rule.unlink()
        legacy = {
            "schema_version": 2,
            "repository": manifest["repository"],
            "repository_version": "0.4.0",
            "profile": manifest["profile"],
            "operator_handle": manifest["operator_handle"],
            "targets": {path: {key: value for key, value in record.items() if key != "source_hash"} for path, record in manifest["targets"].items()},
        }
        install.atomic_json_write(self.state / "install-manifest.json", legacy)
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn("source provenance unknown; reinstall to migrate", output)

        code, output = self.install("cursor")
        self.assertEqual(code, 0, output)
        self.assertIn("predates routing", output)
        self.assertFalse(self.cursor_rule.exists())
        self.assertEqual(self.manifest()["routing_mode"], "migration-required")
        self.assertEqual(self.manifest()["schema_version"], 3)
        self.assertIn("routing decision pending", self.check()[1])

        self.assertEqual(self.install("cursor")[0], 0)
        self.assertFalse(self.cursor_rule.exists())
        code, output = self.install("cursor", "--routing")
        self.assertEqual(code, 0, output)
        self.assertTrue(self.cursor_rule.exists())
        self.assertEqual(self.manifest()["routing_mode"], "enabled")

    def test_partial_schema_two_migration_keeps_routing_pending(self) -> None:
        self.assertEqual(self.install("cursor")[0], 0)
        manifest = self.manifest()
        self.cursor_rule.unlink()
        legacy = {
            "schema_version": 2,
            "repository": manifest["repository"],
            "repository_version": "0.4.0",
            "profile": manifest["profile"],
            "operator_handle": manifest["operator_handle"],
            "targets": {path: {key: value for key, value in record.items() if key != "source_hash"} for path, record in manifest["targets"].items()},
        }
        install.atomic_json_write(self.state / "install-manifest.json", legacy)
        code, output = self.install("cursor", skills="diagnosing-bugs")
        self.assertEqual(code, 0, output)
        self.assertRegex(output, r"source provenance unknown for skills kept from an earlier install: .*astrobyte-mode")
        self.assertIn("Installation matches", output)
        self.assertEqual(self.manifest()["routing_mode"], "migration-required")
        code, output = self.install("cursor")
        self.assertEqual(code, 0, output)
        self.assertIn("predates routing", output)
        self.assertFalse(self.cursor_rule.exists())

    def test_check_follows_moved_harness_homes(self) -> None:
        self.assertEqual(self.install("claude,codex")[0], 0)
        self.assertEqual(self.check()[0], 0)
        os.environ["CODEX_HOME"] = str(self.root / "codex-home")
        os.environ["CLAUDE_CONFIG_DIR"] = str(self.root / "claude-config")
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn(f"routing not at the active codex location: {self.root / 'codex-home/AGENTS.md'}", output)
        self.assertIn(f"routing not at the active claude location: {self.root / 'claude-config/rules/astrobyte-routing.md'}", output)
        self.assertIn(f"skills not at the active claude location: {self.root / 'claude-config/skills'}", output)

    def test_skills_only_records_opt_out_until_routing_is_requested(self) -> None:
        self.assertEqual(self.install("cursor", "--skills-only")[0], 0)
        self.assertFalse(self.cursor_rule.exists())
        self.assertEqual(self.manifest()["routing_mode"], "disabled")
        self.assertEqual(self.install("cursor")[0], 0)
        self.assertFalse(self.cursor_rule.exists())
        self.assertEqual(self.install("cursor", "--routing")[0], 0)
        self.assertTrue(self.cursor_rule.exists())
        self.assertEqual(self.install("cursor", "--skills-only")[0], 0)
        self.assertTrue(self.cursor_rule.exists())
        self.assertEqual(self.manifest()["routing_mode"], "enabled")

    def test_environment_overrides_move_skill_and_instruction_roots(self) -> None:
        os.environ["CLAUDE_CONFIG_DIR"] = str(self.root / "claude-config")
        os.environ["CODEX_HOME"] = str(self.root / "codex-home")
        os.environ["XDG_CONFIG_HOME"] = str(self.root / "xdg")
        code, output = self.install("claude,codex,opencode")
        self.assertEqual(code, 0, output)
        self.assertTrue((self.root / "claude-config/skills/astrobyte-mode/SKILL.md").is_file())
        self.assertTrue((self.root / "claude-config/rules/astrobyte-routing.md").is_file())
        self.assertTrue((self.root / "codex-home/AGENTS.md").is_file())
        self.assertTrue((self.root / "xdg/opencode/AGENTS.md").is_file())
        for path in (self.home / ".claude", self.home / ".codex", self.home / ".config/opencode"):
            self.assertFalse(path.exists(), path)
        self.assertEqual(self.check()[0], 0)

    def test_mistral_vibe_gets_managed_block_and_shares_agents_skills(self) -> None:
        code, output = self.install("mistral-vibe,codex")
        self.assertEqual(code, 0, output)
        text = self.vibe_agents.read_text(encoding="utf-8")
        self.assertTrue(text.startswith(BLOCK_BEGIN))
        self.assertIn("`astrobyte-review`", text)
        manifest = self.manifest()
        record = manifest["routing"][str(self.vibe_agents)]
        self.assertEqual(record["harness"], "mistral-vibe")
        self.assertEqual(record["kind"], "managed-block")
        shared = manifest["targets"][str(self.home / ".agents/skills/astrobyte-mode")]
        self.assertEqual(shared["harnesses"], ["mistral-vibe", "codex"])
        self.assertEqual(self.check()[0], 0)

    def test_vibe_home_override_moves_routing_but_not_skills(self) -> None:
        os.environ["VIBE_HOME"] = str(self.root / "vibe-home")
        code, output = self.install("mistral-vibe")
        self.assertEqual(code, 0, output)
        override_agents = self.root / "vibe-home/AGENTS.md"
        self.assertTrue(override_agents.is_file())
        self.assertFalse(self.vibe_agents.exists())
        self.assertTrue((self.home / ".agents/skills/astrobyte-mode/SKILL.md").is_file())
        self.assertIn(str(override_agents), self.manifest()["routing"])
        self.assertEqual(self.check()[0], 0)

    def test_mistral_vibe_uninstall_releases_shared_copy_only_when_last_owner_leaves(self) -> None:
        self.assertEqual(self.install("mistral-vibe,opencode")[0], 0)
        shared = self.home / ".agents/skills/astrobyte-mode"
        code, output = self.run_installer("--uninstall", "--harnesses", "mistral-vibe", "--yes")
        self.assertEqual(code, 0, output)
        self.assertTrue(shared.is_dir())
        self.assertEqual(self.manifest()["targets"][str(shared)]["harnesses"], ["opencode"])
        self.assertFalse(self.vibe_agents.exists())
        self.assertTrue(self.opencode_agents.exists())
        self.assertEqual(self.check()[0], 0)

    def test_codex_override_shadow_is_reported_and_not_success(self) -> None:
        override = self.home / ".codex/AGENTS.override.md"
        override.parent.mkdir(parents=True)
        override.write_text("Temporary rules\n", encoding="utf-8")
        code, output = self.install("codex")
        self.assertEqual(code, 1)
        self.assertIn(f"inactive: shadowed by {override}", output)
        self.assertIn("inactive: shadowed:", output)
        override.write_text("  \n", encoding="utf-8")
        self.assertEqual(self.check()[0], 0)

    def test_opencode_fallback_loss_requires_explicit_approval(self) -> None:
        fallback = self.home / ".claude/CLAUDE.md"
        fallback.parent.mkdir(parents=True)
        fallback.write_text("Personal Claude rules\n", encoding="utf-8")
        code, output = self.install("opencode")
        self.assertEqual(code, 1)
        self.assertIn("OpenCode then stops reading", output)
        self.assertFalse((self.home / ".agents").exists())
        self.assertFalse(self.state.exists())

        code, output = self.run_installer("--harnesses", "opencode", "--skills", "astrobyte-mode", inputs=["y", "n"])
        self.assertEqual(code, 0, output)
        self.assertFalse(self.opencode_agents.exists())
        self.assertEqual(self.manifest()["routing_declined"], ["opencode"])

        code, output = self.install("opencode", "--routing")
        self.assertEqual(code, 0, output)
        self.assertTrue(self.opencode_agents.exists())
        self.assertEqual(self.manifest()["routing_declined"], [])

    def test_disabled_opencode_claude_prompt_needs_no_fallback_approval(self) -> None:
        fallback = self.home / ".claude/CLAUDE.md"
        fallback.parent.mkdir(parents=True)
        fallback.write_text("Personal Claude rules\n", encoding="utf-8")
        os.environ["OPENCODE_DISABLE_CLAUDE_CODE_PROMPT"] = "1"
        code, output = self.install("opencode")
        self.assertEqual(code, 0, output)
        self.assertTrue(self.opencode_agents.exists())

    def test_symlinked_target_is_refused_before_any_write(self) -> None:
        real = self.root / "dotfiles-agents.md"
        real.write_text("Shared rules\n", encoding="utf-8")
        self.codex_agents.parent.mkdir(parents=True)
        self.codex_agents.symlink_to(real)
        code, output = self.install("codex")
        self.assertEqual(code, 1)
        self.assertIn("symbolic link", output)
        self.assertTrue(self.codex_agents.is_symlink())
        self.assertEqual(real.read_text(encoding="utf-8"), "Shared rules\n")
        self.assertFalse((self.home / ".agents").exists())

    def test_managed_block_preserves_bom_newlines_final_newline_and_mode(self) -> None:
        original = b"\xef\xbb\xbf# Mine\r\nKeep this."
        self.codex_agents.parent.mkdir(parents=True)
        self.codex_agents.write_bytes(original)
        os.chmod(self.codex_agents, 0o600)
        self.assertEqual(self.install("codex")[0], 0)
        data = self.codex_agents.read_bytes()
        self.assertTrue(data.startswith(b"\xef\xbb\xbf# Mine\r\nKeep this.\r\n\r\n" + BLOCK_BEGIN.encode()))
        self.assertIsNone(re.search(rb"(?<!\r)\n", data))
        self.assertFalse(data.endswith(b"\n"))
        self.assertEqual(stat.S_IMODE(self.codex_agents.stat().st_mode), 0o600)
        code, output = self.run_installer("--remove-routing", "--harnesses", "codex", "--yes")
        self.assertEqual(code, 0, output)
        self.assertEqual(self.codex_agents.read_bytes(), original)
        self.assertEqual(stat.S_IMODE(self.codex_agents.stat().st_mode), 0o600)

    def test_malformed_markers_fail_closed(self) -> None:
        block = f"{BLOCK_BEGIN}\nbody\n{BLOCK_END}\n"
        cases = {
            "duplicate": block + block,
            "nested": f"{BLOCK_BEGIN}\n{block}{BLOCK_END}\n",
            "unclosed": f"{BLOCK_BEGIN}\nbody\n",
            "fenced": f"```\n{block}```\n",
            "orphan end": f"{BLOCK_END}\n",
            "unknown": "<!-- astrobyte-routing:begin -->\n",
            "newer schema": f"<!-- astrobyte-routing:begin schema=2 -->\nbody\n{BLOCK_END}\n",
            "unknown kind": "<!-- astrobyte-routing:mystery -->\n",
            "owned marker in shared file": f"{routing.OWNED_MARKER}\n",
        }
        self.codex_agents.parent.mkdir(parents=True)
        for name, content in cases.items():
            with self.subTest(name=name):
                self.codex_agents.write_text(content, encoding="utf-8")
                code, output = self.install("codex")
                self.assertEqual(code, 1)
                self.assertIn("Routing error", output)
                self.assertEqual(self.codex_agents.read_text(encoding="utf-8"), content)
                self.assertFalse((self.home / ".agents").exists())

    def test_unsupported_owned_markers_fail_closed(self) -> None:
        self.cursor_rule.parent.mkdir(parents=True)
        for name, content in {
            "newer schema": "<!-- astrobyte-routing: owned schema=2 -->\nFuture routing\n",
            "duplicate": f"{routing.OWNED_MARKER}\n{routing.OWNED_MARKER}\n",
            "block marker": f"{BLOCK_BEGIN}\nbody\n{BLOCK_END}\n",
            "fenced": f"Example:\n```\n{routing.OWNED_MARKER}\n```\n",
        }.items():
            with self.subTest(name=name):
                self.cursor_rule.write_text(content, encoding="utf-8")
                code, output = self.install("cursor", "--routing")
                self.assertEqual(code, 1)
                self.assertIn("Routing error", output)
                self.assertEqual(self.cursor_rule.read_text(encoding="utf-8"), content)
                self.assertFalse((self.home / ".cursor/skills").exists())

    def test_repeated_install_and_enable_disable_cycles_are_idempotent(self) -> None:
        original = "# Mine\n\nUnrelated rule.\n"
        self.codex_agents.parent.mkdir(parents=True)
        self.codex_agents.write_text(original, encoding="utf-8")
        self.assertEqual(self.install("codex,cursor")[0], 0)
        installed = (self.codex_agents.read_bytes(), self.cursor_rule.read_bytes())
        code, output = self.install("codex,cursor")
        self.assertEqual(code, 0, output)
        self.assertIn(f"same: {self.codex_agents}", output)
        self.assertEqual((self.codex_agents.read_bytes(), self.cursor_rule.read_bytes()), installed)
        for _ in range(2):
            self.assertEqual(self.run_installer("--remove-routing", "--yes")[0], 0)
            self.assertEqual(self.codex_agents.read_text(encoding="utf-8"), original)
            self.assertFalse(self.cursor_rule.exists())
            self.assertEqual(self.manifest()["routing_mode"], "disabled")
            self.assertEqual(self.install("codex,cursor")[0], 0)
            self.assertFalse(self.cursor_rule.exists())
            self.assertEqual(self.install("codex,cursor", "--routing")[0], 0)
            self.assertEqual((self.codex_agents.read_bytes(), self.cursor_rule.read_bytes()), installed)

    def test_harness_removal_is_remembered_until_routing_is_requested(self) -> None:
        self.assertEqual(self.install("cursor,codex")[0], 0)
        code, output = self.run_installer("--remove-routing", "--harnesses", "cursor", "--yes")
        self.assertEqual(code, 0, output)
        self.assertFalse(self.cursor_rule.exists())
        self.assertTrue(self.codex_agents.exists())
        self.assertTrue((self.home / ".cursor/skills/astrobyte-mode").is_dir())
        code, output = self.install("cursor,codex")
        self.assertEqual(code, 0, output)
        self.assertIn("routing for cursor was removed", output)
        self.assertFalse(self.cursor_rule.exists())
        self.assertEqual(self.install("cursor,codex", "--routing")[0], 0)
        self.assertTrue(self.cursor_rule.exists())

    def test_deselected_harness_routing_is_preserved(self) -> None:
        self.assertEqual(self.install("cursor,codex")[0], 0)
        answers = {key: value for key, value in install.load_json(self.state / "config.json").items() if key != "git_identity"}
        answers.update({"harnesses": ["cursor"], "primary_harness": "cursor"})
        answers_path = self.root / "answers.json"
        answers_path.write_text(json.dumps(answers), encoding="utf-8")
        code, output = self.run_installer("--answers", str(answers_path), "--yes")
        self.assertEqual(code, 0, output)
        self.assertIn(f"preserved: {self.codex_agents}", output)
        self.assertIn(BLOCK_BEGIN, self.codex_agents.read_text(encoding="utf-8"))
        self.assertIn(str(self.codex_agents), self.manifest()["routing"])

    def test_hand_written_cursor_rule_is_adopted_only_with_approval(self) -> None:
        self.cursor_rule.parent.mkdir(parents=True)
        self.cursor_rule.write_text("---\nalwaysApply: true\n---\nHand-written routing\n", encoding="utf-8")
        code, output = self.install("cursor")
        self.assertEqual(code, 1)
        self.assertIn("Routing needs explicit approval", output)
        self.assertIn("+" + routing.OWNED_MARKER, output)
        self.assertIn("Hand-written routing", self.cursor_rule.read_text(encoding="utf-8"))
        self.assertFalse((self.home / ".cursor/skills").exists())
        code, output = self.install("cursor", "--routing")
        self.assertEqual(code, 0, output)
        self.assertIn(routing.OWNED_MARKER, self.cursor_rule.read_text(encoding="utf-8"))
        backups = list((self.state / "backups").rglob("astrobyte-routing.mdc"))
        self.assertEqual(len(backups), 1)
        self.assertIn("Hand-written routing", backups[0].read_text(encoding="utf-8"))

    def test_edited_owned_rule_is_reported_and_kept_on_unattended_removal(self) -> None:
        self.assertEqual(self.install("cursor")[0], 0)
        self.cursor_rule.write_text(self.cursor_rule.read_text(encoding="utf-8") + "Local edit\n", encoding="utf-8")
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn(f"routing drifted: {self.cursor_rule}", output)
        code, output = self.run_installer("--remove-routing", "--harnesses", "cursor", "--yes")
        self.assertEqual(code, 1)
        self.assertIn("Local edit", self.cursor_rule.read_text(encoding="utf-8"))
        code, output = self.run_installer("--remove-routing", "--harnesses", "cursor", inputs=["y", "y"])
        self.assertEqual(code, 0, output)
        self.assertFalse(self.cursor_rule.exists())

    def test_shared_skill_directory_is_reference_counted_on_uninstall(self) -> None:
        self.assertEqual(self.install("codex,opencode")[0], 0)
        shared = self.home / ".agents/skills/astrobyte-mode"
        code, output = self.run_installer("--uninstall", "--harnesses", "codex", "--yes")
        self.assertEqual(code, 0, output)
        self.assertTrue(shared.is_dir())
        self.assertEqual(self.manifest()["targets"][str(shared)]["harnesses"], ["opencode"])
        self.assertFalse(self.codex_agents.exists())
        self.assertTrue(self.opencode_agents.exists())
        self.assertNotIn("codex", install.load_json(self.state / "config.json")["harnesses"])
        self.assertEqual(self.check()[0], 0)
        code, output = self.run_installer("--uninstall", "--harnesses", "opencode", "--yes")
        self.assertEqual(code, 0, output)
        self.assertFalse(shared.exists())
        self.assertFalse(self.opencode_agents.exists())
        self.assertEqual(self.manifest()["targets"], {})
        self.assertTrue(list((self.state / "backups").rglob("astrobyte-mode")))

    def test_complete_uninstall_then_guarded_state_purge(self) -> None:
        self.assertEqual(self.install("cursor,claude")[0], 0)
        code, output = self.run_installer("--purge-state", "--yes")
        self.assertEqual(code, 1)
        self.assertIn("--uninstall --all first", output)
        code, output = self.run_installer("--uninstall", "--all", "--dry-run")
        self.assertEqual(code, 0)
        self.assertTrue(self.cursor_rule.exists())
        code, output = self.run_installer("--uninstall", "--all", "--yes")
        self.assertEqual(code, 0, output)
        self.assertFalse((self.home / ".cursor/skills/astrobyte-mode").exists())
        self.assertFalse((self.home / ".claude/skills/astrobyte-mode").exists())
        self.assertFalse(self.cursor_rule.exists())
        self.assertFalse(self.claude_rule.exists())
        self.assertTrue((self.state / "config.json").exists())
        manifest = self.manifest()
        self.assertEqual((manifest["targets"], manifest["routing"]), ({}, {}))
        self.assertNotIn("routing_mode", manifest)
        self.cursor_rule.parent.mkdir(parents=True, exist_ok=True)
        self.cursor_rule.write_text(f"{routing.OWNED_MARKER}\nRestored by a dotfile sync\n", encoding="utf-8")
        code, output = self.run_installer("--purge-state", "--yes")
        self.assertEqual(code, 1)
        self.assertIn(str(self.cursor_rule), output)
        self.assertTrue((self.state / "config.json").exists())
        self.cursor_rule.unlink()
        code, output = self.run_installer("--purge-state", "--yes")
        self.assertEqual(code, 0, output)
        for name in install.STATE_FILES:
            self.assertFalse((self.state / name).exists(), name)
        self.assertTrue((self.state / "backups").is_dir())

    def test_workspace_root_is_opt_in_and_removable(self) -> None:
        existing = self.root / "workspace"
        existing.mkdir()
        (existing / "AGENTS.md").write_text("Workspace notes\n", encoding="utf-8")
        fresh = self.root / "fresh-workspace"
        fresh.mkdir()
        code, output = self.install("cursor", "--workspace-root", str(existing), "--workspace-root", str(fresh))
        self.assertEqual(code, 0, output)
        self.assertIn(BLOCK_BEGIN, (existing / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertIn(BLOCK_BEGIN, (fresh / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertEqual(self.manifest()["workspace_roots"], [str(existing.resolve()), str(fresh.resolve())])
        self.assertEqual(self.install("cursor")[0], 0)
        self.assertEqual(len(self.manifest()["workspace_roots"]), 2)
        with self.assertRaisesRegex(ValueError, "not a recorded workspace root"):
            self.run_installer("--remove-workspace-root", str(self.root), "--yes")
        code, output = self.run_installer("--remove-workspace-root", str(existing), "--remove-workspace-root", str(fresh), "--yes")
        self.assertEqual(code, 0, output)
        self.assertEqual((existing / "AGENTS.md").read_text(encoding="utf-8"), "Workspace notes\n")
        self.assertFalse((fresh / "AGENTS.md").exists())
        self.assertEqual(self.manifest()["workspace_roots"], [])
        self.assertTrue(self.cursor_rule.exists())

    def test_removing_all_routing_includes_workspace_blocks(self) -> None:
        workspace = self.root / "workspace"
        workspace.mkdir()
        (workspace / "AGENTS.md").write_text("Workspace notes\n", encoding="utf-8")
        self.assertEqual(self.install("cursor", "--workspace-root", str(workspace))[0], 0)
        code, output = self.run_installer("--remove-routing", "--yes")
        self.assertEqual(code, 0, output)
        self.assertEqual((workspace / "AGENTS.md").read_text(encoding="utf-8"), "Workspace notes\n")
        self.assertFalse(self.cursor_rule.exists())
        manifest = self.manifest()
        self.assertEqual((manifest["routing"], manifest["workspace_roots"], manifest["routing_mode"]), ({}, [], "disabled"))

    def test_workspace_block_without_record_blocks_check_and_purge(self) -> None:
        workspace = self.root / "workspace"
        workspace.mkdir()
        self.assertEqual(self.install("cursor", "--workspace-root", str(workspace))[0], 0)
        agents = workspace / "AGENTS.md"
        manifest = self.manifest()
        del manifest["routing"][str(agents.resolve())]
        install.atomic_json_write(self.state / "install-manifest.json", manifest)
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn(f"routing not recorded for workspace root {workspace.resolve()}", output)

        manifest["targets"], manifest["routing"] = {}, {}
        install.atomic_json_write(self.state / "install-manifest.json", manifest)
        code, output = self.run_installer("--purge-state", "--yes")
        self.assertEqual(code, 1)
        self.assertIn(str(agents.resolve()), output)
        self.assertTrue((self.state / "config.json").exists())

        code, output = self.run_installer("--uninstall", "--all", "--yes")
        self.assertEqual(code, 0, output)
        self.assertNotIn(BLOCK_BEGIN, agents.read_text(encoding="utf-8") if agents.exists() else "")
        self.assertEqual(self.manifest()["workspace_roots"], [])

    def test_workspace_root_warns_when_agents_file_is_tracked(self) -> None:
        repository = self.root / "tracked"
        repository.mkdir()
        (repository / "AGENTS.md").write_text("Tracked\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(repository)], check=True)
        subprocess.run(["git", "-C", str(repository), "add", "AGENTS.md"], check=True)
        code, output = self.run_installer("--harnesses", "cursor", "--skills", "astrobyte-mode", "--workspace-root", str(repository), "--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("is tracked by Git", output)
        self.assertEqual((repository / "AGENTS.md").read_text(encoding="utf-8"), "Tracked\n")

    def test_workspace_root_requires_routing(self) -> None:
        directory = self.root / "workspace"
        directory.mkdir()
        with self.assertRaisesRegex(ValueError, "--workspace-root needs routing"):
            self.install("cursor", "--skills-only", "--workspace-root", str(directory))

    def test_check_reports_checkout_differences_and_offline_recovery(self) -> None:
        self.assertEqual(self.install("cursor")[0], 0)
        manifest = self.manifest()
        target = str(self.home / ".cursor/skills/astrobyte-mode")
        manifest["targets"][target]["source_hash"] = "0" * 64
        manifest["source"] = {"path": str(self.root / "missing-checkout"), "url": None, "version": "0.5.0", "commit": "abc123"}
        install.atomic_json_write(self.state / "install-manifest.json", manifest)
        no_network = AssertionError("check must not run subprocesses")
        with patch("scripts.install.subprocess.run", side_effect=no_network), patch("scripts.routing.subprocess.run", side_effect=no_network):
            code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn("differs from this checkout: astrobyte-mode", output)
        self.assertIn(f"recorded source checkout is missing: {self.root / 'missing-checkout'}", output)
        self.assertIn(f"git clone {install.canonical_source_url()} <destination>", output)
        self.assertIn("git -C <destination> checkout abc123", output)

    def test_check_rediscovers_unrecorded_markers(self) -> None:
        self.assertEqual(self.install("cursor")[0], 0)
        manifest = self.manifest()
        manifest["routing"] = {}
        install.atomic_json_write(self.state / "install-manifest.json", manifest)
        code, output = self.check()
        self.assertEqual(code, 0)
        self.assertIn(f"unrecorded routing marker: {self.cursor_rule}", output)
        code, output = self.run_installer("--remove-routing", "--harnesses", "cursor", "--yes")
        self.assertEqual(code, 0, output)
        self.assertFalse(self.cursor_rule.exists())

    def test_operations_reject_installation_flags(self) -> None:
        for args in (
            ["--remove-routing", "--routing"],
            ["--uninstall", "--all", "--skills", "astrobyte-mode"],
            ["--uninstall"],
            ["--uninstall", "--all", "--harnesses", "cursor"],
            ["--all"],
            ["--purge-state", "--harnesses", "cursor"],
        ):
            with self.subTest(args=args), self.assertRaises(ValueError):
                self.run_installer(*args)
        with self.assertRaisesRegex(ValueError, "No installer-managed routing"):
            self.run_installer("--remove-routing", "--harnesses", "hermes", "--yes")


class ManagedBlockTests(unittest.TestCase):
    def test_insert_and_remove_restore_original_text(self) -> None:
        block = routing.render_block("Body\n")
        for original in ("", "A\n", "A", "A\n\n", "# Title\r\n".replace("\r\n", "\n")):
            with self.subTest(original=original):
                inserted = routing.insert_block(original, block, None)
                span = routing.find_block(inserted, Path("AGENTS.md"))
                self.assertIsNotNone(span)
                self.assertEqual(routing.remove_block(inserted, span), original)

    def test_block_in_the_middle_is_replaced_in_place(self) -> None:
        text = f"Top\n{routing.render_block('Old')}\nBottom\n"
        span = routing.find_block(text, Path("AGENTS.md"))
        replaced = routing.insert_block(text, routing.render_block("New"), span)
        self.assertEqual(replaced, f"Top\n{routing.render_block('New')}\nBottom\n")
        self.assertEqual(routing.remove_block(text, span), "Top\nBottom\n")


if __name__ == "__main__":
    unittest.main()
