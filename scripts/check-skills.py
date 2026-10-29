#!/usr/bin/env python3
"""
Validation script for Beautiful PHP & Laravel agent skills.
Checks frontmatter, file sizes, references, and line length constraints.
"""

import os
import sys
import yaml
from pathlib import Path

MAX_BODY_BYTES = 24000
MAX_FILE_LINES = 300

def parse_skill_file(skill_path: Path):
    content = skill_path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return None, "Missing frontmatter start marker '---'", len(content)

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, "Malformed YAML frontmatter", len(content)

    try:
        frontmatter = yaml.safe_load(parts[1])
    except Exception as e:
        return None, f"YAML parsing error: {e}", len(content)

    body = parts[2].strip()
    return frontmatter, body, len(body.encode("utf-8"))

def validate_all_skills(repo_root: Path) -> list[str]:
    errors = []
    skills_dir = repo_root / "skills"

    if not skills_dir.exists():
        return ["Skills directory not found"]

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            errors.append(f"Missing SKILL.md in {skill_dir.name}")
            continue

        fm, body, body_bytes = parse_skill_file(skill_file)
        if fm is None:
            errors.append(f"{skill_dir.name}: {body}")
            continue

        if not fm.get("name"):
            errors.append(f"{skill_dir.name}: Missing 'name' in frontmatter")
        elif fm["name"] != skill_dir.name:
            errors.append(f"{skill_dir.name}: Frontmatter name '{fm['name']}' does not match directory")

        if not fm.get("description"):
            errors.append(f"{skill_dir.name}: Missing 'description' in frontmatter")

        if body_bytes > MAX_BODY_BYTES:
            errors.append(f"{skill_dir.name}: Body is {body_bytes} bytes (limit is {MAX_BODY_BYTES})")

        # Check references directory if present
        ref_dir = skill_dir / "references"
        if ref_dir.exists():
            for ref_file in ref_dir.glob("*.md"):
                if ref_file.stat().st_size == 0:
                    errors.append(f"Empty reference file: {ref_file.name}")

    return errors

def check_file_line_limits(repo_root: Path) -> list[str]:
    errors = []
    for ext in ("*.py", "*.php"):
        for path in repo_root.rglob(ext):
            if "BeautifulRust" in path.parts or ".git" in path.parts:
                continue
            line_count = len(path.read_text(encoding="utf-8").splitlines())
            if line_count > MAX_FILE_LINES:
                errors.append(f"{path.relative_to(repo_root)} exceeds limit: {line_count} lines (> {MAX_FILE_LINES})")
    return errors

def main():
    root = Path(__file__).resolve().parent.parent
    skill_errors = validate_all_skills(root)
    line_errors = check_file_line_limits(root)

    all_errors = skill_errors + line_errors

    if all_errors:
        print("Validation FAILED with errors:")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)

    print("All skills, frontmatters, byte limits, and code file lengths successfully validated.")
    sys.exit(0)

if __name__ == "__main__":
    main()
