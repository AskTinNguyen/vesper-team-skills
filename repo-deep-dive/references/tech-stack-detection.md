# Tech Stack Detection Matrix

Detection rules for identifying frameworks, languages, and tools from repository files.

## Language Detection

| Language | Config Files | File Extensions | Key Indicators |
|----------|-------------|-----------------|----------------|
| JavaScript | `package.json` | `.js`, `.mjs`, `.cjs` | `node_modules/`, `npm`, `yarn` |
| TypeScript | `tsconfig.json` | `.ts`, `.tsx` | `@types/` in deps |
| Python | `pyproject.toml`, `setup.py`, `requirements.txt`, `Pipfile` | `.py` | `__init__.py`, `venv/` |
| Ruby | `Gemfile`, `*.gemspec` | `.rb`, `.erb` | `Rakefile`, `bundle` |
| Go | `go.mod`, `go.sum` | `.go` | `cmd/`, `internal/`, `pkg/` |
| Rust | `Cargo.toml`, `Cargo.lock` | `.rs` | `src/main.rs`, `src/lib.rs` |
| Java | `pom.xml`, `build.gradle`, `build.gradle.kts` | `.java` | `src/main/java/`, `src/test/java/` |
| Kotlin | `build.gradle.kts` | `.kt`, `.kts` | `src/main/kotlin/` |
| Swift | `Package.swift`, `*.xcodeproj` | `.swift` | `Sources/`, `Tests/` |
| C# | `*.csproj`, `*.sln` | `.cs` | `Program.cs`, `*.dll` |
| PHP | `composer.json` | `.php` | `vendor/`, `artisan` |
| Elixir | `mix.exs` | `.ex`, `.exs` | `lib/`, `test/` |
| Dart | `pubspec.yaml` | `.dart` | `lib/`, `flutter` |
| Zig | `build.zig` | `.zig` | `build.zig.zon` |

## Web Framework Detection

### JavaScript/TypeScript Frameworks

| Framework | Indicator Files | Dependency Names | Directory Patterns |
|-----------|----------------|------------------|--------------------|
| **React** | — | `react`, `react-dom` | `src/components/`, `.jsx`/`.tsx` files |
| **Next.js** | `next.config.*` | `next` | `app/`, `pages/`, `public/` |
| **Remix** | `remix.config.*` | `@remix-run/*` | `app/routes/` |
| **Astro** | `astro.config.*` | `astro` | `src/pages/`, `src/layouts/` |
| **Svelte/SvelteKit** | `svelte.config.*` | `svelte`, `@sveltejs/kit` | `src/routes/` |
| **Vue** | `vue.config.*` | `vue` | `src/views/`, `src/components/`, `.vue` files |
| **Nuxt** | `nuxt.config.*` | `nuxt` | `pages/`, `composables/` |
| **Angular** | `angular.json` | `@angular/core` | `src/app/`, `*.component.ts` |
| **Express** | — | `express` | `routes/`, `middleware/` |
| **Fastify** | — | `fastify` | `plugins/`, `routes/` |
| **NestJS** | `nest-cli.json` | `@nestjs/core` | `*.module.ts`, `*.controller.ts`, `*.service.ts` |
| **Hono** | — | `hono` | `src/routes/`, `src/middleware/` |

### Ruby Frameworks

| Framework | Indicator Files | Gem Names | Directory Patterns |
|-----------|----------------|-----------|-------------------|
| **Rails** | `config/routes.rb`, `bin/rails` | `rails` | `app/models/`, `app/controllers/`, `app/views/` |
| **Sinatra** | — | `sinatra` | Flat structure, `app.rb` |
| **Hanami** | `config/app.rb` | `hanami` | `slices/`, `app/actions/` |

### Python Frameworks

| Framework | Indicator Files | Package Names | Directory Patterns |
|-----------|----------------|---------------|-------------------|
| **Django** | `manage.py` | `django` | `*/models.py`, `*/views.py`, `*/urls.py` |
| **FastAPI** | — | `fastapi` | `app/routers/`, `app/models/` |
| **Flask** | — | `flask` | `app.py`, `blueprints/` |

### Go Frameworks

| Framework | Indicator Files | Import Paths | Directory Patterns |
|-----------|----------------|-------------|-------------------|
| **Gin** | — | `github.com/gin-gonic/gin` | `handlers/`, `routes/` |
| **Echo** | — | `github.com/labstack/echo` | `handler/`, `route/` |
| **Fiber** | — | `github.com/gofiber/fiber` | `handlers/`, `routes/` |
| **Chi** | — | `github.com/go-chi/chi` | `internal/`, `cmd/` |
| **Standard library** | — | `net/http` | `cmd/`, `internal/handler/` |

### Rust Frameworks

| Framework | Indicator Files | Crate Names | Directory Patterns |
|-----------|----------------|-------------|-------------------|
| **Actix-web** | — | `actix-web` | `src/handlers/`, `src/routes/` |
| **Axum** | — | `axum` | `src/routes/`, `src/handlers/` |
| **Rocket** | — | `rocket` | `src/routes/` |

## Database Detection

| Database | Indicator Files | Dependencies | Connection Strings |
|----------|----------------|-------------|-------------------|
| **PostgreSQL** | — | `pg`, `psycopg2`, `diesel` (postgres feature) | `postgres://`, `postgresql://` |
| **MySQL** | — | `mysql2`, `mysqlclient`, `diesel` (mysql feature) | `mysql://` |
| **SQLite** | `*.sqlite3`, `*.db` | `better-sqlite3`, `sqlite3` | `sqlite://`, `sqlite3` |
| **MongoDB** | — | `mongoose`, `mongodb`, `mongoid` | `mongodb://` |
| **Redis** | — | `redis`, `ioredis` | `redis://` |
| **Prisma** | `prisma/schema.prisma` | `prisma`, `@prisma/client` | in schema.prisma |
| **Drizzle** | `drizzle.config.*` | `drizzle-orm` | in config file |
| **TypeORM** | `ormconfig.*` | `typeorm` | in config file |
| **Sequelize** | `.sequelizerc` | `sequelize` | in config file |
| **ActiveRecord** | `db/schema.rb` | `activerecord` (via rails) | `config/database.yml` |

## Test Framework Detection

| Framework | Config Files | Dependencies | Test Patterns |
|-----------|-------------|-------------|---------------|
| **Jest** | `jest.config.*` | `jest`, `@jest/core` | `*.test.ts`, `*.spec.ts`, `__tests__/` |
| **Vitest** | `vitest.config.*` | `vitest` | `*.test.ts`, `*.spec.ts` |
| **Mocha** | `.mocharc.*` | `mocha` | `test/`, `*.test.js` |
| **pytest** | `pytest.ini`, `pyproject.toml [tool.pytest]` | `pytest` | `test_*.py`, `*_test.py` |
| **RSpec** | `.rspec` | `rspec` | `spec/**/*_spec.rb` |
| **Minitest** | — | `minitest` (via rails) | `test/**/*_test.rb` |
| **Go testing** | — | (standard library) | `*_test.go` |
| **Rust testing** | — | (standard library) | `#[test]`, `tests/` |
| **JUnit** | — | `junit` | `*Test.java`, `src/test/` |
| **Playwright** | `playwright.config.*` | `@playwright/test` | `*.spec.ts`, `e2e/` |
| **Cypress** | `cypress.config.*` | `cypress` | `cypress/e2e/` |

## Build Tool Detection

| Tool | Config Files | Purpose |
|------|-------------|---------|
| **webpack** | `webpack.config.*` | JS bundler |
| **Vite** | `vite.config.*` | JS dev server + bundler |
| **esbuild** | — (usually in scripts) | Fast JS bundler |
| **Turbopack** | (via next.config) | Next.js bundler |
| **Rollup** | `rollup.config.*` | JS library bundler |
| **Bun** | `bunfig.toml` | JS runtime + bundler |
| **Deno** | `deno.json`, `deno.lock` | JS/TS runtime |
| **Turborepo** | `turbo.json` | Monorepo build system |
| **Nx** | `nx.json` | Monorepo build system |
| **Lerna** | `lerna.json` | Monorepo package management |
| **pnpm** | `pnpm-workspace.yaml` | Package manager |
| **Bazel** | `BUILD`, `WORKSPACE` | Multi-language build |
| **CMake** | `CMakeLists.txt` | C/C++ build |
| **Gradle** | `build.gradle*`, `settings.gradle*` | JVM build |
| **Maven** | `pom.xml` | JVM build |
| **Mix** | `mix.exs` | Elixir build |
| **Cargo** | `Cargo.toml` | Rust build |

## Deployment Detection

| Platform | Indicator Files | Evidence |
|----------|----------------|---------|
| **Docker** | `Dockerfile`, `docker-compose.yml` | Container-based deploy |
| **Kubernetes** | `k8s/`, `*.yaml` with `apiVersion:` | K8s orchestration |
| **Heroku** | `Procfile`, `app.json` | PaaS deploy |
| **Vercel** | `vercel.json` | Serverless/edge deploy |
| **Netlify** | `netlify.toml` | JAMstack deploy |
| **AWS Lambda** | `serverless.yml`, `template.yaml` (SAM) | Serverless functions |
| **Fly.io** | `fly.toml` | Container deploy |
| **Railway** | `railway.json`, `nixpacks.toml` | PaaS deploy |
| **Render** | `render.yaml` | PaaS deploy |
| **Terraform** | `*.tf`, `terraform/` | Infrastructure as code |
| **Pulumi** | `Pulumi.yaml` | Infrastructure as code |
| **Kamal** | `config/deploy.yml` | Docker deploy for Rails |
