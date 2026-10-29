# Laravel Naming Conventions Reference

Follow PSR-12 and the standard conventions accepted by the Laravel ecosystem.

## 1. Naming Conventions Matrix

| Artifact | Convention | Good Example | Antipattern |
|---|---|---|---|
| **Model** | Singular, PascalCase | `User`, `OrderItem` | `Users`, `order_items` |
| **Table** | Plural, snake_case | `users`, `order_items` | `user`, `orderItems` |
| **Pivot Table** | Singular model names in alphabetical order, snake_case | `article_user`, `course_student` | `user_article`, `articles_users` |
| **Primary Key** | Lowercase | `id` | `user_id`, `custom_id` |
| **Foreign Key** | Singular model name with `_id` suffix | `user_id`, `order_item_id` | `userId`, `id_user`, `orders_id` |
| **hasOne / belongsTo** | Singular, camelCase | `user()`, `orderItem()` | `users()`, `order_item()` |
| **hasMany / belongsToMany** | Plural, camelCase | `comments()`, `roles()` | `comment()`, `user_roles()` |
| **Controller** | Singular, PascalCase, `Controller` suffix | `OrderController`, `InvoiceController` | `OrdersController`, `Invoice` |
| **Action** | Verb + Noun or Domain + Action, PascalCase, `Action` suffix | `CreateOrderAction`, `RefundInvoiceAction` | `OrderManager`, `ProcessOrder` |
| **FormRequest** | Action/Verb + Model + `Request` suffix | `StoreOrderRequest`, `UpdateProfileRequest` | `OrderFormRequest`, `UserRequest` |
| **API Resource** | Model + `Resource` suffix | `OrderResource`, `UserResource` | `OrderResponse`, `OrderView` |
| **DTO** | Descriptive, PascalCase, `Data` or `DTO` suffix | `CreateOrderData`, `PaymentPayload` | `OrderArray`, `Params` |
| **Event** | Past-tense action statement | `OrderCreatedEvent`, `UserRegisteredEvent` | `CreateOrder`, `SendEmail` |
| **Listener** | Action description | `SendOrderConfirmationEmail`, `LogOrderActivity` | `OrderListener` |
| **Job** | Verb + Noun | `ProcessPaymentJob`, `ExportCsvReport` | `PaymentQueue`, `JobOrder` |
| **Policy** | Model + `Policy` suffix | `OrderPolicy`, `PostPolicy` | `OrderAuth`, `AccessPolicy` |
| **Seeder** | Singular Model + `Seeder` suffix | `UserSeeder`, `ProductSeeder` | `UsersSeeder` |
| **Factory** | Singular Model + `Factory` suffix | `UserFactory`, `OrderFactory` | `UsersFactory` |
| **Enum** | Singular, PascalCase | `OrderStatus`, `PaymentType` | `OrderStatuses`, `OrderStatusEnum` |
| **Interface / Contract** | Adjective or descriptive noun, PascalCase | `PaymentGatewayInterface`, `Auditable` | `IPaymentGateway` |
| **Trait** | Adjective or capability description | `HasUuid`, `Filterable` | `UuidTrait` |
| **Migration** | Timestamp + action + table name, snake_case | `2026_01_01_000000_create_orders_table.php` | `2026_01_01_orders.php` |
| **Route Path** | Plural, kebab-case | `/api/v1/orders`, `/user-profiles` | `/order`, `/user_profiles` |
| **Route Name** | Resource plural + dot notation + action, snake_case | `orders.index`, `user_profiles.show` | `get_orders`, `orders-index` |
| **Blade View** | kebab-case | `order-summary.blade.php` | `orderSummary.blade.php` |
| **Config File** | snake_case | `payment_gateways.php` | `paymentGateways.php` |

## 2. Method Conventions

- **Resource Controllers:** Use standard REST methods: `index`, `create`, `store`, `show`, `edit`, `update`, `destroy`.
- **Actions:** Maintain a single public entry point: `execute()` or `__invoke()`.
- **Boolean checks:** Prefix with `is`, `has`, `can`, or `should`: `isCompleted()`, `hasDiscount()`.
- **Scopes in Models:** Use camelCase starting with the scope name without `scope` prefix when invoking (`published()`, `pendingReview()`).
