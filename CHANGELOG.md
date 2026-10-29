# Changelog

All notable changes to the Beautiful PHP & Laravel project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-30

### Added
- Initial release of the Beautiful PHP & Laravel agent skill suite.
- `laravel-best-practices` skill covering modern PHP 8.3, clean architecture, Action classes, FormRequests, DTOs, Eloquent optimization, and Pest testing.
- Comprehensive reference digests in `references/`:
  - `laravel-architecture.md`
  - `eloquent-performance-n1.md`
  - `php-modern-features.md`
  - `laravel-security.md`
  - `testing-pest-guidelines.md`
  - `laravel-naming-conventions.md`
  - `caching-and-resilience.md`
  - `livewire-and-tall-stack.md`
- `laravel-review` skill providing automated, prioritized code reviews citing rules, severity levels, and code remediation.
- `laravel-port` skill guiding migrations from legacy procedural PHP, Express.js, Django, FastAPI, and Rails to modern Laravel.
- Production-ready drop-in tooling configurations in `lints/`:
  - `pint.json` (Laravel Pint strict formatting preset)
  - `phpstan.neon` (Larastan level 8 static analysis)
  - `rector.php` (Rector rule sets for PHP 8.3 and modern Laravel)
- Native Antigravity / Gemini CLI / Claude Code plugin integration via `plugin.json` and `rules/AGENTS.md`.
- Automated skill verification suite and unit tests (`scripts/check-skills.py`, `tests/test_skills.py`).
