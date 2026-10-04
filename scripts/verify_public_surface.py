#!/usr/bin/env python3
"""Verify the repository's public skill surface with stdlib only."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_FILES = (
    "SKILL.md",
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CHANGELOG.md",
    ".claude-plugin/plugin.json",
)

PERSONAL_PATH = re.compile(r"(?:/Users|/home)/[A-Za-z0-9._-]+/")
PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
REFERENCE_PATH = re.compile(r"references/[A-Za-z0-9._/-]+\.md")
VERSION_FIELD = re.compile(r"(?m)^version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$")
README_VERSION = re.compile(r"version-([0-9]+\.[0-9]+\.[0-9]+)-")


def markdown_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if ".git" not in path.parts)


def local_link_errors(root: Path, path: Path, text: str) -> list[str]:
    errors: list[str] = []
    candidates = [(match.group(1), path.parent) for match in MARKDOWN_LINK.finditer(text)]
    candidates.extend((match.group(0), root) for match in REFERENCE_PATH.finditer(text))

    for raw, base in candidates:
        target = raw.strip().split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:", "/")):
            continue
        resolved = (base / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{path.relative_to(root)}: local link escapes repository: {raw}")
            continue
        if not resolved.exists():
            errors.append(f"{path.relative_to(root)}: missing local link: {raw}")
    return sorted(set(errors))


def verify(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    skill_path = root / "SKILL.md"
    readme_path = root / "README.md"
    changelog_path = root / "CHANGELOG.md"
    plugin_path = root / ".claude-plugin/plugin.json"

    skill_text = skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""
    if not skill_text.startswith("---\n"):
        errors.append("SKILL.md: frontmatter must start at byte 0")
    if "\n---\n" not in skill_text[4:]:
        errors.append("SKILL.md: frontmatter closing delimiter is missing")

    version_match = VERSION_FIELD.search(skill_text)
    version = version_match.group(1) if version_match else None
    if not version:
        errors.append("SKILL.md: semver version field is missing")

    readme_text = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    readme_match = README_VERSION.search(readme_text)
    if version and (not readme_match or readme_match.group(1) != version):
        errors.append("README.md: version badge does not match SKILL.md")

    if plugin_path.exists():
        try:
            plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f".claude-plugin/plugin.json: invalid JSON: {exc}")
        else:
            if version and plugin.get("version") != version:
                errors.append(".claude-plugin/plugin.json: version does not match SKILL.md")
            for field in ("name", "description", "version", "author", "repository", "license"):
                if field not in plugin:
                    errors.append(f".claude-plugin/plugin.json: missing field: {field}")

    if version and changelog_path.exists():
        changelog = changelog_path.read_text(encoding="utf-8")
        if f"## [{version}]" not in changelog:
            errors.append("CHANGELOG.md: current SKILL.md version has no release section")

    for path in markdown_files(root):
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(root)
        if PERSONAL_PATH.search(text):
            errors.append(f"{relative}: contains a machine-specific home path")
        if PRIVATE_KEY.search(text):
            errors.append(f"{relative}: contains private-key material")
        errors.extend(local_link_errors(root, path, text))

    references = sorted((root / "references").glob("*.md"))
    if not references:
        errors.append("references/: no reference files found")
    for path in references:
        if "https://" not in path.read_text(encoding="utf-8"):
            errors.append(f"{path.relative_to(root)}: no HTTPS source URL found")

    return sorted(set(errors))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = verify(root)
    if errors:
        print("Public-surface verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Public-surface verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
