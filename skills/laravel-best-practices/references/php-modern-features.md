# Modern PHP (8.3 - 8.5) Standards Reference

## 1. Strict Typing and Declarations

Every file must start with strict types:

```php
<?php

declare(strict_types=1);
```

Declare parameter types, return types, and class property types explicitly:

```php
public function calculateTotal(int $quantity, float $unitPrice): float
{
    return $quantity * $unitPrice;
}
```

## 2. Readonly Classes and Asymmetric Visibility

Declare DTOs and value objects as immutable:

```php
// PHP 8.2+: Readonly class
readonly class AddressValue
{
    public function __construct(
        public string $street,
        public string $city,
        public string $postalCode,
        public string $country = 'ID',
    ) {}
}

// PHP 8.4+: Asymmetric property visibility
class UserProfile
{
    public private(set) string $status;

    public function __construct(string $status)
    {
        $this->status = $status;
    }
}
```

## 3. Backed Enums

Replace magic string literals and integer codes with backed Enums:

```php
enum PaymentMethod: string
{
    case CreditCard = 'credit_card';
    case BankTransfer = 'bank_transfer';
    case EWallet = 'e_wallet';

    public function feeInCents(): int
    {
        return match ($this) {
            self::CreditCard => 250,
            self::BankTransfer => 0,
            self::EWallet => 150,
        };
    }
}
```

## 4. Match Expressions

Use `match` instead of verbose `switch` statements:

```php
$discountMultiplier = match ($membershipTier) {
    MembershipTier::Gold => 0.80,
    MembershipTier::Silver => 0.90,
    MembershipTier::Bronze => 0.95,
    MembershipTier::None => 1.0,
};
```

`match` performs strict identity checks (`===`) and returns a value directly.

## 5. PHP 8.3 Features

### Typed Class Constants
Explicitly declare constant types to prevent subclass drift:

```php
class OrderConfiguration
{
    public const int MAX_LINE_ITEMS = 50;
    public const string INVOICE_PREFIX = 'INV-';
}
```

### Native json_validate()
Validate JSON syntax without allocating memory for parsed structures:

```php
if (! json_validate($rawPayload)) {
    throw new InvalidPayloadException('Malformed JSON received.');
}

$data = json_decode($rawPayload, associative: true);
```

### The #[Override] Attribute
Enforce contract compliance at compile time when overriding parent methods:

```php
class CustomUserProvider extends BaseUserProvider
{
    #[Override]
    public function retrieveById(mixed $identifier): ?Authenticatable
    {
        return $this->findUserCached($identifier);
    }
}
```

## 6. PHP 8.4 - 8.5 Additions

- **Property Hooks:** Replace boilerplate getter/setter methods:
  ```php
  class Customer
  {
      public string $first;
      public string $last;

      public string $fullName {
          get => "{$this->first} {$this->last}";
      }
  }
  ```
- **Array inspection functions:** Use native `array_find()`, `array_find_key()`, `array_any()`, and `array_all()` instead of manual loops.

## 7. Caution: Named Arguments and Semantic Versioning

Laravel's backwards compatibility guidelines explicitly exclude parameter names:
- Parameter names in Laravel framework methods can and do change between releases.
- Calling Laravel methods with named arguments (e.g. `Route::get(uri: '/home', action: ...)` or `$request->validate(rules: ...)`) creates brittle code that breaks during minor or patch upgrades.
- **Rule:** Use positional arguments when calling framework and vendor methods. Restrict named arguments strictly to your own application code (DTOs, Actions, Value Objects).
