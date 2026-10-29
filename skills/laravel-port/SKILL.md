---
name: laravel-port
description: >-
  Port legacy PHP, Express.js, Node.js, Python (Django/FastAPI), or Ruby on Rails code
  into idiomatic modern PHP (8.3 - 8.5) and Laravel 13.x with identical observable
  behavior. Ports original tests first into Pest to prove parity, then converts business
  logic into FormRequests, Action classes, DTOs, and Eloquent models. Use this whenever
  the user asks to port, translate, convert, migrate, modernize, or rewrite code in PHP
  or Laravel ("rewrite this in Laravel", "port this express API to Laravel", "modernize
  this legacy PHP script"), even if they do not say "port". Pairs with the
  laravel-best-practices skill.
---

# Laravel Port

The objective of a port is to produce modern, idiomatic PHP 8.3 - 8.5 and Laravel 13
code that solves the same domain problem with identical observable behavior. A direct
line-by-line transliteration (e.g. copying procedural `$_POST` scripts or Express
middleware chains directly into a Laravel controller) carries over technical debt. Port
the behavior, not the legacy structure.

## 1. Understand the Original Code

1. **Map the inputs and outputs:** Enumerate all endpoints, HTTP methods, accepted request
   payloads, query parameters, returned headers, JSON responses, and HTTP status codes
   (200, 201, 400, 401, 403, 404, 422, 500).
2. **Catalog edge cases & quiet behavior:** Note how empty strings, nulls, array sorting,
   validation failures, and exceptions are formatted in the source code.
3. **Separate domain logic from runtime artifacts:** Strip away runtime-specific scaffolding:
   Express `next()` callbacks, manual database connection pooling, or Python `async/await`
   event loops that have no direct place in synchronous Laravel request workers.

## 2. Port the Tests First

Translate existing test suites into Pest feature tests before writing application code:

```php
// Port original Jest / Pytest cases into Pest
it('authenticates user and returns access token on valid credentials', function () {
    $user = User::factory()->create([
        'email' => 'developer@example.com',
        'password' => bcrypt('secret123'),
    ]);

    $response = $this->postJson('/api/v1/auth/login', [
        'email' => 'developer@example.com',
        'password' => 'secret123',
    ]);

    $response->assertOk()
        ->assertJsonStructure(['token', 'user' => ['id', 'email']]);
});
```

Passing ported tests proves that the new implementation matches original behavior.

## 3. Design the Laravel Architecture

Implement according to clean architectural layers:

| Original Component | Modern Laravel 13 Equivalent |
|---|---|
| Procedural script / Express route handler | Thin Controller invoking an Action class |
| Zod / Joi / Pydantic schema / manual `if (!req.body)` | Dedicated `FormRequest` with typed rules |
| Raw SQL queries / procedural database calls | Eloquent Models + Migration with explicit indexes |
| Multi-table update script | `DB::transaction()` inside an `Action` class |
| React / Vue widget / jQuery AJAX form | Livewire 3/4 Component + Alpine.js |
| Inline JSON response object | `JsonResource` / JSON:API Resource |
| Express middleware / Django middleware | Laravel HTTP Middleware |
| Python Dataclass / TypeScript interface | PHP 8.3+ `readonly class` DTO |
| String flags / status integers | PHP 8.3+ backed `Enum` |

## 4. Source-Specific Translation Guides

### From Legacy PHP (Procedural / CodeIgniter / PHP 5-7)
- **Global state:** Eliminate `$_GET`, `$_POST`, `$_SESSION`, and `global $conn`. Inject
  `Request` and use Laravel's session or token authentication.
- **Raw SQL:** Convert procedural queries (`mysqli_query`, `PDO::query`) into Eloquent
  relationships or parameterized Query Builder calls.
- **Passwords:** Replace legacy `md5()` or `sha1()` hashing with Laravel's `Hash::make()`
  (bcrypt/Argon2id) and implement transparent re-hashing on login.

### From Express.js / Node.js
- **Routing:** Convert `app.post('/api/users', handler)` into `Route::post('/users', [UserController::class, 'store'])`
  in `routes/api.php`. Use positional arguments, avoiding named parameters.
- **Validation:** Replace `express-validator` or `zod` with a `StoreUserRequest`.
- **Async/Await:** Node's async I/O is standard synchronous execution in PHP workers. For
  heavy background tasks, dispatch queued jobs (`dispatch(new ProcessWebhookJob($payload))`).

### From Python (Django / FastAPI)
- **Django Models:** Convert Django model fields (`models.CharField`, `models.ForeignKey`)
  into Laravel database migrations and Eloquent relationships (`belongsTo`, `hasMany`).
- **FastAPI Pydantic:** Replace Pydantic request models with FormRequests, and response
  models with Laravel API Resources.

## 5. Verification

Before concluding the port, execute:

```bash
vendor/bin/pint --test
vendor/bin/phpstan analyse
vendor/bin/pest
```
