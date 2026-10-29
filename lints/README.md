# Drop-in Tooling Configurations for Modern Laravel

This directory provides production-ready configuration files for code style, static analysis, and automated refactoring.

## Files

- `pint.json`: Configuration for Laravel Pint enforcing strict types, explicit sorting, and clean formatting.
- `phpstan.neon`: Strict Larastan (PHPStan) configuration at level 8.
- `rector.php`: Rector rule set targeting PHP 8.3 features, early returns, type declarations, and dead code removal.

## Usage in a Laravel Project

1. Copy `pint.json` and `phpstan.neon` to the root of your Laravel project:
   ```bash
   cp lints/pint.json /path/to/laravel-project/pint.json
   cp lints/phpstan.neon /path/to/laravel-project/phpstan.neon
   ```

2. Run automated style checks:
   ```bash
   vendor/bin/pint --test
   ```

3. Run static analysis:
   ```bash
   vendor/bin/phpstan analyse
   ```
