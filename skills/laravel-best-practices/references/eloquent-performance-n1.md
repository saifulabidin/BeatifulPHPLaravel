# Eloquent Performance and N+1 Elimination Reference

## 1. What is the N+1 Query Problem?

The N+1 query problem occurs when an initial query fetches N records (1 query), and subsequent code fetches related records for each item inside a loop (N additional queries), leading to N+1 database queries.

```php
// Antipattern: 1 + 50 queries for 50 posts
$posts = Post::latest()->take(50)->get();
foreach ($posts as $post) {
    echo $post->author->name; // Separate SELECT query per post
}

// Optimized: Exactly 2 queries
$posts = Post::with('author')->latest()->take(50)->get();
foreach ($posts as $post) {
    echo $post->author->name; // Read from in-memory relation
}
```

## 2. Global Lazy Loading Prevention

Enforce prevention of lazy loading during development and testing by placing this configuration in `app/Providers/AppServiceProvider.php`:

```php
use Illuminate\Database\Eloquent\Model;

public function boot(): void
{
    Model::preventLazyLoading(! $this->app->isProduction());
    Model::preventSilentlyDiscardingAttributes(! $this->app->isProduction());
    Model::preventAccessingMissingAttributes(! $this->app->isProduction());
}
```

When lazy loading is triggered, Eloquent will throw a `LazyLoadingViolationException`, surfacing the defect immediately during testing.

## 3. Advanced Eager Loading Techniques

### Specific Column Selection
Select only the columns needed, always including primary and foreign keys:

```php
$orders = Order::with('customer:id,name,email')->get();
```

### Nested Eager Loading
Load deeper relations efficiently:

```php
$posts = Post::with(['author', 'comments.author'])->get();
```

### Constrained Eager Loading
Filter related models before loading:

```php
$users = User::with(['orders' => function ($query) {
    $query->where('status', OrderStatus::Paid)->latest();
}])->get();
```

### Aggregates Without Loading Models
Count or sum relations without hydrating models:

```php
// Loads post with an author_count attribute in a single query
$posts = Post::withCount('comments')->withAvg('reviews', 'rating')->get();
```

## 4. Hidden N+1 Traps

### Accessor Traps
Accessors on Eloquent models that touch relationships trigger N+1 when serialized:

```php
// Danger: serialization triggers relation on each model
public function getAuthorNameAttribute(): string
{
    return $this->author->name;
}
```
Fix: Eager load the relation whenever serializing, or avoid calling relationships within accessors.

### API Resources
Always guard relationship access with `whenLoaded()` in JsonResource classes:

```php
public function toArray(Request $request): array
{
    return [
        'id' => $this->id,
        'title' => $this->title,
        'author' => new AuthorResource($this->whenLoaded('author')),
    ];
}
```

### Blade Template Queries
Never execute queries directly inside Blade templates (`@foreach ($user->orders()->where(...)->get() as $order)`). Prepare and eager load all data in the Action or Controller before passing it to the view.

## 5. Large Dataset Processing

Never load unbounded collections into memory with `all()`.

| Method | Use Case | Memory Impact | Safe on Updates? |
|---|---|---|---|
| `chunk(100, $callback)` | Read-only processing by offset | Low | No (offset shifts if updating) |
| `chunkById(100, $callback)` | Processing and updating records | Low | Yes (uses `id > last_id`) |
| `lazyById(100)` | Lazy collections with generators | Constant | Yes |
| `cursor()` | Raw single-record streaming | Minimal | Read-only |

## 6. High-Throughput Query Optimizations

### Subquery Selects for Single Related Values
Avoid eager-loading entire relationship collections when only needing a single value (e.g., the last order date):

```php
// Fetches the latest order date via subquery in the primary SELECT
$users = User::addSelect([
    'last_order_date' => Order::select('created_at')
        ->whereColumn('user_id', 'users.id')
        ->latest()
        ->take(1),
])->get();
```

### whereIn + pluck() Over whereHas() on Large Tables
`whereHas()` compiles to a `WHERE EXISTS (SELECT 1 ...)` correlated subquery, which can bypass indexes on large tables:

```php
// Slower on very large datasets:
$posts = Post::whereHas('tags', fn ($q) => $q->where('name', 'laravel'))->get();

// Significantly faster when indexed:
$tagIds = Tag::where('name', 'laravel')->pluck('id');
$postIds = DB::table('post_tag')->whereIn('tag_id', $tagIds)->pluck('post_id');
$posts = Post::whereIn('id', $postIds)->get();
```

### Conditional Aggregates
Avoid multiple counting queries by using conditional `CASE WHEN` statements in a single query:

```php
$stats = Order::query()
    ->selectRaw('count(*) as total')
    ->selectRaw('count(CASE WHEN status = ? THEN 1 END) as paid_count', [OrderStatus::Paid->value])
    ->selectRaw('count(CASE WHEN status = ? THEN 1 END) as pending_count', [OrderStatus::Pending->value])
    ->first();
```
