---
name: laravel-best-practices
description: >-
  Write, review, or refactor modern PHP (8.3 - 8.5) and Laravel 13.x code. This includes
  creating or modifying controllers, models, migrations, form requests, policies, queue
  jobs, scheduled commands, service classes, Livewire components, Blade views, and Eloquent
  queries. Triggers on N+1 queries and query performance issues, caching strategies,
  authorization and security patterns, input validation, domain error handling, queue and
  worker configuration, route definitions, and architectural decisions.
---

# Laravel Best Practices

Distilled from modern PHP (8.3 - 8.5) standards and Laravel 13 enterprise architecture.
Detailed deep-dive guides for architecture, Livewire and TALL stack, Eloquent performance,
PHP features, security, naming conventions, resilience, and Pest testing are bundled in
`references/`.

## 1. Mindset

- **Write idiomatic modern Laravel 13.** Avoid legacy PHP antipatterns: global helpers
  where dependency injection belongs, fat controllers containing SQL queries, or
  procedural scripts disguised as classes. Use dedicated FormRequests, single-purpose
  Action classes, immutable DTOs, and backed Enums.
- **Full-stack TALL-stack hygiene.** Treat Livewire components as frontend controllers:
  delegate domain logic to Actions, lock sensitive public identifiers with `#[Locked]`,
  group form fields into `Livewire\Form` objects, memoize data queries via `#[Computed]`,
  and never execute database queries inside `render()` or Blade templates.
- **Follow strict Laravel naming conventions.** Consistency across the ecosystem is
  critical: singular PascalCase models (`User`), plural snake_case tables (`users`),
  alphabetical singular pivot tables (`article_user`), singular belongsTo (`user()`),
  plural hasMany (`orders()`), and singular resource controllers (`OrderController`).
- **Make invalid states unrepresentable.** Use PHP 8.3+ typed properties, backed Enums
  instead of arbitrary strings or numeric status flags, and readonly DTOs with validated
  constructors. Rely on the type system rather than defensive comments.
- **Thin controllers, rich domain actions.** Controllers only route requests: authorize,
  delegate to a single Action, and return a JSON:API Resource or View. Any business logic,
  multi-step database mutation, or third-party API call inside a controller is an
  architectural defect.
- **Caution with named arguments on framework methods.** Laravel's backwards compatibility
  guidelines explicitly exclude argument names. Parameter names in framework methods may
  change across releases. Never use named arguments when calling Laravel methods
  (e.g., call `$request->input('key')`, never `$request->input(key: 'key')`). Restrict
  named arguments strictly to your internal application code (Actions, DTOs, value objects).
- **Leverage Laravel 13 primitives.** Take advantage of first-party AI primitives,
  native JSON:API resources, and vector search indexing where appropriate.
- **Resiliency by default.** Never issue an untimed external HTTP call. Always configure
  explicit timeouts (`Http::timeout(5)`) and automated retry backoffs. Use atomic distributed
  locks (`Cache::lock()`) for high-contention checkout/mutation workflows.
- **Fail early and protect boundaries.** Validate and authorize every incoming payload
  at the boundary via FormRequest or Livewire Form Object before business logic executes.
  Never trust client input, even from authenticated users.
- **Modularity is mandatory.** No PHP class shall exceed 300 lines of code. No method
  shall exceed cyclomatic complexity 10. Decompose into dedicated sub-actions or services
  proactively.

## 2. Before You Hand Back Code

Run these automated checks from the project root and resolve all issues:

```bash
vendor/bin/pint --test          # Code style & PSR-12 enforcement
vendor/bin/phpstan analyse      # Static analysis (Larastan level 8/max)
vendor/bin/pest                 # Unit, Feature, and Architecture test suite
composer audit                  # Check dependencies for known security vulnerabilities
```

- Fix the underlying issue rather than suppressing warnings with baseline comments or
  untyped docblocks.
- Use Laravel Pint (`pint.json`) to automate code style formatting (`vendor/bin/pint`).

## 3. Modern PHP (8.3 - 8.5) Standards

Always declare strict types at the very top of every PHP file:

```php
<?php

declare(strict_types=1);

namespace App\Actions\Order;
```

- **Type declarations everywhere.** Every function and method must declare explicit parameter
  types and return types. Use union types (`int|string`) and nullable types (`?string`)
  strictly where needed. Avoid untyped variables or generic `mixed` unless implementing an
  untyped external contract.
- **Readonly classes and asymmetric visibility.** Value objects and data transfer objects
  must be immutable. Use `readonly class` (PHP 8.2+) or asymmetric visibility
  `public private(set)` (PHP 8.4+):
  ```php
  readonly class CreateOrderData
  {
      public function __construct(
          public int $userId,
          public int $amountInCents,
          public OrderStatus $status,
      ) {}
  }
  ```
- **Backed Enums over magic values.** Never use bare strings (`'pending'`) or integer flags
  (`1`) for statuses, roles, or categories:
  ```php
  enum OrderStatus: string
  {
      case Pending = 'pending';
      case Paid = 'paid';
      case Cancelled = 'cancelled';
  }
  ```
- **Modern PHP language features.** Use typed class constants (`public const string DEFAULT_ROLE = 'guest';`),
  `json_validate()` to check JSON before decoding, the `#[Override]` attribute on
  methods that intentionally override parent behavior, and array helpers (`array_find()`).

## 4. Architecture & Layering

Maintain strict separation of concerns across both API and full-stack requests:

```text
HTTP Request / Livewire Event
  └── FormRequest / Livewire Form   (Validation & boundary authorization)
       └── Controller / Component   (Route to action, manage UI state)
            └── Action              (Single business/AI operation, DB transaction)
                 └── Service        (Stateless cross-action orchestration)
                      └── Repository / Eloquent Model (Persistence)
                           └── DTO  (Readonly immutable transport)
```

### FormRequest & Livewire Form Objects
Encapsulate validation and authorization cleanly:

```php
final class StoreOrderRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()->can('create', Order::class);
    }

    public function rules(): array
    {
        return [
            'item_id' => ['required', 'integer', 'exists:items,id'],
            'quantity' => ['required', 'integer', 'min:1', 'max:100'],
        ];
    }
}
```

In Livewire components, use dedicated Form Objects:
```php
use Livewire\Form;
use Livewire\Attributes\Validate;

final class CheckoutForm extends Form
{
    #[Validate('required|integer|exists:items,id')]
    public int $itemId;

    #[Validate('required|integer|min:1|max:100')]
    public int $quantity = 1;
}
```

### Controller & Livewire Component
Controllers and Livewire components must contain zero domain business logic:

```php
final class OrderController extends Controller
{
    public function store(
        StoreOrderRequest $request,
        CreateOrderAction $action,
    ): JsonResponse {
        $order = $action->execute(
            $request->user(),
            CreateOrderData::fromRequest($request),
        );

        return (new OrderResource($order))
            ->response()
            ->setStatusCode(Response::HTTP_CREATED);
    }
}
```

### Action Class (Single Business Operation)
An Action encapsulates one distinct business workflow, exposing a single `execute()` method:

```php
final class CreateOrderAction
{
    public function __construct(
        private readonly PaymentGatewayInterface $paymentGateway,
        private readonly OrderRepositoryInterface $orders,
    ) {}

    public function execute(User $user, CreateOrderData $data): Order
    {
        return DB::transaction(function () use ($user, $data) {
            $order = $this->orders->createForUser($user, $data);
            $this->paymentGateway->charge($order, $data->amountInCents);

            OrderCreatedEvent::dispatch($order);

            return $order;
        });
    }
}
```

- Inject dependencies through the constructor.
- Wrap multi-statement database operations in `DB::transaction()`.
- Dispatch Events for side effects (emails, webhooks, audit logs).

## 5. Eloquent & Database Optimization

### Eliminate N+1 Queries
Accessing relations inside loops triggers an individual SQL query per iteration:

```php
// Bad: N+1 queries executed
$orders = Order::all();
foreach ($orders as $order) {
    echo $order->customer->name;
}

// Good: 2 queries total via eager loading
$orders = Order::with('customer')->get();
foreach ($orders as $order) {
    echo $order->customer->name;
}
```

- In `AppServiceProvider::boot()`, prevent lazy loading in non-production environments:
  ```php
  Model::preventLazyLoading(! app()->isProduction());
  ```
- Use `loadMissing()` when a model instance already exists without relations loaded.
- In API Resources and Blade components, guard relations with `whenLoaded('customer')`.
- Never execute database queries inside Blade templates or Livewire `render()` methods.

### Caching and Resiliency
- Use `Cache::remember()` or `Cache::flexible()` (for stale-while-revalidate protection
  against thundering herds).
- Use `Cache::lock()` to avoid race conditions during concurrent financial mutations.
- Always configure HTTP client timeouts (`Http::timeout(5)->retry(3)`).

### Large Dataset Processing
- Never use `Model::all()` on unbounded database tables.
- Use `chunkById(1000)` or `lazyById()` to process large record collections with constant
  memory consumption:
  ```php
  Order::query()
      ->where('status', OrderStatus::Pending)
      ->chunkById(500, function (Collection $orders): void {
          foreach ($orders as $order) {
              $this->processOrder($order);
          }
      });
  ```

### Database Migrations
- Define explicit foreign key constraints with indexed foreign keys.
- Write bidirectional migrations: `up()` to apply and `down()` to revert safely.
- Never write business logic inside migration classes.

## 6. Security Engineering

- **Mass assignment:** Use explicit `$fillable` arrays on Eloquent models. Never use
  empty `$guarded = []` on models exposed to request payloads.
- **SQL Injection:** Never concatenate raw user input into `whereRaw()`, `orderByRaw()`,
  or `DB::raw()`. Always pass parameterized bindings.
- **Livewire state hardening:** Annotate immutable properties with `#[Locked]`. Authorize
  every state-changing action method with `$this->authorize()`. Never store unmasked
  sensitive models in public component properties.
- **Authorization:** Authorize every state-changing operation using Laravel Policies:
  `$this->authorize('update', $order)` or `$user->can('delete', $post)`.
- **XSS Prevention:** In Blade templates, always use `{{ $escaped }}`. Use `{!! $raw !!}`
  only for trusted internal HTML, never for user-submitted content.
- **Secrets Management:** Never access `env()` outside config files. Always read through
  `config('services.stripe.key')`. Run `config:cache` in production.

## 7. Testing with Pest

Write expressive, behavior-driven tests with Pest, including Livewire component tests:

```php
use App\Models\User;
use App\Models\Order;
use App\Enums\OrderStatus;
use function Pest\Livewire\livewire;
use App\Livewire\OrderCheckoutComponent;

it('creates an order and dispatches creation event', function () {
    Event::fake();
    $user = User::factory()->create();

    $response = $this->actingAs($user)->postJson('/api/orders', [
        'item_id' => 12,
        'quantity' => 2,
    ]);

    $response->assertStatus(201)
        ->assertJsonPath('data.status', OrderStatus::Pending->value);

    Event::assertDispatched(OrderCreatedEvent::class);
});

it('tests livewire checkout component authorization and validation', function () {
    $user = User::factory()->create();

    livewire(OrderCheckoutComponent::class)
        ->actingAs($user)
        ->set('form.itemId', 12)
        ->set('form.quantity', 2)
        ->call('process')
        ->assertHasNoErrors()
        ->assertRedirect();
});
```

- Enforce architecture rules using Pest Architecture testing:
  ```php
  arch('controllers are thin')
      ->expect('App\Http\Controllers')
      ->not->toUse('Illuminate\Support\Facades\DB')
      ->toOnlyImplement(['App\Http\Controllers\Controller']);

  arch('strict types are declared')
      ->expect('App')
      ->toUseStrictTypes();
  ```

## 8. Detailed References

For comprehensive guidelines, consult the digests in `references/`:
- `references/laravel-architecture.md`: In-depth layered architecture, Action patterns, and ADRs.
- `references/livewire-and-tall-stack.md`: TALL-stack patterns, Livewire security, state locking, and Blade components.
- `references/eloquent-performance-n1.md`: Deep dive on query optimization, eager loading, and subqueries.
- `references/laravel-naming-conventions.md`: Complete matrix of Laravel ecosystem naming conventions.
- `references/caching-and-resilience.md`: Caching strategies, distributed locks, and HTTP client resiliency.
- `references/php-modern-features.md`: Full reference of PHP 8.3 - 8.5 modern features.
- `references/laravel-security.md`: OWASP Top 10 mitigation and security checklists.
- `references/testing-pest-guidelines.md`: Complete Pest testing patterns and architecture tests.
