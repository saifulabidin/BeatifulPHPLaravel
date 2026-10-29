# Laravel Clean Architecture Reference

This digest defines the architectural layers, boundaries, and communication contracts for modern Laravel applications.

## 1. Request Lifecycle Flow

Every HTTP request follows a unidirectional flow:

```text
Request ──> Middleware ──> FormRequest (Validation/Auth)
                               └──> Controller (Route only)
                                       └──> Action (Business Logic)
                                               ├──> Service (Orchestration)
                                               └──> Repository/Model (Persistence)
                                                       └──> DTO (Data Transport)
```

## 2. Layer Responsibilities

### FormRequest
- Owns input validation rules and preliminary authorization (`can()`).
- Sanitizes or formats primitives into typed representations if necessary.
- Never performs database mutations or dispatches domain events.

### Controller
- Accepts the injected FormRequest and domain Action.
- Instantiates a DTO from the validated request.
- Invokes the Action with typed parameters.
- Converts the Action's domain return object into an API Resource or View.
- Contains no `if/else` business workflows, no direct Eloquent queries, and no raw SQL.

### Action Class
- Encapsulates exactly one business operation.
- Has a single public method: `execute(...)` or `__invoke(...)`.
- Receives dependencies via constructor injection.
- Wraps database write operations in `DB::transaction()`.
- Dispatches domain Events for non-critical side effects.
- Throws domain-specific exceptions on business rule violations.

### DTO (Data Transfer Object)
- Immutable PHP 8.3 `readonly class`.
- Strongly typed properties; no untyped arrays or bags.
- Provides static factory methods like `fromRequest(FormRequest $request): self` or `fromArray(array $data): self`.

### Service
- Stateless coordinator used only when an operation spans across multiple Actions or interfaces with third-party APIs (payment processors, CRM integrations).
- Does not hold user state.

### Repository
- Encapsulates query logic to keep business logic independent of Eloquent query builder nuances.
- Returns Models, Collections, or DTOs.
- Never leaks `Builder` instances outside the repository class.

## 3. Error Handling and Domain Exceptions

- **Domain-Specific Exceptions:** Actions throw typed domain exceptions extending `DomainException` instead of generic `\Exception` (e.g., `throw new InsufficientInventoryException('Product stock depleted.');`).
- **Zero Silent Exception Swallowing:** Never use empty `catch (\Exception $e) {}` blocks. If an exception is expected, log it with context or handle it explicitly.
- **Centralized Exception Configuration:** Map domain exceptions to HTTP responses cleanly in `bootstrap/app.php`:
  ```php
  ->withExceptions(function (Exceptions $exceptions) {
      $exceptions->render(function (DomainException $e, Request $request) {
          if ($request->expectsJson()) {
              return response()->json([
                  'message' => $e->getMessage(),
              ], Response::HTTP_UNPROCESSABLE_ENTITY);
          }
      });
  })
  ```

## 4. Architecture Decision Record (ADR) Template

Document major architectural choices using this structure:

```markdown
# ADR-001: Adoption of Action Classes for Business Logic

## Context
Controllers were accumulating mixed concerns: query building, payment API calls, validation, and email dispatching, leading to high cyclomatic complexity and low testability.

## Decision
Adopt single-purpose Action classes under `app/Actions/{Domain}/` for all state-changing operations. Controllers will act strictly as request routers.

## Consequences
- Positive: Each business operation is testable in isolation without HTTP mocking.
- Positive: Operations can be reused in Artisan commands, Queued Jobs, and API controllers.
- Negative: Additional classes to maintain compared to inline controller methods.
```
