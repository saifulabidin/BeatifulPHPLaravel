# Testing with Pest and Architecture Tests Reference

## 1. Test Suite Structure

Organize tests into clear directories:

```text
tests/
├── Architecture/
│   └── ArchTest.php
├── Feature/
│   ├── Order/
│   │   ├── CreateOrderTest.php
│   │   └── CancelOrderTest.php
└── Unit/
    └── DTO/
        └── CreateOrderDataTest.php
```

## 2. Feature Testing Patterns

Feature tests test end-to-end HTTP request and response cycles:

```php
use App\Models\User;
use App\Models\Product;
use Illuminate\Support\Facades\Queue;
use App\Jobs\ProcessOrderJob;

beforeEach(function () {
    Queue::fake();
    $this->user = User::factory()->create();
});

it('allows customer to create order with valid items', function () {
    $product = Product::factory()->create(['stock' => 10, 'price' => 5000]);

    $response = $this->actingAs($this->user)->postJson('/api/orders', [
        'product_id' => $product->id,
        'quantity' => 2,
    ]);

    $response->assertCreated()
        ->assertJsonPath('data.total_amount', 10000);

    $this->assertDatabaseHas('orders', [
        'user_id' => $this->user->id,
        'total_amount' => 10000,
    ]);

    Queue::assertPushed(ProcessOrderJob::class);
});

it('rejects order when requested quantity exceeds stock', function () {
    $product = Product::factory()->create(['stock' => 1]);

    $response = $this->actingAs($this->user)->postJson('/api/orders', [
        'product_id' => $product->id,
        'quantity' => 5,
    ]);

    $response->assertUnprocessable()
        ->assertJsonValidationErrors(['quantity']);
});
```

## 3. Architecture Testing (`arch()`)

Use Pest's architecture testing engine to verify adherence to standards automatically in CI:

```php
arch('app codebase enforces strict types')
    ->expect('App')
    ->toUseStrictTypes();

arch('no debug statements remain in codebase')
    ->expect(['dd', 'dump', 'ray', 'var_dump', 'print_r'])
    ->not->toBeUsed();

arch('controllers remain thin routers')
    ->expect('App\Http\Controllers')
    ->toOnlyUse([
        'App\Actions',
        'App\Http\Requests',
        'App\Http\Resources',
        'Illuminate\Http',
        'Symfony\Component\HttpFoundation',
    ])
    ->not->toUse('Illuminate\Support\Facades\DB');

arch('actions have a single responsibility')
    ->expect('App\Actions')
    ->toHaveMethod('execute')
    ->classes->toBeFinal();

arch('models do not use guarded property')
    ->expect('App\Models')
    ->not->toHaveProperty('guarded');
```
