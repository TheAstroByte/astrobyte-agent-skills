"""Plan, write, check, and remove the always-loaded Astrobyte routing pointer."""

from __future__ import annotations

import difflib
import hashlib
import os
import re
import shutil
import stat
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_RELATIVE = Path("templates") / "routing.md"
TEMPLATE_SCHEMA = 1
ROUTING_HARNESSES = ("cursor", "codex", "opencode", "claude", "mistral-vibe")
REQUIRED_SKILLS = frozenset({"astrobyte-mode", "astrobyte-review", "astrobyte-git-identity"})
ENVIRONMENT_OVERRIDES = (
    "CLAUDE_CONFIG_DIR",
    "CODEX_HOME",
    "VIBE_HOME",
    "XDG_CONFIG_HOME",
    "OPENCODE_DISABLE_CLAUDE_CODE",
    "OPENCODE_DISABLE_CLAUDE_CODE_PROMPT",
)
OWNED_FILE = "owned-file"
MANAGED_BLOCK = "managed-block"

OWNED_MARKER = f"<!-- astrobyte-routing: owned schema={TEMPLATE_SCHEMA} -->"
BEGIN_MARKER = f"<!-- astrobyte-routing:begin schema={TEMPLATE_SCHEMA} -->"
END_MARKER = "<!-- astrobyte-routing:end -->"
MARKER_LIKE = re.compile(r"^\s*<!--\s*astrobyte-routing\b")
FENCE = re.compile(r"^\s*(?:```|~~~)")
CURSOR_FRONTMATTER = (
    "---\n"
    "description: Route substantial work through the installed Astrobyte skills\n"
    "alwaysApply: true\n"
    "---\n"
)
FORBIDDEN_TEMPLATE_CONTENT = (
    (re.compile(r"~/"), "a home-relative path"),
    (re.compile(r"\$HOME\b|\$\{HOME\}"), "$HOME"),
    (re.compile(r"\.config/astrobyte"), "the local Astrobyte config path"),
    (re.compile(r"/Users/|/home/|[A-Za-z]:\\Users\\"), "an absolute user path"),
    (re.compile(r"\bgpt-\d", re.IGNORECASE), "a versioned model slug"),
)


class RoutingError(ValueError):
    """A routing target cannot be changed safely."""


@dataclass(frozen=True)
class Location:
    harness: str
    path: Path
    kind: str


@dataclass(frozen=True)
class TextFile:
    exists: bool
    text: str = ""
    bom: bool = False
    newline: str = "\n"
    mode: int | None = None


def claude_root(home: Path) -> Path:
    override = os.environ.get("CLAUDE_CONFIG_DIR")
    return Path(override).expanduser() if override else home / ".claude"


def codex_home(home: Path) -> Path:
    override = os.environ.get("CODEX_HOME")
    return Path(override).expanduser() if override else home / ".codex"


def xdg_config_home(home: Path) -> Path:
    override = os.environ.get("XDG_CONFIG_HOME")
    return Path(override).expanduser() if override else home / ".config"


def vibe_home(home: Path) -> Path:
    override = os.environ.get("VIBE_HOME")
    return Path(override).expanduser() if override else home / ".vibe"


def harness_location(harness: str, home: Path) -> Location:
    if harness == "cursor":
        return Location(harness, home / ".cursor" / "rules" / "astrobyte-routing.mdc", OWNED_FILE)
    if harness == "claude":
        return Location(harness, claude_root(home) / "rules" / "astrobyte-routing.md", OWNED_FILE)
    if harness == "codex":
        return Location(harness, codex_home(home) / "AGENTS.md", MANAGED_BLOCK)
    if harness == "opencode":
        return Location(harness, xdg_config_home(home) / "opencode" / "AGENTS.md", MANAGED_BLOCK)
    if harness == "mistral-vibe":
        return Location(harness, vibe_home(home) / "AGENTS.md", MANAGED_BLOCK)
    raise RoutingError(f"{harness} has no always-loaded routing location")


def workspace_location(root: Path) -> Location:
    return Location("workspace", root / "AGENTS.md", MANAGED_BLOCK)


def record_location(path: str, record: dict[str, Any]) -> Location:
    return Location(str(record.get("harness")), Path(path), str(record.get("kind")))


def validate_template_text(text: str) -> list[str]:
    errors = [f"routing template contains {label}" for pattern, label in FORBIDDEN_TEMPLATE_CONTENT if pattern.search(text)]
    if not text.strip():
        errors.append("routing template is empty")
    if any(MARKER_LIKE.match(line) for line in text.splitlines()):
        errors.append("routing template contains an ownership marker")
    for skill in sorted(REQUIRED_SKILLS):
        if f"`{skill}`" not in text:
            errors.append(f"routing template does not name `{skill}`")
    return errors


def template_body(root: Path = REPO_ROOT) -> str:
    text = (root / TEMPLATE_RELATIVE).read_text(encoding="utf-8")
    errors = validate_template_text(text)
    if errors:
        raise RoutingError("; ".join(errors))
    return text.strip() + "\n"


def render_owned(harness: str, body: str) -> str:
    header = CURSOR_FRONTMATTER if harness == "cursor" else ""
    return f"{header}{OWNED_MARKER}\n{body}"


def render_block(body: str) -> str:
    return f"{BEGIN_MARKER}\n{body.rstrip(chr(10))}\n{END_MARKER}"


def digest(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def read_text_file(path: Path) -> TextFile:
    if path.is_symlink():
        raise RoutingError(f"{path} is a symbolic link; replace it with a regular file or edit its target by hand")
    if not path.exists():
        return TextFile(False)
    if not path.is_file():
        raise RoutingError(f"{path} is not a regular file")
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    try:
        text = raw[3 if bom else 0:].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RoutingError(f"{path} is not UTF-8 text") from exc
    newline = "\r\n" if "\r\n" in text else "\n"
    return TextFile(True, text.replace("\r\n", "\n"), bom, newline, stat.S_IMODE(path.stat().st_mode))


def write_text_file(path: Path, original: TextFile, text: str) -> None:
    data = (b"\xef\xbb\xbf" if original.bom else b"") + text.replace("\n", original.newline).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
        os.chmod(temporary, original.mode if original.mode is not None else 0o644)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def find_block(text: str, path: Path) -> tuple[int, int] | None:
    """Return the span of the single managed block, failing closed on ambiguity."""
    spans: list[tuple[int, int]] = []
    start: int | None = None
    fenced = False
    offset = 0
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\n")
        if FENCE.match(content):
            fenced = not fenced
        elif MARKER_LIKE.match(content):
            if fenced:
                raise RoutingError(f"{path}: an Astrobyte routing marker is inside a code fence")
            marker = content.strip()
            if marker == BEGIN_MARKER:
                if start is not None:
                    raise RoutingError(f"{path}: nested Astrobyte routing markers")
                start = offset
            elif marker == END_MARKER:
                if start is None:
                    raise RoutingError(f"{path}: an Astrobyte routing end marker has no begin marker")
                spans.append((start, offset + len(content)))
                start = None
            else:
                raise RoutingError(f"{path}: unsupported Astrobyte routing marker: {marker}")
        offset += len(line)
    if start is not None:
        raise RoutingError(f"{path}: an Astrobyte routing begin marker is not closed")
    if len(spans) > 1:
        raise RoutingError(f"{path}: duplicate Astrobyte routing blocks")
    return spans[0] if spans else None


def owned_marker(text: str, path: Path) -> bool:
    """Return whether an owned file carries the current ownership marker, failing closed on any other marker."""
    found = 0
    fenced = False
    for line in text.splitlines():
        if FENCE.match(line):
            fenced = not fenced
            continue
        if not MARKER_LIKE.match(line):
            continue
        if fenced:
            raise RoutingError(f"{path}: an Astrobyte routing marker is inside a code fence")
        marker = line.strip()
        if marker != OWNED_MARKER:
            raise RoutingError(f"{path}: unsupported Astrobyte routing marker: {marker}")
        found += 1
    if found > 1:
        raise RoutingError(f"{path}: duplicate Astrobyte ownership markers")
    return found == 1


def marked_locations(home: Path, records: dict[str, Any], workspace_roots: list[str] = ()) -> tuple[list[Path], list[str]]:
    """Find known harness and workspace locations that carry Astrobyte markers but have no manifest record."""
    marked: list[Path] = []
    unsafe: list[str] = []
    recorded_paths = {Path(path).resolve() for path in records}
    locations = [harness_location(harness, home) for harness in ROUTING_HARNESSES]
    locations += [workspace_location(Path(root)) for root in workspace_roots]
    for location in locations:
        if location.path.resolve() in recorded_paths:
            continue
        try:
            current = read_text_file(location.path)
            if not current.exists:
                continue
            if owned_marker(current.text, location.path) if location.kind == OWNED_FILE else find_block(current.text, location.path):
                marked.append(location.path)
        except RoutingError as exc:
            unsafe.append(str(exc))
    return marked, unsafe


def insert_block(text: str, block: str, span: tuple[int, int] | None) -> str:
    if span is not None:
        return text[: span[0]] + block + text[span[1]:]
    if not text:
        return block + "\n"
    if text.endswith("\n"):
        return text + "\n" + block + "\n"
    return text + "\n\n" + block


def remove_block(text: str, span: tuple[int, int]) -> str:
    before, after = text[: span[0]], text[span[1]:]
    if not after:
        for _ in range(2):
            if before.endswith("\n"):
                before = before[:-1]
    elif after.startswith("\n"):
        after = after[1:]
        if before.endswith("\n\n"):
            before = before[:-1]
    return before + after


def backup_path(backup_root: Path, path: Path) -> Path:
    return backup_root / (Path(*path.parts[1:]) if path.is_absolute() else path)


def unified_diff(path: Path, current: str, proposed: str) -> str:
    return "".join(
        difflib.unified_diff(
            current.splitlines(keepends=True),
            proposed.splitlines(keepends=True),
            fromfile=str(path),
            tofile=f"{path} (Astrobyte routing)",
        )
    )


def codex_shadow(path: Path) -> Path | None:
    override = path.parent / "AGENTS.override.md"
    try:
        if override.is_file() and override.read_text(encoding="utf-8", errors="replace").strip():
            return override
    except OSError:
        return None
    return None


def opencode_fallback_loss(home: Path) -> Path | None:
    if any(os.environ.get(name) for name in ("OPENCODE_DISABLE_CLAUDE_CODE", "OPENCODE_DISABLE_CLAUDE_CODE_PROMPT")):
        return None
    fallback = home / ".claude" / "CLAUDE.md"
    try:
        if fallback.is_file() and fallback.read_text(encoding="utf-8", errors="replace").strip():
            return fallback
    except OSError:
        return None
    return None


def git_tracking_note(root: Path) -> str | None:
    def git(*args: str) -> subprocess.CompletedProcess[str] | None:
        try:
            return subprocess.run(["git", "-C", str(root), *args], check=False, text=True, capture_output=True)
        except OSError:
            return None

    tracked = git("ls-files", "--error-unmatch", "AGENTS.md")
    if tracked is not None and tracked.returncode == 0:
        return f"{root / 'AGENTS.md'} is tracked by Git; the managed block will appear in that repository's diff"
    inside = git("rev-parse", "--is-inside-work-tree")
    if inside is not None and inside.returncode == 0 and inside.stdout.strip() == "true":
        return f"{root} is inside a Git work tree; commit or ignore AGENTS.md deliberately"
    return None


def plan_install(
    home: Path,
    harnesses: list[str],
    workspace_roots: list[Path],
    records: dict[str, Any],
    root: Path = REPO_ROOT,
) -> list[dict[str, Any]]:
    """Describe every routing write without changing files."""
    body = template_body(root)
    locations = [harness_location(name, home) for name in harnesses if name in ROUTING_HARNESSES]
    locations += [workspace_location(path) for path in workspace_roots]
    items: list[dict[str, Any]] = []
    for location in locations:
        record = records.get(str(location.path))
        current = read_text_file(location.path)
        item: dict[str, Any] = {
            "harness": location.harness,
            "path": str(location.path),
            "kind": location.kind,
            "notes": [],
            "approval": None,
            "diff": None,
        }
        if location.kind == OWNED_FILE:
            proposed = render_owned(location.harness, body)
            item["created"] = bool(record.get("created")) if record else not current.exists
            if current.exists:
                owned_marker(current.text, location.path)
            if not current.exists:
                item["status"] = "new"
            elif current.text == proposed:
                item["status"] = "same"
            elif record and digest(current.text) == record.get("hash"):
                item["status"] = "update"
            else:
                item["status"] = "conflict"
                item["approval"] = f"replace {location.path}, which Astrobyte does not own or which was edited; the current file is backed up first"
                item["diff"] = unified_diff(location.path, current.text, proposed)
        else:
            proposed = render_block(body)
            span = find_block(current.text, location.path) if current.exists else None
            item["created"] = bool(record.get("created")) if record else not current.exists
            if not current.exists:
                item["status"] = "new"
            elif span is None:
                item["status"] = "add"
            else:
                existing = current.text[span[0]: span[1]]
                if existing == proposed:
                    item["status"] = "same"
                elif record and digest(existing) != record.get("hash"):
                    item["status"] = "conflict"
                    item["approval"] = f"replace the edited Astrobyte block in {location.path}; the current file is backed up first"
                    item["diff"] = unified_diff(location.path, existing + "\n", proposed + "\n")
                else:
                    item["status"] = "update"
            if location.harness == "codex" and (override := codex_shadow(location.path)):
                item["notes"].append(f"inactive: shadowed by {override}")
            if location.harness == "opencode" and not current.exists and (fallback := opencode_fallback_loss(home)):
                item["approval"] = f"create {location.path}; OpenCode then stops reading {fallback} as global instructions"
            if location.harness == "workspace" and item["status"] in {"new", "add"} and (note := git_tracking_note(location.path.parent)):
                item["notes"].append(note)
        item["proposed"] = proposed
        items.append(item)
    return items


def apply_install(items: list[dict[str, Any]], backup_root: Path) -> tuple[dict[str, Any], list[str]]:
    """Write approved items and return their manifest records and backups."""
    records: dict[str, Any] = {}
    backups: list[str] = []
    for item in items:
        if item["status"] == "declined":
            continue
        path = Path(item["path"])
        current = read_text_file(path)
        if item["status"] != "same":
            if current.exists:
                backup = backup_path(backup_root, path)
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, backup)
                backups.append(str(backup))
            if item["kind"] == OWNED_FILE:
                write_text_file(path, TextFile(False, mode=current.mode), item["proposed"])
            else:
                span = find_block(current.text, path) if current.exists else None
                write_text_file(path, current, insert_block(current.text, item["proposed"], span))
        records[str(path)] = {
            "harness": item["harness"],
            "kind": item["kind"],
            "template_schema": TEMPLATE_SCHEMA,
            "hash": digest(item["proposed"]),
            "marker": OWNED_MARKER if item["kind"] == OWNED_FILE else BEGIN_MARKER,
            "created": bool(item["created"]),
        }
    return records, backups


def plan_remove(locations: list[Location], records: dict[str, Any], root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    """Describe removal of Astrobyte-owned routing at each location."""
    body = template_body(root)
    items: list[dict[str, Any]] = []
    for location in dict.fromkeys(locations):
        record = records.get(str(location.path))
        current = read_text_file(location.path)
        item: dict[str, Any] = {"harness": location.harness, "path": str(location.path), "kind": location.kind, "approval": None, "notes": []}
        if not current.exists:
            item["status"] = "absent"
        elif location.kind == OWNED_FILE:
            matches_record = bool(record) and digest(current.text) == record.get("hash")
            if matches_record or current.text == render_owned(location.harness, body):
                item["status"] = "delete"
            elif owned_marker(current.text, location.path) or record:
                item["status"] = "conflict"
                item["approval"] = f"delete {location.path}, which was edited after installation; it is backed up first"
            else:
                item["status"] = "absent"
                item["notes"].append(f"left in place: {location.path} has no Astrobyte ownership marker")
        else:
            span = find_block(current.text, location.path)
            if span is None:
                item["status"] = "absent"
            else:
                remaining = remove_block(current.text, span)
                created = bool(record.get("created")) if record else False
                item["status"] = "delete" if created and not remaining.strip() else "strip"
        items.append(item)
    return items


def apply_remove(items: list[dict[str, Any]], backup_root: Path, approved: set[str]) -> tuple[list[str], list[str], list[str]]:
    """Remove routing; return removed paths, kept conflict paths, and backups."""
    removed: list[str] = []
    kept: list[str] = []
    backups: list[str] = []
    for item in items:
        path = Path(item["path"])
        status = item["status"]
        if status == "absent":
            removed.append(item["path"])
            continue
        if status == "conflict" and item["path"] not in approved:
            kept.append(item["path"])
            continue
        current = read_text_file(path)
        backup = backup_path(backup_root, path)
        backup.parent.mkdir(parents=True, exist_ok=True)
        if status in {"delete", "conflict"}:
            shutil.move(str(path), str(backup))
        else:
            shutil.copy2(path, backup)
            span = find_block(current.text, path)
            if span is not None:
                write_text_file(path, current, remove_block(current.text, span))
        backups.append(str(backup))
        removed.append(item["path"])
    return removed, kept, backups


def check(home: Path, records: dict[str, Any], workspace_roots: list[str] = (), root: Path = REPO_ROOT) -> tuple[list[str], list[str]]:
    """Compare recorded routing with disk and the current checkout's template."""
    errors: list[str] = []
    notes: list[str] = []
    body = template_body(root)
    for raw_path, record in sorted(records.items()):
        location = record_location(raw_path, record)
        try:
            current = read_text_file(location.path)
            if not current.exists:
                errors.append(f"routing missing: {location.path}")
                continue
            if location.kind == OWNED_FILE:
                installed = current.text
                expected = render_owned(location.harness, body)
            else:
                span = find_block(current.text, location.path)
                if span is None:
                    errors.append(f"routing missing: {location.path}")
                    continue
                installed = current.text[span[0]: span[1]]
                expected = render_block(body)
        except RoutingError as exc:
            errors.append(f"routing unsafe: {exc}")
            continue
        if digest(installed) != record.get("hash"):
            errors.append(f"routing drifted: {location.path}")
        elif installed != expected:
            errors.append(f"routing differs from this checkout: {location.path}")
        if location.harness == "codex" and (override := codex_shadow(location.path)):
            errors.append(f"inactive: shadowed: {location.path} by {override}")
    recorded_harnesses = {record.get("harness") for record in records.values()}
    recorded_paths = {Path(path).resolve() for path in records}
    for harness in ROUTING_HARNESSES:
        active = harness_location(harness, home).path
        if harness in recorded_harnesses and active.resolve() not in recorded_paths:
            errors.append(f"routing not at the active {harness} location: {active}; rerun the installer with --routing")
    for workspace in workspace_roots:
        path = workspace_location(Path(workspace)).path
        if path.resolve() not in recorded_paths:
            errors.append(f"routing not recorded for workspace root {workspace}; rerun the installer with --routing --workspace-root, or use --remove-workspace-root")
    marked, unsafe = marked_locations(home, records)
    notes.extend(f"unrecorded routing marker: {path}" for path in marked)
    notes.extend(f"unrecorded routing location is unsafe: {problem}" for problem in unsafe)
    return errors, notes
