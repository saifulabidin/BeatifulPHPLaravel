# Beautiful PHP & Laravel Engineering Standards

<EXTREMELY_IMPORTANT>
You have the Beautiful PHP & Laravel suite available globally.
Enforce these core standards for modern PHP (8.3 - 8.5) and Laravel 13.x:

1. PHP 8.3 - 8.5 & Type Safety:
- Always declare strict types: declare(strict_types=1);
- Enforce explicit type declarations on all parameters, return types, and class properties.
- Use PHP 8.3+ readonly classes or PHP 8.4+ asymmetric visibility (public private(set)) for DTOs.
- Use typed class constants, #[Override], and json_validate() where applicable.
- Replace magic values, strings, and integer flags with backed PHP enums.
- CAUTION ON NAMED ARGUMENTS: Never use named arguments when calling Laravel framework methods (e.g., $request->input(key: '...'), Route::get(uri: '...')). Laravel does not cover argument names under SemVer. Restrict named arguments exclusively to your internal code (DTOs, Actions, Value Objects).

2. Laravel 13.x Architecture & Layering:
- Controllers are routers only. Maximum one Action execution per controller method; never place business logic in controllers.
- FormRequests handle all boundary validation and authorization checks.
- Actions execute single business or AI-orchestration tasks with one public execute() method and handle database transactions.
- Services orchestrate multiple actions or handle third-party integrations (stateless).
- DTOs transport structured immutable data between layers.
- API output conforms to JSON:API / JsonResource specifications.
- Repositories abstract persistence without leaking Eloquent query builders.
- Events and Listeners handle side effects exclusively (notifications, logs, cache invalidation).

3. TALL-Stack & Livewire 3/4 Standards:
- Livewire components act as UI controllers: delegate domain operations and mutations to Action classes, never inline in components.
- State Hardening: Use #[Locked] on immutable public properties (IDs, keys). Always authorize inside action methods ($this->authorize()).
- Use Livewire Form Objects (Livewire\Form) for multi-field forms instead of sprawling public properties.
- Data Performance: Never execute database queries inside render() or Blade templates. Cache data using #[Computed] properties and defer slow widgets with #[Lazy].
- Blade View Hygiene: Zero inline <script> or <style> tags. Use Tailwind utility classes for design and Alpine.js (x-data, x-on) for UI interactivity. Use wire:ignore on third-party JS widgets.

4. Eloquent & Performance:
- Never execute database queries inside loops or Blade views.
- Always eager load relationships using with() to eliminate N+1 queries.
- Activate Model::preventLazyLoading(!app()->isProduction()) in AppServiceProvider.
- Wrap multi-statement database modifications inside DB::transaction().
- Process large datasets using chunkById() or lazy(), never Model::all().

5. Strict Modularity:
- Max File Length: No PHP class or script shall exceed 300 lines of code. Split into dedicated actions, requests, or sub-services before reaching the ceiling.
- Cyclomatic complexity ceiling of 10 per method.

6. Forbidden Patterns:
- dd(), dump(), var_dump(), print_r() in non-debug code.
- env() outside config files; always use config().
- Raw SQL without parameter bindings.
- Silently swallowed exceptions (empty catch blocks).
- Unvalidated user inputs or mass assignment vulnerabilities ($guarded = []).
</EXTREMELY_IMPORTANT>
