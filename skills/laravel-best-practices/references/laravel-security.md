# Laravel Security Engineering Reference

## 1. OWASP Top 10 Mitigation in Laravel

### Broken Access Control & IDOR Prevention
Never rely solely on authentication middleware. Always verify resource ownership using Laravel Policies:

```php
// Antipattern: Insecure Direct Object Reference (IDOR)
public function show(int $id): JsonResponse
{
    $invoice = Invoice::findOrFail($id); // Any logged in user can view any invoice
    return response()->json($invoice);
}

// Secure: Policy authorization
public function show(Invoice $invoice): JsonResponse
{
    $this->authorize('view', $invoice); // Enforced via InvoicePolicy
    return response()->json(new InvoiceResource($invoice));
}
```

In `InvoicePolicy.php`:

```php
public function view(User $user, Invoice $invoice): bool
{
    return $user->id === $invoice->user_id || $user->hasRole('admin');
}
```

### SQL Injection Prevention
Never concatenate variables into raw SQL queries. Always pass bindings as an array:

```php
// Antipattern: Vulnerable to SQL Injection
DB::select("SELECT * FROM users WHERE email = '" . $request->input('email') . "'");

// Secure: Parameterized query
DB::select('SELECT id, name, email FROM users WHERE email = ?', [$request->input('email')]);

// Secure: Eloquent Query Builder
User::query()->where('email', $request->input('email'))->first();
```

### Mass Assignment Vulnerabilities
Never leave `$guarded = []` on models that accept user payloads. Explicitly define `$fillable`:

```php
class User extends Authenticatable
{
    /**
     * @var list<string>
     */
    protected $fillable = [
        'name',
        'email',
        'password',
    ];
}
```

Filter inputs using validated data from FormRequests:

```php
$user->update($request->validated());
```

### Cross-Site Scripting (XSS)
- Blade automatically sanitizes output when using double braces: `{{ $content }}`.
- Never render user input with unescaped tags `{!! $content !!}` unless processed through a strict HTML sanitizer (such as `mewebstudio/Purifier`).

### Cross-Site Request Forgery (CSRF)
- Web routes using session authentication must include `@csrf` in forms or send the `X-XSRF-TOKEN` header.
- Stateless API routes authenticated via tokens (Sanctum/Passport) should disable CSRF and enforce strict CORS origin allowlists in `config/cors.php`.

### Secrets & Environment Management
- Access `.env` values exclusively within configuration files (`config/*.php`).
- In application code, always use `config('services.stripe.secret')`.
- Running `php artisan config:cache` clears `env()` access during runtime; reading `env()` in controllers will return `null`.

### Rate Limiting
Protect authentication, password reset, and expensive endpoints:

```php
RateLimiter::for('api', function (Request $request) {
    return Limit::perMinute(60)->by($request->user()?->id ?: $request->ip());
});

RateLimiter::for('login', function (Request $request) {
    return Limit::perMinute(5)->by($request->input('email') . '|' . $request->ip());
});
```
