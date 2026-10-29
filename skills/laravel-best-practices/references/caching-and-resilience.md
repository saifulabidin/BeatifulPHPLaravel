# Caching, Resilience, Queue, and Task Scheduling Reference

## 1. Caching Strategies

### Never Perform Manual Cache Get/Put
Avoid manual cache checks that create race conditions:

```php
// Antipattern: Race condition prone
$value = Cache::get('key');
if ($value === null) {
    $value = $this->expensiveCalculation();
    Cache::put('key', $value, 3600);
}

// Recommended: Atomic read and compute
$value = Cache::remember('key', now()->addHour(), function () {
    return $this->expensiveCalculation();
});
```

### Stale-While-Revalidate with Cache::flexible()
Prevent thundering herd problems on high-traffic endpoints by serving stale cache while recomputing in the background:

```php
// Fresh for 5 minutes, served stale up to 30 minutes while recomputing
$stats = Cache::flexible('dashboard:daily_stats', [300, 1800], function () {
    return $this->calculateHeavyDailyStats();
});
```

### Distributed Locks for Critical Mutations
Use atomic locks to prevent race conditions on payment captures or inventory reservations:

```php
$lock = Cache::lock("checkout:user:{$user->id}", 10);

try {
    $lock->block(5); // Wait up to 5 seconds to acquire lock
    $this->chargeUser($user, $amount);
} finally {
    $lock?->release();
}
```

### Per-Request Memoization with once()
Avoid re-evaluating identical calls within a single HTTP request lifecycle without polluting Redis:

```php
public function currentTenant(): Tenant
{
    return once(function () {
        return Tenant::where('hostname', request()->getHost())->firstOrFail();
    });
}
```

## 2. HTTP Client Resiliency

Never make untimed external HTTP requests. A hanging third-party API will exhaust PHP-FPM workers and crash the application:

```php
// Antipattern: Can hang forever
$response = Http::post('https://api.gateway.com/charge', $payload);

// Recommended: Explicit timeouts and retry backoff
$response = Http::timeout(5)
    ->connectTimeout(2)
    ->retry(3, 100, throw: false) // Retry 3 times, waiting 100ms
    ->post('https://api.gateway.com/charge', $payload);

if ($response->failed()) {
    throw new ExternalServiceUnavailableException('Payment gateway unreachable.');
}
```

## 3. Queue and Background Job Best Practices

### Job Idempotency
Jobs can be executed multiple times due to network drops, worker restarts, or queue retries. Design every job to be idempotent:

```php
final class FulfillOrderJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $tries = 3;
    public array $backoff = [10, 60, 300]; // 10s, 1m, 5m
    public int $timeout = 60;

    public function __construct(
        public readonly int $orderId,
    ) {}

    public function handle(OrderRepositoryInterface $orders): void
    {
        $order = $orders->find($this->orderId);

        // Guard: check if already fulfilled before processing
        if ($order->isFulfilled()) {
            return;
        }

        $orders->markAsFulfilled($order);
    }
}
```

- Pass IDs or DTO primitives instead of giant serialized state.
- Always declare `$tries`, `$backoff`, and `$timeout` explicitly.

## 4. Artisan Commands and Task Scheduling

### Commands are Routers Only
Artisan commands must remain thin controllers: parse CLI arguments and options, instantiate DTOs, and delegate immediately to domain Action classes:

```php
final class PruneExpiredSubscriptionsCommand extends Command
{
    protected $signature = 'subscriptions:prune {--days=30 : Days since expiration}';
    protected $description = 'Prune cancelled subscriptions older than the specified days';

    public function handle(PruneExpiredSubscriptionsAction $action): int
    {
        $days = (int) $this->option('days');
        $count = $action->execute($days);

        $this->info("Successfully pruned {$count} expired subscriptions.");
        return self::SUCCESS;
    }
}
```

### Scheduling Best Practices in routes/console.php
Configure task schedules with concurrency protections:

```php
use Illuminate\Support\Facades\Schedule;

// Run daily at midnight on one server, preventing overlapping runs
Schedule::command('subscriptions:prune --days=30')
    ->dailyAt('00:00')
    ->withoutOverlapping(expiresAt: 60) // Prevent parallel runs if execution exceeds interval
    ->onOneServer()                     // In multi-server cluster, run on a single node only
    ->runInBackground()                 // Do not block subsequent scheduled commands
    ->onFailure(function () {
        Log::channel('alerts')->critical('Pruning subscriptions command failed.');
    });
```
