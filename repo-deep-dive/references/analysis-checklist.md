# Analysis Checklist

Priority file reading order and analysis dimensions for repo deep dives.

## Priority File Reading Order

Read files in this order to build understanding progressively. Stop at each tier and synthesize before continuing.

### Tier 1: Identity (Read First — Always)

These files answer "What is this project?"

| Priority | File | What to Extract |
|----------|------|-----------------|
| 1 | `README.md` / `README.rst` / `README` | Purpose, features, architecture overview, getting started |
| 2 | `LICENSE` / `LICENSE.md` | License type (affects redistribution) |
| 3 | `package.json` / `Gemfile` / `Cargo.toml` / `go.mod` / `pyproject.toml` / `pom.xml` / `build.gradle` | Dependencies, scripts, version, name |
| 4 | `.github/workflows/*.yml` / `.circleci/config.yml` / `Jenkinsfile` | CI pipeline, test commands, deploy steps |
| 5 | `docker-compose.yml` / `Dockerfile` | Services, infrastructure dependencies |

### Tier 2: Configuration (Read Second)

These files answer "How is this project configured?"

| Priority | File | What to Extract |
|----------|------|-----------------|
| 6 | `tsconfig.json` / `jsconfig.json` | Module resolution, path aliases, target |
| 7 | `.eslintrc*` / `.prettierrc*` / `rubocop.yml` / `rustfmt.toml` | Code style rules (authoritative source) |
| 8 | `Makefile` / `Rakefile` / `Taskfile.yml` / `justfile` | Build/dev/test commands |
| 9 | `.env.example` / `.env.sample` | Environment variables (reveals integrations) |
| 10 | `config/` directory listing | Configuration structure |

### Tier 3: Entry Points (Read Third)

These files answer "How does execution flow?"

| Priority | File | What to Extract |
|----------|------|-----------------|
| 11 | Main entry: `src/index.ts`, `main.go`, `app.rb`, `manage.py`, `src/main.rs` | Bootstrap, initialization, dependency wiring |
| 12 | Router/routes: `routes.rb`, `src/routes/`, `urls.py`, `router.go` | Full API surface |
| 13 | App config: `config/application.rb`, `app.module.ts`, `settings.py` | Framework configuration |
| 14 | Database schema: `schema.rb`, `prisma/schema.prisma`, `migrations/`, `*.sql` | Data model |
| 15 | Middleware: `middleware/`, `app/middleware/` | Cross-cutting concerns |

### Tier 4: Domain Code (Read Selectively)

Read based on what Tiers 1-3 reveal. Focus on the most important modules.

| Priority | File | What to Extract |
|----------|------|-----------------|
| 16 | Core models / entities / types | Domain model, business rules |
| 17 | Core services / controllers | Business logic implementation |
| 18 | Shared utilities / helpers | Common patterns, reusable code |
| 19 | Error classes / error handling | Error strategy |
| 20 | Base classes / abstract types | Extension patterns |

### Tier 5: Testing (Read for Pattern Extraction)

| Priority | File | What to Extract |
|----------|------|-----------------|
| 21 | Test config: `jest.config.*`, `pytest.ini`, `test_helper.rb` | Test framework setup |
| 22 | Test fixtures / factories | Data setup patterns |
| 23 | 2-3 representative test files | Test style and conventions |
| 24 | Integration / E2E test examples | Testing strategy for complex flows |

### Tier 6: Documentation (Read if Available)

| Priority | File | What to Extract |
|----------|------|-----------------|
| 25 | `CONTRIBUTING.md` | Development workflow, commit conventions |
| 26 | `ARCHITECTURE.md` / `docs/architecture.md` | Official architecture documentation |
| 27 | `CHANGELOG.md` | Evolution history, breaking changes |
| 28 | `docs/` directory listing | Available documentation |
| 29 | API docs: `openapi.yaml`, `swagger.json` | Formal API specification |

## Analysis Dimensions

For each dimension, document findings with file:line evidence.

### 1. Architecture

- System type (monolith, microservices, serverless, library)
- Layer architecture (MVC, hexagonal, clean, etc.)
- Component boundaries and ownership
- Dependency direction (which layers depend on which)
- Data flow (request → response path)

### 2. Design Patterns

- Creational patterns (how objects are created)
- Structural patterns (how components are composed)
- Behavioral patterns (how components interact)
- Framework-specific patterns
- Custom/domain-specific patterns

### 3. Conventions

- Naming (files, functions, variables, classes)
- File organization (grouping strategy)
- Import ordering and style
- Error handling approach
- Documentation practices
- Git workflow (branch naming, commit messages)

### 4. Features

- User-facing capabilities
- Implementation patterns per feature
- Extension points
- Feature flags / configuration-driven behavior

### 5. Quality

- Test coverage approach
- CI/CD pipeline
- Code review practices (from PR templates, CODEOWNERS)
- Static analysis tools
- Performance monitoring

### 6. Operations

- Deployment strategy
- Environment management
- Logging and monitoring
- Database migration approach
- Secret management
