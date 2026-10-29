---
name: laravel-review
description: >-
  Review existing PHP, Laravel, Livewire, and Blade code for clean architecture,
  Eloquent performance, N+1 queries, OWASP security vulnerabilities, and maintainability,
  and produce a prioritized report where every finding cites the rule it breaks and
  provides a concrete drop-in fix. Use this whenever the user asks to review, audit,
  critique, grade, or check PHP or Laravel code, a Livewire component, a Blade view, a
  controller, an action, a model, a migration, a diff, or a pull request, or asks what is
  wrong with their Laravel code, even if they do not say "review". Pairs with the
  laravel-best-practices skill.
---

# Laravel Code Review

Review PHP, Laravel, and TALL-stack code against the standards in the
`laravel-best-practices` skill and report exact remediation steps. The output is an
engineering review, not an unsolicited rewrite: the developer decides what to fix.
Only rewrite the file completely when the user explicitly asks for that.

## 1. Decide the Scope

- **Identify target boundary:** Review exactly what the user specifies: a controller,
  a Livewire component, a Blade view, an action, a model, a migration, or a Git diff.
  For a diff, review the changed lines and their immediate callers, not unrelated files.
- **Identify Laravel and PHP version:** Check `composer.json` for PHP version (`^8.3`, `^8.4`, `^8.5`)
  and framework version (`laravel/framework: ^13.0`). Do not suggest features
  unsupported by the project's target runtime.
- **Identify stack & architecture:** Distinguish between pure JSON REST APIs, traditional
  Blade applications, and full-stack TALL-stack (Tailwind, Alpine, Livewire) components.

## 2. Run Automated Quality Tools First

If a terminal environment or container is accessible, run automated quality linters:

```bash
vendor/bin/pint --test          # Style and formatting conformance
vendor/bin/phpstan analyse      # Type safety and static analysis (Larastan)
vendor/bin/pest                 # Test suite status
```

Fold any reported static analysis warnings into the review report under the appropriate
category rather than dumping raw command logs.

## 3. Review Checklist in Priority Order

Evaluate the code systematically against these four levels:

### Level 1: Security & Data Integrity (Critical / High)
- **Authorization & IDOR:** Is every state-changing route and Livewire action method
  protected by a Policy check (`$this->authorize()`)? Are sequential IDs exposed without
  resource ownership checks?
- **Livewire State Hardening:** Are immutable public identifiers (IDs, tenant keys)
  annotated with `#[Locked]`? Are sensitive Eloquent models exposed directly as public
  properties without field protection?
- **Mass Assignment:** Is `$guarded = []` present on any model taking user payloads?
- **SQL Injection:** Are there unparameterized variables inside `whereRaw`, `orderByRaw`,
  or `DB::raw`?
- **Database Transactions:** Are multi-step updates or creations wrapped in `DB::transaction()`?
- **Secrets:** Is `env()` accessed directly instead of `config()`?

### Level 2: Database Performance, Resiliency & N+1 (High / Medium)
- **N+1 Queries:** Are model relationships accessed inside loops, accessors, or Blade
  views without prior eager loading (`with()`)?
- **Blade & Livewire Queries:** Are database queries executed directly inside Blade view
  templates or Livewire `render()` methods instead of prepared in computed properties
  (`#[Computed]`) or Actions?
- **Untimed HTTP Calls:** Are external API requests dispatched via `Http` without explicit
  `timeout()` and retry backoffs?
- **Memory Exhaustion:** Is `Model::all()` called on potentially large tables instead of
  `chunkById()` or pagination (`WithPagination`)?
- **Indexing:** Are foreign keys in migrations declared without indexes or foreign key
  constraints?

### Level 3: Architecture & Separation of Concerns (Medium)
- **Fat Controllers & Components:** Does the controller or Livewire component contain
  query building, payment calculations, or multi-step persistence? Decompose into an
  Action class.
- **Validation Boundary:** Are inputs validated using `$request->validate()` inline
  rather than a dedicated FormRequest (or `Livewire\Form` Form Object)?
- **Blade Template Hygiene:** Are there inline `<script>` or `<style>` blocks in Blade
  views? Extract interactivity to Alpine.js and styling to Tailwind classes.
- **Side Effects:** Are notifications, emails, or webhooks executed synchronously in the
  main request path instead of dispatched Events/Queued Jobs?
- **Naming Conventions:** Do models, tables, pivot tables, or relations violate Laravel
  community conventions (e.g., non-alphabetical pivot `user_article`, plural model names)?
- **File Length & Complexity:** Does any class exceed 300 lines of code or cyclomatic
  complexity 10?

### Level 4: Modern PHP & Type Safety (Low / Style)
- **Strict Types:** Is `declare(strict_types=1);` missing from the top of the file?
- **Type Hints:** Are function parameters, return types, or class properties untyped?
- **Magic Values:** Are string literals (`'active'`) or integer flags used instead of backed
  PHP Enums?
- **Fragile Named Arguments:** Are named arguments used when calling Laravel framework
  methods (e.g., `Route::get(uri: '...')`, `$request->input(key: '...')`)? Laravel does not
  guarantee parameter name stability across releases. Flag and replace with positional
  arguments.

## 4. Review Report Format

Format the review into a clear, prioritized Markdown report:

```markdown
# Code Review: UserManagementModule

## Summary
| Severity | Count | Summary of Issues |
|---|---|---|
| Critical | 1 | Unlocked public ID in Livewire component allowing IDOR |
| High | 2 | Query in Blade template; untimed HTTP client call |
| Medium | 2 | Domain mutation inside Livewire component; inline `<script>` in view |
| Low | 1 | Missing strict_types declaration |

## Findings & Fixes

### [Critical] Unlocked Public Identifier in Livewire Component
- **Location:** `app/Livewire/EditUserComponent.php:14`
- **Rule Broken:** Livewire Security - State Hardening with `#[Locked]`
- **Risk:** Unlocked `$userId` property allows clients to tamper with the target user ID via browser devtools.
- **Remediation:**
```php
// Before
public int $userId;

// After
use Livewire\Attributes\Locked;

#[Locked]
public int $userId;
```

### [High] Database Query inside Blade View
- **Location:** `resources/views/livewire/user-list.blade.php:22`
- **Rule Broken:** Blade Performance - Zero Database Queries in Views
- **Risk:** Querying inside `@foreach` triggers N+1 queries during every component DOM diff.
- **Remediation:**
```blade
{{-- Before --}}
@foreach ($user->orders()->latest()->take(5)->get() as $order)

{{-- After --}}
{{-- In Component: eager load via #[Computed] and pass collection to view --}}
@foreach ($user->recentOrders as $order)
```
```
