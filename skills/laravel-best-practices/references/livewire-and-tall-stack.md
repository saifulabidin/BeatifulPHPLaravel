# Livewire and TALL-Stack Engineering Reference

This reference defines best practices for full-stack Laravel applications powered by the TALL stack (Tailwind CSS, Alpine.js, Laravel, and Livewire 3/4).

## 1. Livewire Architecture & Separation of Concerns

Livewire components are frontend controllers. They handle user interaction, dispatch events, and render views, but they must not become monolithic repositories of business logic.

```text
Blade / Alpine Interaction
    └── Livewire Component (Handles user actions & UI state)
         └── Form Object    (Component-specific validation & state)
              └── Action    (Domain logic, transactions, repository persistence)
```

- **Delegate domain operations to Actions:** Do not place multi-step database mutations, external HTTP calls, or complex business logic directly in Livewire component methods. Call dedicated Action classes:
  ```php
  final class CheckoutComponent extends Component
  {
      public CheckoutForm $form;

      public function process(ProcessCheckoutAction $action): void
      {
          $this->authorize('checkout', Order::class);
          $this->form->validate();

          $order = $action->execute(auth()->user(), $this->form->toData());

          $this->redirectRoute('orders.show', ['order' => $order]);
      }
  }
  ```
- **Never execute heavy queries in `render()`:** The `render()` method runs on every network roundtrip, property update, and DOM diff. Eager load and cache queries via computed properties.

## 2. Security & State Hardening

Client browsers inspect and manipulate public Livewire component properties. Enforce strict boundaries:

- **Lock immutable properties:** Use the `#[Locked]` attribute on properties that should never be modified by the client (such as primary IDs, tenant IDs, or status codes):
  ```php
  use Livewire\Attributes\Locked;

  final class EditInvoiceComponent extends Component
  {
      #[Locked]
      public int $invoiceId;

      #[Locked]
      public int $tenantId;
  }
  ```
- **Authorize every action method:** Livewire action methods can be triggered directly via network requests. Always run authorization inside the method, not only in `mount()`:
  ```php
  public function deleteItem(int $itemId, DeleteItemAction $action): void
  {
      $item = Item::findOrFail($itemId);
      $this->authorize('delete', $item);

      $action->execute($item);
  }
  ```
- **Never expose sensitive Eloquent models in public properties:** Public model properties serialize all attributes (including hidden ones) to the browser payload. Use typed Form Objects or primitive DTOs instead.
- **Use Form Objects for complex forms:** Group validation rules and form state into dedicated `Livewire\Form` classes:
  ```php
  use Livewire\Form;
  use Livewire\Attributes\Validate;

  final class UpdateProfileForm extends Form
  {
      #[Validate('required|string|min:3|max:255')]
      public string $name = '';

      #[Validate('required|email|max:255')]
      public string $email = '';
  }
  ```

## 3. High-Performance Livewire Patterns

- **Computed properties for caching:** Wrap data queries in `#[Computed]` properties so they are evaluated once per request lifecycle:
  ```php
  use Livewire\Attributes\Computed;

  #[Computed(persist: true, seconds: 300)]
  public function activeProjects(): Collection
  {
      return Project::where('status', ProjectStatus::Active)
          ->with('leadDeveloper')
          ->get();
  }
  ```
  In Blade: access via `$this->activeProjects` (not as a method call).
- **Deferred loading with `#[Lazy]`:** Defer loading slow dashboard panels or charts until initial page shell has loaded:
  ```php
  use Livewire\Attributes\Lazy;

  #[Lazy]
  final class RevenueChartComponent extends Component
  {
      public function placeholder(): string
      {
          return <<<'HTML'
          <div class="animate-pulse bg-gray-200 h-64 rounded-xl"></div>
          HTML;
      }
  }
  ```
- **Pagination trait:** Always use `WithPagination` for list rendering to avoid memory exhaustion:
  ```php
  use Livewire\WithPagination;

  final class UserListComponent extends Component
  {
      use WithPagination;

      #[Computed]
      public function users(): LengthAwarePaginator
      {
          return User::latest()->paginate(15);
      }
  }
  ```

## 4. Blade & Alpine.js Clean Patterns

- **Zero database queries in Blade views:** Never invoke Eloquent relationships or queries inside templates (e.g. `@foreach ($user->orders()->where(...) as $order)`). Prepare and eager load all relationships in the component or controller.
- **No inline JavaScript or CSS:** Keep styling strictly in Tailwind utility classes and interactive state in Alpine.js (`x-data`, `x-show`, `x-on:click`). Never write `<script>` tags or `<style>` blocks inside Blade views.
- **Isolate third-party DOM widgets with `wire:ignore`:** When wrapping external JavaScript libraries (e.g., date pickers, charting libraries, rich text editors), wrap them in `wire:ignore` so Livewire's morphdom diffing does not tear down external DOM trees.
- **Componentize reusable UI:** Build atomic Blade components (`resources/views/components/`) with explicit props:
  ```blade
  {{-- resources/views/components/badge.blade.php --}}
  @props([
      'variant' => 'info',
  ])

  @php
  $classes = match($variant) {
      'success' => 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
      'danger' => 'bg-rose-50 text-rose-700 ring-rose-600/10',
      default => 'bg-gray-50 text-gray-600 ring-gray-500/10',
  };
  @endphp

  <span {{ $attributes->merge(['class' => "inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ring-1 ring-inset {$classes}"]) }}>
      {{ $slot }}
  </span>
  ```
- **Use expressive Blade directives:** Prefer `@forelse` over `@if` + `@foreach`, and use `@can` / `@cannot` for permission checks.
