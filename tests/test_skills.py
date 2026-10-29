"""
Unit test suite for Beautiful PHP & Laravel agent skills.
"""

import unittest
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

class TestBeautifulPHPLaravelSkills(unittest.TestCase):
    def setUp(self):
        self.skills_dir = REPO_ROOT / "skills"
        self.expected_skills = [
            "laravel-best-practices",
            "laravel-review",
            "laravel-port",
        ]

    def test_skills_directories_exist(self):
        for skill_name in self.expected_skills:
            path = self.skills_dir / skill_name
            self.assertTrue(path.is_dir(), f"Skill directory missing: {skill_name}")
            self.assertTrue((path / "SKILL.md").is_file(), f"SKILL.md missing in {skill_name}")

    def test_skills_frontmatter(self):
        for skill_name in self.expected_skills:
            skill_file = self.skills_dir / skill_name / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            self.assertGreaterEqual(len(parts), 3, f"Invalid YAML frontmatter in {skill_name}")

            fm = yaml.safe_load(parts[1])
            self.assertEqual(fm.get("name"), skill_name)
            self.assertIn("description", fm)
            self.assertGreater(len(fm["description"]), 50)

    def test_skill_body_size_limits(self):
        for skill_name in self.expected_skills:
            skill_file = self.skills_dir / skill_name / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            body = content.split("---", 2)[2].strip()
            body_bytes = len(body.encode("utf-8"))
            self.assertLessEqual(
                body_bytes,
                24000,
                f"{skill_name} body exceeds 24,000 bytes ({body_bytes} bytes)",
            )

    def test_references_exist_for_best_practices(self):
        ref_dir = self.skills_dir / "laravel-best-practices" / "references"
        self.assertTrue(ref_dir.is_dir())
        expected_refs = [
            "laravel-architecture.md",
            "eloquent-performance-n1.md",
            "php-modern-features.md",
            "laravel-security.md",
            "testing-pest-guidelines.md",
            "laravel-naming-conventions.md",
            "caching-and-resilience.md",
            "livewire-and-tall-stack.md",
        ]
        for ref in expected_refs:
            ref_path = ref_dir / ref
            self.assertTrue(ref_path.is_file(), f"Reference file missing: {ref}")
            self.assertGreater(ref_path.stat().st_size, 100, f"Reference file too small: {ref}")

    def test_code_files_within_line_limit(self):
        for ext in ("*.py", "*.php"):
            for path in REPO_ROOT.rglob(ext):
                if "BeautifulRust" in path.parts or ".git" in path.parts:
                    continue
                lines = len(path.read_text(encoding="utf-8").splitlines())
                self.assertLessEqual(
                    lines,
                    300,
                    f"File {path.relative_to(REPO_ROOT)} exceeds 300 lines limit ({lines} lines)",
                )

if __name__ == "__main__":
    unittest.main()
