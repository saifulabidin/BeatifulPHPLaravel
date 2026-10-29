# Contributing to Beautiful PHP & Laravel

Contributions from the developer community are welcome. Follow these engineering guidelines before submitting issues or pull requests.

## Standards & Principles

1. **Anti-Hallucination & Accuracy:** Ensure all guidance reflects official PHP 8.3 and Laravel 11/12 documentation. Never invent nonexistent APIs.
2. **Strict Code Modularity:**
   - No Python script or PHP class/file shall exceed 300 lines of code.
   - Decompose complex workflows into dedicated actions, requests, or helper modules.
3. **Agent Skills Standards:**
   - Every skill must reside in `skills/<skill-name>/SKILL.md` with valid YAML frontmatter containing `name` and `description`.
   - The markdown body of `SKILL.md` must not exceed 24,000 bytes. Extended explanations belong in `references/`.
4. **Style & Hygiene:**
   - Zero emojis in code, commits, comments, or documentation.
   - Avoid conversational filler; write dense, actionable technical content.

## Development Workflow

1. Fork and clone the repository.
2. Run automated validation:
   ```bash
   python3 scripts/check-skills.py
   python3 -m unittest discover -s tests
   ```
3. If using Antigravity CLI, validate plugin compatibility:
   ```bash
   agy plugin validate .
   ```
4. Submit pull requests with descriptive commit messages and updated test coverage.
