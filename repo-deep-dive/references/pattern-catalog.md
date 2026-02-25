# Pattern Catalog

Comprehensive catalog of design patterns to search for during repo analysis. Organized by category with detection heuristics.

## Creational Patterns

### Factory / Factory Method
**What to search for:** Classes/functions that create and return instances without exposing creation logic.
**Detection heuristics:**
- Functions named `create*`, `make*`, `build*`, `new*`
- Switch/match statements that return different types based on input
- Classes with static creation methods
**Grep patterns:** `create[A-Z]`, `make[A-Z]`, `build[A-Z]`, `factory`, `Factory`

### Abstract Factory
**What to search for:** Factory that produces families of related objects.
**Detection heuristics:**
- Interface/abstract class with multiple `create*` methods
- Concrete factory implementations for different configurations
**Grep patterns:** `AbstractFactory`, `FactoryProvider`, `createFactory`

### Builder
**What to search for:** Step-by-step object construction with fluent API.
**Detection heuristics:**
- Method chaining that returns `this` / `self`
- Classes named `*Builder`
- `.build()` method calls
**Grep patterns:** `Builder`, `.build()`, `\.set[A-Z].*return (this|self)`

### Singleton
**What to search for:** Single instance enforcement.
**Detection heuristics:**
- `getInstance()` static methods
- Module-level instances
- `@@instance` / `_instance` class variables
**Grep patterns:** `getInstance`, `_instance`, `singleton`, `Singleton`

### Dependency Injection / IoC
**What to search for:** Dependencies passed in rather than created internally.
**Detection heuristics:**
- Constructor parameters that are interfaces/abstract types
- DI container configuration files
- `@Inject`, `@Injectable` decorators
- `bind`, `register`, `provide` in container setup
**Grep patterns:** `@Inject`, `@Injectable`, `container.register`, `bind(`, `provide(`

## Structural Patterns

### Adapter / Wrapper
**What to search for:** Classes that convert one interface to another.
**Detection heuristics:**
- Classes named `*Adapter`, `*Wrapper`
- Methods that delegate to an internal object with different signatures
**Grep patterns:** `Adapter`, `Wrapper`, `adapt`, `wrap`

### Decorator
**What to search for:** Wrapping objects to add behavior without modifying the original.
**Detection heuristics:**
- Python `@decorator` syntax
- TypeScript/Java decorators (`@Log`, `@Cache`, `@Auth`)
- Ruby modules included/prepended to classes
- Functions that take a function and return a function
**Grep patterns:** `@[A-Z]`, `decorator`, `decorate`, `def .*wrapper`

### Facade
**What to search for:** Simplified interface to a complex subsystem.
**Detection heuristics:**
- Classes that aggregate and simplify multiple service calls
- API clients that wrap REST calls
- "Manager" or "Service" classes that orchestrate multiple components
**Grep patterns:** `Facade`, `Manager`, `Service`, `Client`

### Proxy
**What to search for:** Stand-in objects that control access to another object.
**Detection heuristics:**
- Caching proxies (check cache before delegating)
- Lazy loading (create real object only when needed)
- Logging proxies (log before/after delegating)
**Grep patterns:** `Proxy`, `proxy`, `delegate`, `lazy`

### Plugin / Extension System
**What to search for:** Dynamic loading and registration of functionality.
**Detection heuristics:**
- Plugin registration (`register`, `use`, `addPlugin`)
- Dynamic imports based on configuration
- Hook systems (`beforeX`, `afterX`, `onX`)
**Grep patterns:** `plugin`, `Plugin`, `register`, `\.use\(`, `hook`, `Hook`

### Middleware
**What to search for:** Pipeline of processing functions that wrap a core handler.
**Detection heuristics:**
- `app.use(...)` patterns
- `next()` function calls in handler chains
- Ordered arrays of processing functions
**Grep patterns:** `middleware`, `\.use\(`, `next\(\)`, `Middleware`

## Behavioral Patterns

### Observer / Event Emitter
**What to search for:** Publish-subscribe notification systems.
**Detection heuristics:**
- `on`, `emit`, `subscribe`, `publish` methods
- Event bus / event emitter instances
- Callback registration
- `addEventListener`, `removeEventListener`
**Grep patterns:** `\.on\(`, `\.emit\(`, `subscribe`, `publish`, `EventEmitter`, `EventBus`

### Strategy
**What to search for:** Interchangeable algorithms selected at runtime.
**Detection heuristics:**
- Interface/type with multiple implementations
- Strategy objects passed to constructors/functions
- Configuration-driven algorithm selection
**Grep patterns:** `Strategy`, `strategy`, `policy`, `Policy`

### Command
**What to search for:** Encapsulated actions as objects.
**Detection heuristics:**
- Classes with `execute()` / `run()` / `perform()` methods
- Command queues
- Undo/redo support
**Grep patterns:** `Command`, `execute`, `\.run\(`, `\.perform\(`, `undo`, `redo`

### State Machine
**What to search for:** Explicit state transitions.
**Detection heuristics:**
- State enums/constants with transition maps
- `transition`, `setState`, `currentState` patterns
- Libraries like `xstate`, `aasm`, `statesman`
**Grep patterns:** `state`, `State`, `transition`, `StateMachine`, `status`

### Chain of Responsibility
**What to search for:** Sequential processing where each handler decides to handle or pass.
**Detection heuristics:**
- `handle` or `process` methods with `next` delegation
- Ordered handler lists
- Middleware-like patterns in non-HTTP contexts
**Grep patterns:** `handler`, `Handler`, `handle`, `chain`, `Chain`

### Iterator / Generator
**What to search for:** Custom iteration over collections.
**Detection heuristics:**
- `yield` keyword usage
- Custom iterator implementations (`__iter__`, `Symbol.iterator`)
- Pagination implementations
**Grep patterns:** `yield`, `iterator`, `Iterator`, `paginate`, `cursor`

## Architectural Patterns

### Repository
**What to search for:** Data access abstraction layer.
**Detection heuristics:**
- Classes named `*Repository` with CRUD methods
- Separation between domain objects and data access
- Query building abstracted behind method calls
**Grep patterns:** `Repository`, `repository`, `findBy`, `findAll`, `findOne`

### Unit of Work
**What to search for:** Transaction management across multiple operations.
**Detection heuristics:**
- `commit`, `rollback`, `saveChanges` methods
- Transaction wrappers around multiple operations
**Grep patterns:** `UnitOfWork`, `transaction`, `commit`, `rollback`, `saveChanges`

### CQRS (Command Query Responsibility Segregation)
**What to search for:** Separate read and write models/paths.
**Detection heuristics:**
- Separate `Command` and `Query` classes
- Different models for reading and writing
- Event sourcing combined with read projections
**Grep patterns:** `Command`, `Query`, `ReadModel`, `WriteModel`, `Projection`

### Event Sourcing
**What to search for:** State stored as sequence of events rather than current state.
**Detection heuristics:**
- Event stores, event streams
- `apply`, `replay` methods
- Event classes named `*Created`, `*Updated`, `*Deleted`
**Grep patterns:** `EventStore`, `eventStream`, `apply`, `replay`, `Created$`, `Updated$`

### Circuit Breaker
**What to search for:** Failure isolation for external calls.
**Detection heuristics:**
- Retry logic with failure counting
- State tracking (closed, open, half-open)
- Timeout handling with fallback behavior
**Grep patterns:** `CircuitBreaker`, `circuitBreaker`, `halfOpen`, `fallback`, `retry`

### Saga / Process Manager
**What to search for:** Long-running multi-step processes with compensation.
**Detection heuristics:**
- Step-by-step workflows with rollback logic
- Compensation actions for each step
- Process state tracking across services
**Grep patterns:** `Saga`, `saga`, `compensate`, `ProcessManager`, `workflow`, `step`

## Framework-Specific Patterns

### Ruby/Rails
- **Concerns:** `extend ActiveSupport::Concern`, `included do` blocks
- **STI:** `type` column, inheritance from `ApplicationRecord` subclass
- **Polymorphic associations:** `belongs_to :imageable, polymorphic: true`
- **Service objects:** Classes in `app/services/` with `call` method
- **Form objects:** Classes in `app/forms/` wrapping complex validations
- **Decorators/Presenters:** `app/decorators/`, `app/presenters/`
- **Jobs:** `ApplicationJob` subclasses, `perform` method

### JavaScript/TypeScript
- **Module pattern:** IIFE, closure-based encapsulation
- **HOC (Higher-Order Component):** `with*` functions wrapping React components
- **Hooks:** `use*` custom hooks in React
- **Render Props:** Components that take render functions
- **Composables:** Vue 3 `use*` composition functions
- **Barrel files:** `index.ts` re-exporting from directory

### Python
- **Decorators:** `@` syntax for function/class wrapping
- **Context managers:** `__enter__`/`__exit__`, `@contextmanager`
- **Metaclasses:** `class Meta:`, `__metaclass__`, custom `type` subclasses
- **Descriptors:** `__get__`/`__set__`/`__delete__`
- **Mixins:** Multiple inheritance for behavior sharing
- **Dataclasses:** `@dataclass` for data containers

### Go
- **Functional options:** `func WithTimeout(t time.Duration) Option`
- **Interface satisfaction:** Implicit interface implementation
- **Table-driven tests:** Test cases defined as struct slices
- **Goroutine patterns:** Worker pools, fan-in/fan-out, pipelines
- **Error wrapping:** `fmt.Errorf("...: %w", err)`

### Rust
- **Builder pattern:** `FooBuilder` with method chaining
- **Type state pattern:** Generic types that encode state at compile time
- **Newtype pattern:** `struct Meters(f64)` for type safety
- **Error handling:** `Result<T, E>` with custom error enums, `thiserror`, `anyhow`
- **Trait objects:** `Box<dyn Trait>` for runtime polymorphism
